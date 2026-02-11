"""
Cylindrical waveguide mode solver for myelinated axon.

Solves the characteristic equation for guided modes in a three-layer
cylindrical waveguide: axoplasm (core) | myelin (annular guiding region) |
extracellular fluid (outer cladding).

References:
    Snyder and Love (1983), Optical Waveguide Theory
    Kumar et al. (2016), Scientific Reports 6, 36508
"""

import numpy as np
from scipy.special import jv, yv, iv, kv, jvp, yvp, ivp, kvp
from scipy.optimize import brentq
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import (
    AxonGeometry, N_MYELIN, N_AXOPLASM, N_ECF,
    n_myelin, n_axoplasm, n_ecf, C_VACUUM
)


def characteristic_equation_3layer(beta, k0, l, r_inner, r_outer, n1, n2, n3):
    kappa1_sq = n1**2 * k0**2 - beta**2
    kappa2_sq = n2**2 * k0**2 - beta**2
    kappa3_sq = n3**2 * k0**2 - beta**2
    if kappa2_sq <= 0:
        return 1e10
    kappa2 = np.sqrt(kappa2_sq)
    u2_inner = kappa2 * r_inner
    u2_outer = kappa2 * r_outer
    if u2_inner < 1e-12 or u2_outer < 1e-12:
        return 1e10
    if kappa1_sq >= 0:
        kappa1 = np.sqrt(kappa1_sq)
        u1 = kappa1 * r_inner
        if u1 < 1e-12:
            return 1e10
        J_val = jv(l, u1)
        if abs(J_val) < 1e-30:
            return 1e10
        Q1 = jvp(l, u1, 1) / (u1 * J_val)
    else:
        gamma1 = np.sqrt(-kappa1_sq)
        w1 = gamma1 * r_inner
        if w1 < 1e-12:
            return 1e10
        I_val = iv(l, w1)
        if abs(I_val) < 1e-30:
            return 1e10
        Q1 = ivp(l, w1, 1) / (w1 * I_val)
    if kappa3_sq >= 0:
        kappa3 = np.sqrt(kappa3_sq)
        u3 = kappa3 * r_outer
        if u3 < 1e-12:
            return 1e10
        J3_val = jv(l, u3)
        if abs(J3_val) < 1e-30:
            return 1e10
        Q3 = jvp(l, u3, 1) / (u3 * J3_val)
    else:
        gamma3 = np.sqrt(-kappa3_sq)
        w3 = gamma3 * r_outer
        if w3 < 1e-12:
            return 1e10
        K_val = kv(l, w3)
        if abs(K_val) < 1e-30:
            return 1e10
        Q3 = kvp(l, w3, 1) / (w3 * K_val)
    J2i = jv(l, u2_inner); Y2i = yv(l, u2_inner)
    J2o = jv(l, u2_outer); Y2o = yv(l, u2_outer)
    J2ip = jvp(l, u2_inner, 1); Y2ip = yvp(l, u2_inner, 1)
    J2op = jvp(l, u2_outer, 1); Y2op = yvp(l, u2_outer, 1)
    lhs_num = -(Y2ip - Q1 * u2_inner * Y2i)
    lhs_den = (J2ip - Q1 * u2_inner * J2i)
    rhs_num = -(Y2op - Q3 * u2_outer * Y2o)
    rhs_den = (J2op - Q3 * u2_outer * J2o)
    if abs(lhs_den) < 1e-30 or abs(rhs_den) < 1e-30:
        return 1e10
    return lhs_num * rhs_den - rhs_num * lhs_den


def find_modes(axon, wavelength_nm, l_max=5, n_search=500, use_dispersion=True):
    """Find all guided modes for a given axon geometry and wavelength."""
    lam_m = wavelength_nm * 1e-9
    k0 = 2 * np.pi / lam_m
    if use_dispersion:
        n1 = float(n_axoplasm(wavelength_nm))
        n2 = float(n_myelin(wavelength_nm))
        n3 = float(n_ecf(wavelength_nm))
    else:
        n1 = N_AXOPLASM; n2 = N_MYELIN; n3 = N_ECF
    r_inner = axon.r_axon_m
    r_outer = axon.r_outer_m
    beta_min = n3 * k0 * 1.00001
    beta_max = n2 * k0 * 0.99999
    if beta_min >= beta_max:
        return []
    modes = []
    for l in range(0, l_max + 1):
        betas = np.linspace(beta_min, beta_max, n_search)
        vals = np.array([characteristic_equation_3layer(
            b, k0, l, r_inner, r_outer, n1, n2, n3) for b in betas])
        m_count = 0
        for i in range(len(vals) - 1):
            if abs(vals[i]) > 1e8 or abs(vals[i+1]) > 1e8:
                continue
            if np.isnan(vals[i]) or np.isnan(vals[i+1]):
                continue
            if vals[i] * vals[i+1] < 0:
                try:
                    beta_root = brentq(
                        characteristic_equation_3layer,
                        betas[i], betas[i+1],
                        args=(k0, l, r_inner, r_outer, n1, n2, n3),
                        xtol=1e-12, maxiter=200)
                    m_count += 1
                    n_eff = beta_root / k0
                    V = axon.v_number(wavelength_nm, n_core=n2, n_clad=n3)
                    modes.append({
                        'l': l, 'm': m_count,
                        'beta': beta_root, 'n_eff': n_eff,
                        'V': float(V), 'wavelength_nm': wavelength_nm})
                except (ValueError, RuntimeError):
                    pass
    modes.sort(key=lambda x: -x['n_eff'])
    return modes


def compute_mode_field(mode, axon, r_points=500):
    """Compute the radial field profile for a given mode."""
    beta = mode['beta']; l = mode['l']
    wavelength_nm = mode['wavelength_nm']
    lam_m = wavelength_nm * 1e-9
    k0 = 2 * np.pi / lam_m
    n1 = float(n_axoplasm(wavelength_nm))
    n2 = float(n_myelin(wavelength_nm))
    n3 = float(n_ecf(wavelength_nm))
    r_inner = axon.r_axon_m; r_outer = axon.r_outer_m
    kappa1_sq = n1**2 * k0**2 - beta**2
    kappa2_sq = n2**2 * k0**2 - beta**2
    kappa3_sq = n3**2 * k0**2 - beta**2
    kappa2 = np.sqrt(max(kappa2_sq, 0))
    r_max = r_outer * 2.0
    r = np.linspace(1e-12, r_max, r_points)
    field = np.zeros_like(r)
    mask1 = r < r_inner
    if kappa1_sq >= 0:
        kappa1 = np.sqrt(kappa1_sq)
        field[mask1] = jv(l, kappa1 * r[mask1])
        val_at_boundary = jv(l, kappa1 * r_inner)
    else:
        gamma1 = np.sqrt(-kappa1_sq)
        field[mask1] = iv(l, gamma1 * r[mask1])
        val_at_boundary = iv(l, gamma1 * r_inner)
    mask2 = (r >= r_inner) & (r <= r_outer)
    u2_inner = kappa2 * r_inner
    J2i = jv(l, u2_inner); Y2i = yv(l, u2_inner)
    if abs(Y2i) > 1e-30:
        A2 = 1.0; B2 = (val_at_boundary - J2i) / Y2i
    elif abs(J2i) > 1e-30:
        A2 = val_at_boundary / J2i; B2 = 0.0
    else:
        A2 = 1.0; B2 = 0.0
    field[mask2] = A2 * jv(l, kappa2 * r[mask2]) + B2 * yv(l, kappa2 * r[mask2])
    mask3 = r > r_outer
    val_at_outer = A2 * jv(l, kappa2 * r_outer) + B2 * yv(l, kappa2 * r_outer)
    if kappa3_sq < 0:
        gamma3 = np.sqrt(-kappa3_sq)
        K_at_outer = kv(l, gamma3 * r_outer)
        C3 = val_at_outer / K_at_outer if abs(K_at_outer) > 1e-30 else 0.0
        field[mask3] = C3 * kv(l, gamma3 * r[mask3])
    else:
        kappa3r = np.sqrt(kappa3_sq)
        J3out = jv(l, kappa3r * r_outer)
        C3 = val_at_outer / J3out if abs(J3out) > 1e-30 else 0.0
        field[mask3] = C3 * jv(l, kappa3r * r[mask3])
    peak = np.max(np.abs(field))
    if peak > 0:
        field = field / peak
    return r * 1e6, field


def confinement_factor(mode, axon, r_points=1000):
    r_um, field = compute_mode_field(mode, axon, r_points)
    r_m = r_um * 1e-6
    intensity = field**2 * r_m
    dr = np.diff(r_m)
    ri = axon.r_axon_m; ro = axon.r_outer_m
    m1 = r_m[:-1] < ri
    m2 = (r_m[:-1] >= ri) & (r_m[:-1] < ro)
    m3 = r_m[:-1] >= ro
    mi = 0.5 * (intensity[:-1] + intensity[1:])
    Pa = np.sum(mi[m1] * dr[m1])
    Pm = np.sum(mi[m2] * dr[m2])
    Pe = np.sum(mi[m3] * dr[m3])
    Pt = Pa + Pm + Pe
    if Pt > 0:
        return dict(Gamma_axon=Pa/Pt, Gamma_myelin=Pm/Pt, Gamma_ecf=Pe/Pt)
    return dict(Gamma_axon=0, Gamma_myelin=0, Gamma_ecf=0)


def dispersion_curve(axon, wl_range=(380,700), n_wl=80, l_max=3):
    wls = np.linspace(wl_range[0], wl_range[1], n_wl)
    am = {}
    for lam in wls:
        for mode in find_modes(axon, lam, l_max=l_max):
            key = (mode["l"], mode["m"])
            if key not in am:
                am[key] = dict(l=mode["l"], m=mode["m"], wavelengths=[], n_eff=[], beta=[])
            am[key]["wavelengths"].append(lam)
            am[key]["n_eff"].append(mode["n_eff"])
            am[key]["beta"].append(mode["beta"])
    for k in am:
        for f in ["wavelengths","n_eff","beta"]:
            am[k][f] = np.array(am[k][f])
    return dict(wavelength_range=wls, modes=list(am.values()))


if __name__=="__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    axon=AxonGeometry(r_axon_um=0.5,g_ratio=0.7)
    print(axon.summary())
    modes=find_modes(axon,500.0,l_max=3)
    print("Found",len(modes),"modes at 500nm")
    for m in modes:
        cf=confinement_factor(m,axon)
        print("  LP(%d,%d) neff=%.6f Gm=%.4f"%(m["l"],m["m"],m["n_eff"],cf["Gamma_myelin"]))
    if modes:
        fig,ax=plt.subplots(figsize=(8,5))
        for m in modes[:4]:
            r,fld=compute_mode_field(m,axon)
            ax.plot(r,fld,lw=1.5,label="LP(%d,%d)"%(m["l"],m["m"]))
        ax.axvspan(axon.r_axon_um,axon.r_outer_um,alpha=0.15,color="gold")
        ax.axvline(axon.r_axon_um,color="gray",ls="--",alpha=0.7)
        ax.axvline(axon.r_outer_um,color="gray",ls=":",alpha=0.7)
        ax.set_xlabel("r [um]");ax.set_ylabel("Field");ax.legend(fontsize=8)
        ax.set_title("Mode Profiles at 500nm")
        fp=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","figures","mode_profiles.png")
        plt.savefig(fp,dpi=150,bbox_inches="tight");plt.close()
        print("Saved",fp)
    disp=dispersion_curve(axon,wl_range=(380,700),n_wl=30)
    fig2,ax2=plt.subplots(figsize=(8,5))
    for md in disp["modes"]:
        ax2.plot(md["wavelengths"],md["n_eff"],"-",lw=1.5,label="LP(%d,%d)"%(md["l"],md["m"]))
    ax2.set_xlabel("Wavelength [nm]");ax2.set_ylabel("n_eff");ax2.grid(True,alpha=0.3)
    ax2.set_title("Dispersion Curves");ax2.legend(fontsize=8,ncol=2)
    fp2=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","figures","dispersion_curves.png")
    plt.savefig(fp2,dpi=150,bbox_inches="tight");plt.close()
    print("Saved",fp2)
