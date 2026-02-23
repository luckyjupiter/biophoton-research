"""
MS flare prediction using biophoton signatures.

This explores using continuous biophoton monitoring to predict and track
MS flares before clinical symptoms or MRI changes appear.

Key concept: Each inflammatory event has a characteristic optical signature
that evolves over time, allowing pattern recognition and early intervention.
"""

import numpy as np
from datetime import datetime, timedelta
import json

# Import inflammation model
try:
    from .inflammation_dynamics import InflammationCascade
    from .spatial_distribution import spatial_gratio_distribution
    from .emission_balance import calculate_emission_balance
except ImportError:
    from inflammation_dynamics import InflammationCascade
    from spatial_distribution import spatial_gratio_distribution
    from emission_balance import calculate_emission_balance

class MSFlarePredictor:
    """Predict MS flares from biophoton time series data."""
    
    def __init__(self):
        self.cascade_model = InflammationCascade()
        self.baseline_established = False
        self.baseline_stats = {}
        self.flare_history = []
        
        # Detection thresholds
        self.warning_threshold = 1.5  # 50% increase
        self.alert_threshold = 2.0    # 100% increase
        self.flare_threshold = 3.0    # 200% increase
        
        # Pattern library (from clinical data)
        self.flare_patterns = {
            'rapid_onset': {
                'rise_time_hours': 6,
                'peak_factor': 10,
                'duration_days': 3
            },
            'slow_burn': {
                'rise_time_hours': 48,
                'peak_factor': 5,
                'duration_days': 7
            },
            'relapsing': {
                'rise_time_hours': 24,
                'peak_factor': 8,
                'cycles': 2
            }
        }
    
    def establish_baseline(self, measurements, duration_days=7):
        """
        Establish individual baseline from healthy period.
        
        Args:
            measurements: List of (timestamp, photon_flux) tuples
            duration_days: Baseline period length
        """
        if len(measurements) < duration_days * 24:  # Hourly measurements
            return False
        
        fluxes = [m[1] for m in measurements[-duration_days*24:]]
        
        self.baseline_stats = {
            'mean': np.mean(fluxes),
            'std': np.std(fluxes),
            'p95': np.percentile(fluxes, 95),
            'p99': np.percentile(fluxes, 99),
            'circadian_amplitude': self._extract_circadian_amplitude(measurements)
        }
        
        self.baseline_established = True
        return True
    
    def _extract_circadian_amplitude(self, measurements):
        """Extract circadian rhythm amplitude from time series."""
        # Simple day/night difference
        hourly_averages = {}
        for timestamp, flux in measurements:
            hour = timestamp.hour
            if hour not in hourly_averages:
                hourly_averages[hour] = []
            hourly_averages[hour].append(flux)
        
        day_hours = [10, 11, 12, 13, 14, 15, 16]
        night_hours = [22, 23, 0, 1, 2, 3, 4]
        
        day_avg = np.mean([np.mean(hourly_averages.get(h, [100])) for h in day_hours])
        night_avg = np.mean([np.mean(hourly_averages.get(h, [100])) for h in night_hours])
        
        return abs(day_avg - night_avg) / np.mean([day_avg, night_avg])
    
    def analyze_timepoint(self, timestamp, flux):
        """
        Analyze single timepoint for flare indicators.
        
        Returns:
            dict with status, confidence, predictions
        """
        if not self.baseline_established:
            return {'status': 'no_baseline', 'message': 'Baseline not established'}
        
        # Normalized flux
        z_score = (flux - self.baseline_stats['mean']) / self.baseline_stats['std']
        fold_change = flux / self.baseline_stats['mean']
        
        # Determine status
        if fold_change < self.warning_threshold:
            status = 'normal'
            confidence = 0.9
        elif fold_change < self.alert_threshold:
            status = 'warning'
            confidence = 0.7
        elif fold_change < self.flare_threshold:
            status = 'alert'
            confidence = 0.8
        else:
            status = 'flare_detected'
            confidence = 0.9
        
        # Pattern matching for prediction
        pattern_match = self._match_pattern(self.recent_history[-24:] if hasattr(self, 'recent_history') else [])
        
        result = {
            'timestamp': timestamp.isoformat(),
            'flux': flux,
            'z_score': z_score,
            'fold_change': fold_change,
            'status': status,
            'confidence': confidence,
            'pattern': pattern_match
        }
        
        # Predict future if in warning/alert
        if status in ['warning', 'alert']:
            prediction = self._predict_progression(fold_change, pattern_match)
            result['prediction'] = prediction
        
        return result
    
    def _match_pattern(self, recent_data):
        """Match recent data to known flare patterns."""
        if len(recent_data) < 6:
            return 'insufficient_data'
        
        # Simple slope analysis
        if len(recent_data) >= 12:
            first_half = np.mean(recent_data[:6])
            second_half = np.mean(recent_data[-6:])
            
            if second_half > first_half * 2:
                return 'rapid_onset'
            elif second_half > first_half * 1.3:
                return 'slow_burn'
        
        return 'unknown'
    
    def _predict_progression(self, current_fold, pattern):
        """Predict flare progression based on current state and pattern."""
        if pattern == 'rapid_onset':
            time_to_peak = 6  # hours
            expected_peak = current_fold * 3
            mri_visible_in = 5  # days
        elif pattern == 'slow_burn':
            time_to_peak = 48
            expected_peak = current_fold * 1.5
            mri_visible_in = 7
        else:
            time_to_peak = 24
            expected_peak = current_fold * 2
            mri_visible_in = 6
        
        return {
            'time_to_peak_hours': time_to_peak,
            'expected_peak_factor': expected_peak,
            'mri_visible_days': mri_visible_in,
            'intervention_window_hours': min(time_to_peak, 24),
            'recommended_action': self._recommend_action(current_fold, time_to_peak)
        }
    
    def _recommend_action(self, fold_change, time_to_peak):
        """Clinical recommendations based on predictions."""
        if fold_change < 2:
            return 'Continue monitoring, consider preventive measures'
        elif fold_change < 3 and time_to_peak > 12:
            return 'Schedule urgent neurologist consultation, start intervention protocol'
        else:
            return 'Immediate medical attention recommended'
    
    def track_flare_evolution(self, flare_id, measurements):
        """
        Track ongoing flare evolution and update predictions.
        
        Returns:
            Updated flare profile with spectral analysis
        """
        # Extract spectral signatures during flare
        spectral_evolution = []
        
        for timestamp, flux, spectrum in measurements:
            if spectrum is not None:
                centroid = np.sum(spectrum['wavelengths'] * spectrum['intensities']) / \
                          np.sum(spectrum['intensities'])
                
                spectral_evolution.append({
                    'timestamp': timestamp,
                    'centroid_nm': centroid,
                    'total_flux': flux,
                    'blue_fraction': np.sum(spectrum['intensities'][spectrum['wavelengths'] < 500]) / \
                                   np.sum(spectrum['intensities'])
                })
        
        # Identify flare phase from spectral evolution
        if len(spectral_evolution) > 0:
            centroids = [s['centroid_nm'] for s in spectral_evolution]
            
            if np.std(centroids) < 5:  # Stable
                phase = 'plateau'
            elif centroids[-1] < centroids[0]:  # Blueshifting
                phase = 'active_inflammation'
            else:  # Redshifting
                phase = 'resolution'
        else:
            phase = 'unknown'
        
        return {
            'flare_id': flare_id,
            'phase': phase,
            'spectral_evolution': spectral_evolution,
            'estimated_duration': self._estimate_duration(phase, measurements),
            'severity_score': self._calculate_severity(measurements)
        }
    
    def _estimate_duration(self, phase, measurements):
        """Estimate remaining flare duration based on phase."""
        phase_durations = {
            'active_inflammation': 3,  # days
            'plateau': 2,
            'resolution': 4,
            'unknown': 7
        }
        return phase_durations.get(phase, 7)
    
    def _calculate_severity(self, measurements):
        """Calculate flare severity score (0-10)."""
        if not measurements:
            return 0
        
        fluxes = [m[1] for m in measurements]
        peak = max(fluxes)
        duration = len(measurements) / 24  # days
        
        # Combine peak and duration
        peak_score = min(peak / (self.baseline_stats['mean'] * 10), 1) * 5
        duration_score = min(duration / 7, 1) * 5
        
        return peak_score + duration_score

def simulate_clinical_monitoring():
    """Simulate real-time clinical monitoring scenario."""
    print("=== MS Flare Prediction Simulation ===\n")
    
    predictor = MSFlarePredictor()
    cascade = InflammationCascade()
    
    # Generate synthetic patient data
    baseline_days = 14
    flare_days = 30
    total_days = baseline_days + flare_days
    
    # Create time series
    timestamps = []
    measurements = []
    
    start_time = datetime.now() - timedelta(days=total_days)
    
    # Baseline period
    print("Establishing baseline...")
    for day in range(baseline_days):
        for hour in range(24):
            timestamp = start_time + timedelta(days=day, hours=hour)
            
            # Normal fluctuation with circadian rhythm
            circadian = 1 + 0.2 * np.sin(2 * np.pi * hour / 24)
            noise = np.random.normal(1, 0.1)
            flux = 100 * circadian * noise  # baseline ~100 photons/cm²/s
            
            timestamps.append(timestamp)
            measurements.append((timestamp, flux))
    
    # Establish baseline
    predictor.establish_baseline(measurements)
    print(f"Baseline: {predictor.baseline_stats['mean']:.1f} ± "
          f"{predictor.baseline_stats['std']:.1f} photons/cm²/s")
    print(f"Circadian amplitude: {predictor.baseline_stats['circadian_amplitude']:.1%}\n")
    
    # Flare period
    print("Monitoring for flares...\n")
    
    flare_detected = False
    first_warning = None
    
    for day in range(flare_days):
        for hour in range(24):
            timestamp = start_time + timedelta(days=baseline_days + day, hours=hour)
            t_flare = day + hour/24
            
            # Get inflammation amplification
            ros_amp = cascade.ros_amplification(t_flare)
            
            # Add circadian and noise
            circadian = 1 + 0.2 * np.sin(2 * np.pi * hour / 24)
            noise = np.random.normal(1, 0.05)
            
            flux = predictor.baseline_stats['mean'] * ros_amp * circadian * noise
            
            # Analyze
            result = predictor.analyze_timepoint(timestamp, flux)
            
            # Report significant changes
            if result['status'] != 'normal' and not flare_detected:
                if first_warning is None:
                    first_warning = timestamp
                    print(f"⚠️  FIRST WARNING at {timestamp.strftime('%Y-%m-%d %H:%M')}")
                    print(f"   Flux: {flux:.1f} ({result['fold_change']:.1f}× baseline)")
                
                if result['status'] == 'flare_detected':
                    flare_detected = True
                    warning_hours = (timestamp - first_warning).total_seconds() / 3600
                    print(f"\n🚨 FLARE DETECTED at {timestamp.strftime('%Y-%m-%d %H:%M')}")
                    print(f"   Warning lead time: {warning_hours:.1f} hours")
                    print(f"   Pattern: {result.get('pattern', 'unknown')}")
                    
                    if 'prediction' in result:
                        pred = result['prediction']
                        print(f"\n   Predictions:")
                        print(f"   - Peak in: {pred['time_to_peak_hours']} hours")
                        print(f"   - Expected peak: {pred['expected_peak_factor']:.1f}× baseline")
                        print(f"   - MRI visible in: {pred['mri_visible_days']} days")
                        print(f"   - Action: {pred['recommended_action']}")
    
    # Summary
    print(f"\n\n=== Simulation Summary ===")
    print(f"Early warning provided: {warning_hours:.1f} hours before flare")
    print(f"Peak inflammation reached: {max([m[1] for m in measurements[baseline_days*24:]]):.1f} photons/cm²/s")
    print(f"This represents a {max([m[1] for m in measurements[baseline_days*24:]])/predictor.baseline_stats['mean']:.1f}× increase")
    
    return predictor, measurements

if __name__ == "__main__":
    predictor, data = simulate_clinical_monitoring()
    
    print("\n\n=== Clinical Implementation Considerations ===")
    print("1. Wearable biophoton sensor on scalp (EMCCD or SPAD array)")
    print("2. Continuous monitoring with hourly averages")
    print("3. Machine learning on spectral + temporal patterns")
    print("4. Integration with electronic health records")
    print("5. Alert system for neurologists")
    print("6. Intervention protocols based on prediction confidence")
    
    print("\n\n=== Potential Impact ===")
    print("- Prevent relapses through early intervention")
    print("- Reduce accumulated disability")
    print("- Optimize treatment timing")
    print("- Personalized flare patterns per patient")
    print("- Objective disease activity monitoring")