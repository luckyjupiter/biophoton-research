#!/usr/bin/env python3
"""
Master script to generate all publication-quality figures for the biophoton research.
Ensures consistency and makes it easy to regenerate everything.
"""

import os
import sys
import subprocess
from datetime import datetime

# Add models to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'models'))

def run_script(script_name, description):
    """Run a visualization script and report status."""
    print(f"\n{'='*60}")
    print(f"Generating: {description}")
    print(f"Script: {script_name}")
    print(f"{'='*60}")
    
    try:
        # Use subprocess to capture output
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Success!")
        if result.stdout:
            print("Output:", result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed with error:")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def create_figure_index():
    """Create an HTML index of all generated figures."""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Biophoton Research Figures</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .figure {{ margin: 20px 0; border: 1px solid #ccc; padding: 10px; }}
        img {{ max-width: 100%; height: auto; }}
        h1, h2 {{ color: #333; }}
        .metadata {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>Biophoton Demyelination Research - Figure Gallery</h1>
    <p class="metadata">Generated: {timestamp}</p>
    
    <h2>Core Model Visualizations</h2>
    
    <div class="figure">
        <h3>Figure 1: Comprehensive Analysis</h3>
        <img src="comprehensive_biophoton_analysis.png" alt="Comprehensive Analysis">
        <p>6-panel figure showing cuprizone timeline, waveguide physics, spectral predictions, 
        detector efficiency, detection impact, and key insights.</p>
    </div>
    
    <div class="figure">
        <h3>Figure 2: Master Model Summary</h3>
        <img src="master_biophoton_models.png" alt="Master Models">
        <p>8-panel comprehensive figure including chronic model, spatial distribution, 
        remyelination quality, and experimental design.</p>
    </div>
    
    <div class="figure">
        <h3>Figure 3: Human Brain Detection Gap</h3>
        <img src="human_brain_detection_gap.png" alt="Detection Gap">
        <p>Shows why standard detectors miss >50% of human brain biophotons due to 
        865nm peak in detector efficiency gap.</p>
    </div>
    
    <h2>Physics Models</h2>
    
    <div class="figure">
        <h3>Figure 4: Relay Model Visualization</h3>
        <img src="../viz_output/relay_vs_pure_loss.png" alt="Relay Model">
        <p>Node-to-node photon relay achieving steady state vs exponential decay.</p>
    </div>
    
    <div class="figure">
        <h3>Figure 5: Cuprizone Dual Signature</h3>
        <img src="../viz_output/cuprizone_dual_signature.png" alt="Dual Signature">
        <p>External emission increases while internal relay decreases during demyelination.</p>
    </div>
    
    <h2>Cavity QED Analysis</h2>
    
    <div class="figure">
        <h3>Figure 6: Cavity QED Irrelevance</h3>
        <img src="cavity_qed_analysis.png" alt="Cavity QED">
        <p>4-panel figure demonstrating why quantum effects are negligible: weak coupling, 
        rapid decoherence, and classical emission dominance.</p>
    </div>
    
    <div class="figure">
        <h3>Figure 7: Emission Spectrum Comparison</h3>
        <img src="emission_spectrum_comparison.png" alt="Emission Spectra">
        <p>Comparison of ROS, nanoantenna, thermal, and QED emission mechanisms across wavelengths.</p>
    </div>
    
    <h2>Model Validation</h2>
    
    <div class="figure">
        <h3>Figure 8: Two-Mechanism Timeline</h3>
        <img src="../viz_output/two_mechanism_v2_timeline.png" alt="Two-Mechanism Model">
        <p>Validated model showing 96% error reduction with separated metabolic and waveguide components.</p>
    </div>
    
    <hr>
    <p class="metadata">
    Repository: <a href="https://github.com/luckyjupiter/biophoton-research">github.com/luckyjupiter/biophoton-research</a><br>
    Contact: Dr. Jiapei Dai collaboration pending
    </p>
</body>
</html>
""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    with open('figure_index.html', 'w') as f:
        f.write(html)
    print("\n✅ Created figure index: figure_index.html")

def main():
    """Generate all figures in the correct order."""
    print("Biophoton Research - Master Figure Generation")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Track success
    results = []
    
    # List of scripts to run
    scripts = [
        ("viz_comprehensive.py", "Comprehensive analysis and detector response"),
        ("viz_all_models.py", "Master model summary with all improvements"),
        ("viz_relay_suite.py", "Relay model visualization suite"),
        ("viz_cavity_qed.py", "Cavity QED analysis and emission spectra"),
    ]
    
    # Change to tools directory
    original_dir = os.getcwd()
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(tools_dir)
    
    try:
        # Run each script
        for script, description in scripts:
            if os.path.exists(script):
                success = run_script(script, description)
                results.append((script, success))
            else:
                print(f"⚠️  Skipping {script} - not found")
                results.append((script, False))
        
        # Create index
        create_figure_index()
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        successful = sum(1 for _, success in results if success)
        total = len(results)
        
        print(f"\nGenerated {successful}/{total} figure sets successfully")
        
        if successful < total:
            print("\nFailed scripts:")
            for script, success in results:
                if not success:
                    print(f"  - {script}")
        
        print(f"\nAll figures are in: {tools_dir}")
        print(f"View index at: {os.path.join(tools_dir, 'figure_index.html')}")
        
    finally:
        # Return to original directory
        os.chdir(original_dir)
    
    return successful == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)