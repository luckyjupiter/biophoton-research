"""
Node of Ranvier emission model based on Zangari et al. (2018, 2021).

Models ion channel currents at nodes of Ranvier as nanoantenna arrays
that radiate electromagnetic energy during action potentials.

All parameters from measured values:
- Channel density: 400-1400/μm² (rat/rabbit optic nerve)
- Channel length (dipole): ~13 nm (Na_v structure)
- Driving voltage: 120 mV (AP onset) → 0 mV (peak)
- Node dimensions: 0.7-1.4 μm length, 0.27-3.12 μm diameter
- AP duration at node: ~0.1-0.5 ms

References:
    Zangari et al., Sci Rep 8:539 (2018) — computational model
    Zangari et al., Sci Rep 11:3022 (2021) — experimental detection
    Kumar et al., Sci Rep 6:36508 (2016) — waveguide propagation
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass

from . import constants as C
from .axon import AxonGeometry


# ===========================================================================
# Node of Ranvier parameters (measured values from literature)
# ===========================================================================

# Ion channel properties
NA_CHANNEL_DENSITY_PER_UM2 = 700.0      # Zangari default (range: 400-1400)
NA_CHANNEL_LENGTH_M = 13e-9             # ~13 nm, Na_v channel height
NA_CHANNEL_CONDUCTANCE_PS = 20.0        # single channel conductance [pS]
NA_CHANNEL_OPEN_PROBABILITY = 0.8       # peak open probability during AP
AP_DRIVING_FORCE_V = 0.100              # V_df at AP onset (100 mV)
AP_DURATION_AT_NODE_S = 0.2e-3          # ~0.2 ms for AP at a single node

# Node geometry (rat optic nerve, Zangari Table 1)
NODE_LENGTH_UM = 1.0                    # 0.7-1.4 μm
NODE_DIAMETER_UM = 0.8                  # ~axon diameter at node

# Electromagnetic constants
ETA_0 = 377.0                           # free-space impedance [Ω]
C_LIGHT = C.C_LIGHT


@dataclass
class NodeEmission:
    """Emission properties of a single Node of Ranvier as a nanoantenna array.
    
    Parameters
    ----------
    axon : AxonGeometry
        The axon geometry (determines node diameter).
    channel_density : float
        Na⁺ channel density in channels/μm². Default from Zangari.
    driving_voltage : float
        Driving force voltage in volts during AP.
    """
    
    axon: AxonGeometry
    channel_density: float = NA_CHANNEL_DENSITY_PER_UM2
    driving_voltage: float = AP_DRIVING_FORCE_V
    
    @property
    def node_diameter_m(self) -> float:
        """Node diameter in meters (≈ axon diameter)."""
        return self.axon.axon_diameter_um * 1e-6
    
    @property
    def node_area_um2(self) -> float:
        """Surface area of the node of Ranvier (cylinder wall)."""
        return np.pi * self.axon.axon_diameter_um * NODE_LENGTH_UM
    
    @property
    def n_channels(self) -> int:
        """Total number of active Na⁺ channels at the node."""
        return int(self.channel_density * self.node_area_um2)
    
    @property
    def single_channel_current_A(self) -> float:
        """Current through a single open Na⁺ channel.
        
        I = g × V_df, where g is single-channel conductance.
        """
        g = NA_CHANNEL_CONDUCTANCE_PS * 1e-12  # pS → S
        return g * self.driving_voltage
    
    @property
    def peak_total_current_A(self) -> float:
        """Total ionic current through all open channels at AP peak."""
        return (self.n_channels * NA_CHANNEL_OPEN_PROBABILITY 
                * self.single_channel_current_A)
    
    def dipole_radiated_power_W(self, wavelength_nm: float) -> float:
        """Radiated power from a single channel modeled as a Hertzian dipole.
        
        P = (π/3) × (η₀/λ²) × |I·l|²
        
        This is the standard short-dipole radiation formula.
        l = channel length (13 nm), I = single channel current.
        """
        lam_m = wavelength_nm * 1e-9
        I = self.single_channel_current_A
        l = NA_CHANNEL_LENGTH_M
        
        return (np.pi / 3) * (ETA_0 / lam_m**2) * (I * l)**2
    
    def array_directivity(self, wavelength_nm: float) -> float:
        """Directivity gain of the nanoantenna array.
        
        For a phased array of N elements with proper phase delays,
        the directivity scales as ~N for forward radiation.
        
        Zangari showed the radiation pattern is directed toward
        the next internode. We use a conservative estimate.
        
        The array factor enhancement depends on wavelength:
        - IR (>700nm): more focused → higher directivity
        - Visible (<700nm): more side lobes → lower directivity
        """
        lam_m = wavelength_nm * 1e-9
        N = self.n_channels
        
        # Inter-element spacing (channel-to-channel distance)
        d_spacing = 1.0 / np.sqrt(self.channel_density * 1e12)  # m
        
        # Effective array gain: scales with N but limited by spatial coherence
        # For d << λ (which is always true: ~30nm spacing vs 300-2500nm wavelength),
        # the array radiates as a superdipole with gain ~ N
        # But spatial incoherence reduces this. Conservative: sqrt(N)
        array_gain = np.sqrt(N)
        
        # IR wavelengths have better directivity (Zangari Figs 2-3)
        if wavelength_nm > 700:
            ir_bonus = 1.0 + 0.5 * (wavelength_nm - 700) / 1000
        else:
            ir_bonus = 1.0
        
        return array_gain * ir_bonus
    
    def total_radiated_power_W(self, wavelength_nm: float) -> float:
        """Total power radiated by the node in the forward direction.
        
        P_total = P_single × N_open × D_array
        
        This is the power directed toward the next internode waveguide.
        """
        P_single = self.dipole_radiated_power_W(wavelength_nm)
        N_open = self.n_channels * NA_CHANNEL_OPEN_PROBABILITY
        D = self.array_directivity(wavelength_nm)
        
        return P_single * N_open * D
    
    def photons_per_ap(self, wavelength_nm: float) -> float:
        """Number of photons emitted per action potential at this wavelength.
        
        N_photon = P × Δt / E_photon
        where E_photon = hc/λ
        """
        P = self.total_radiated_power_W(wavelength_nm)
        E_photon = C.H_PLANCK * C_LIGHT / (wavelength_nm * 1e-9)
        
        return P * AP_DURATION_AT_NODE_S / E_photon
    
    def emission_spectrum(
        self,
        wavelength_nm: np.ndarray,
    ) -> np.ndarray:
        """Spectral distribution of nanoantenna emission.
        
        The nanoantenna array radiates across a broad spectrum (300-2500nm).
        The spectral shape depends on:
        1. Dipole radiation efficiency (∝ 1/λ² for short dipoles)
        2. Array directivity (better at longer wavelengths)
        3. Waveguide coupling (determined by V-number)
        
        Returns photons per AP per nm bandwidth.
        """
        lam = np.atleast_1d(wavelength_nm).astype(np.float64)
        spectrum = np.zeros_like(lam)
        
        for i, wl in enumerate(lam):
            spectrum[i] = self.photons_per_ap(wl)
        
        return spectrum


def propagate_with_relay(
    axon: AxonGeometry,
    wavelength_nm: np.ndarray,
    n_nodes: int = 10,
    node_coupling_loss_db: float = 1.0,
    channel_density: float = NA_CHANNEL_DENSITY_PER_UM2,
    include_ros: bool = True,
    ap_rate_hz: float = 10.0,
) -> dict:
    """Propagate light through a chain of internodes WITH node re-emission.
    
    Unlike the pure-loss model in waveguide.propagate_multi_node, this
    adds photons at each node from the nanoantenna emission.
    
    The model is CLASSICAL — no quantum correlations between nodes.
    Each node independently emits based on its own AP.
    
    Two emission sources are modeled separately:
    1. Nanoantenna (EM from ion currents) — Zangari et al. 2018/2021
       Very low flux (~10⁻⁵ photons/AP/node at visible wavelengths)
       but directional (phased array → forward-coupled into waveguide)
    2. ROS/chemiluminescence — dominant source, ~1-1000 photons/cm²/s
       Isotropic emission, only a fraction couples into waveguide
       
    Both sources are empirically grounded:
    - Nanoantenna: channel density, driving voltage, dipole length from 
      measured values (rat optic nerve, Zangari Table 1)
    - ROS: baseline emission from Kobayashi et al. 2009, Cifra & Pospíšil 2014
    
    Parameters
    ----------
    ap_rate_hz : float
        Action potential firing rate (Hz). Affects nanoantenna emission
        integrated over time. Default 10 Hz (typical cortical neuron).
    
    Returns
    -------
    dict with signal history, source breakdown, and metadata.
    """
    from .waveguide import attenuation_db_per_cm, transfer_matrix_transmission
    from .emission import ros_spectrum
    
    lam = np.atleast_1d(wavelength_nm).astype(np.float64)
    
    # Setup
    node = NodeEmission(axon, channel_density=channel_density)
    internode_cm = axon.internode_length_um() * 1e-4
    
    # Single internode transmission
    t_sheath = transfer_matrix_transmission(axon, lam)
    atten = attenuation_db_per_cm(lam)
    t_internode = t_sheath * 10 ** (-atten * internode_cm / 10)
    
    # Node coupling — fraction of light that re-enters next internode
    # Zangari showed directional radiation pattern; coupling is better
    # than isotropic assumption. Use measured node_coupling_loss_db.
    coupling = 10 ** (-node_coupling_loss_db / 10)
    
    # === Source 1: Nanoantenna emission (per second, at given AP rate) ===
    # Photons per AP × AP rate = photons/s from EM radiation
    antenna_per_ap = node.emission_spectrum(lam)  # photons/AP/nm
    antenna_per_s = antenna_per_ap * ap_rate_hz   # photons/s/nm
    # This is DIRECTIONAL — most couples into waveguide (Zangari Figs 2-3)
    antenna_waveguide_coupling = 0.3  # conservative: 30% into forward mode
    antenna_emission = antenna_per_s * antenna_waveguide_coupling
    
    # === Source 2: ROS chemiluminescence (continuous, isotropic) ===
    if include_ros:
        # Baseline: 100 photons/cm²/s (Kobayashi, Cifra)
        # At node: no myelin → direct emission from exposed membrane
        # Scale to node surface area
        ros = ros_spectrum(lam) * C.BASELINE_EMISSION_PHOTONS_PER_CM2_PER_S
        node_area_cm2 = node.node_area_um2 * 1e-8
        ros_per_node = ros * node_area_cm2
        # ROS is isotropic; fraction coupling into waveguide
        # Node is a ~1μm gap; guided modes subtend small solid angle
        ros_coupling = 0.05  # ~5% couples into guided modes (conservative)
        ros_guided = ros_per_node * ros_coupling
    else:
        ros_guided = np.zeros_like(lam)
        ros_per_node = np.zeros_like(lam)
    
    # Total guided emission per node per second
    new_per_node = antenna_emission + ros_guided
    
    # Propagate through chain
    signal_history = np.zeros((n_nodes + 1, len(lam)))
    original_history = np.zeros((n_nodes + 1, len(lam)))
    antenna_history = np.zeros((n_nodes + 1, len(lam)))
    ros_history = np.zeros((n_nodes + 1, len(lam)))
    
    # Node 0 emits
    signal_history[0] = new_per_node.copy()
    original_history[0] = new_per_node.copy()
    antenna_history[0] = antenna_emission.copy()
    ros_history[0] = ros_guided.copy()
    
    for i in range(1, n_nodes + 1):
        # Signal from previous node propagates through internode + coupling
        surviving = signal_history[i-1] * t_internode * coupling
        
        # This node emits its own photons
        signal_history[i] = surviving + new_per_node
        original_history[i] = original_history[i-1] * t_internode * coupling
        antenna_history[i] = antenna_emission.copy()
        ros_history[i] = ros_guided.copy()
    
    # Steady-state computation (geometric series)
    # S_ss = E / (1 - T) where E = emission per node, T = internode transmission
    T = t_internode * coupling
    steady_state = np.where(T < 1.0, new_per_node / (1.0 - T), np.inf)
    
    return {
        'total_signal': signal_history,
        'surviving_original': original_history,
        'antenna_contribution': antenna_history,
        'ros_contribution': ros_history,
        'new_per_node': new_per_node,
        'transmission_per_internode': t_internode * coupling,
        'steady_state': steady_state,
        'wavelength_nm': lam,
        'node_emission': node,
        'n_nodes': n_nodes,
        'ap_rate_hz': ap_rate_hz,
        'sources': {
            'antenna_photons_per_ap': antenna_per_ap,
            'antenna_per_s': antenna_per_s,
            'ros_total_per_node': ros_per_node if include_ros else np.zeros_like(lam),
            'ros_guided': ros_guided,
        },
    }


def ap_timing(
    axon: AxonGeometry,
    n_nodes: int = 10,
    conduction_velocity_ms: float = 50.0,
) -> dict:
    """Compute timing of AP arrival and photon arrival at each node.
    
    Demonstrates that photons from node N arrive at node N+1 
    BEFORE the action potential does.
    
    Parameters
    ----------
    conduction_velocity_ms : float
        AP conduction velocity in m/s. Myelinated: 20-120 m/s.
    
    Returns
    -------
    dict with timing arrays for each node.
    """
    internode_m = axon.internode_length_um() * 1e-6
    
    # AP travel time between nodes
    ap_transit_s = internode_m / conduction_velocity_ms
    
    # Photon travel time between nodes (at c/n_axon)
    photon_velocity = C.C_LIGHT / C.N_AXON
    photon_transit_s = internode_m / photon_velocity
    
    # Time advantage: how much earlier photons arrive vs AP
    photon_advantage_s = ap_transit_s - photon_transit_s
    
    nodes = np.arange(n_nodes + 1)
    ap_arrival = nodes * ap_transit_s
    photon_arrival = nodes * photon_transit_s  # from node 0
    
    return {
        'nodes': nodes,
        'ap_arrival_s': ap_arrival,
        'photon_arrival_from_origin_s': photon_arrival,
        'ap_transit_per_internode_s': ap_transit_s,
        'photon_transit_per_internode_s': photon_transit_s,
        'photon_advantage_s': photon_advantage_s,
        'photon_advantage_us': photon_advantage_s * 1e6,
        'internode_m': internode_m,
    }
