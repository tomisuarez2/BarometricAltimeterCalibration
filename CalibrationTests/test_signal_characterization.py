"""
Barometric Altimeter signal characterization test
Authors: Tomás Suárez, Agustín Corazza, Rodrigo Pérez
University: Universidad Nacional de Cuyo
"""

import numpy as np

from BarometricAltimeterCalibrationModules import bar_altimeter_calibration as bar
from BarometricAltimeterCalibrationModules.utils import extract_barometric_altimeter_data, show_time_data

# Use synthetic data
synthetic = False

# Save data flag
save = True

# Read data
if not synthetic:
    file_name = "characterization data/static_bar_alt_data.csv" 
    params, bar_data = extract_barometric_altimeter_data(file_name)
    sampling_freq, t_init = params
else:
    R_real = 0.001
    q_real = 0.00001
    sampling_freq = 80
    bar_data = bar.simulate_sensor_data(60000,sampling_freq, R_real, q_real)
n_samples = bar_data.shape[0]
print(f"Number of samples in the file: {n_samples}")

# Compute Allan Variance
tau, avar = bar.compute_allan_variance(bar_data, sampling_freq, m_steps='exponential')
rel_alt_a_dev = np.sqrt(avar[:,:1]).reshape(-1)

# Estimate R and q values
R, q, tauwn, taurw = bar.auto_estimate_R_q_from_allan(tau, rel_alt_a_dev, plot=True)

# Show results
print(f"Barometric altimeter white measurement–noise variance [m²]: {R}")
print(f"Barometric altimeter bias random–walk intensity [m²/s]: {q}")

# Save data if required
if save:
    np.savetxt("characterization result data/R_q_bar_alt.csv", (R, q), delimiter=',')

# Show time data and simulated data.
sim_data = bar.simulate_sensor_data(n_samples,sampling_freq, R, q)
show_time_data(np.vstack([(bar_data[:,0] if bar_data.ndim > 1 else bar_data), sim_data]).T, 
               sampling_freq, ["Logged Signal", "Simulated Signal"])


