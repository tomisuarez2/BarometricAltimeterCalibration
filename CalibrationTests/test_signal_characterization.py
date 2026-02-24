"""
Barometric Altimeter signal characterization test
Authors: Tomás Suárez, Agustín Corazza, Rodrigo Pérez
University: Universidad Nacional de Cuyo
"""

import numpy as np

import BarometricAltimeterCalibrationModules.bar_altimeter_calibration as bar
from BarometricAltimeterCalibrationModules.utils import extract_barometric_altimeter_data, show_time_data

spanish = False

# Use synthetic data
synthetic = False

# Save data flag
save = False

# Read data
if not synthetic:
    file_name = "characterization data/static_bar_alt_data_3_3_V.csv" 
    params, bar_data = extract_barometric_altimeter_data(file_name)
    sampling_freq, t_init = params
else:
    R_real = 0.001
    q_real = 0.00001
    sampling_freq = 80
    bar_data = bar.simulate_sensor_data(60000,sampling_freq, R_real, q_real)
n_samples = bar_data.shape[0]

rel_alt = bar_data[:,0]
temp = bar_data[:,1]
time_vector = np.arange(0, n_samples, 1) / sampling_freq

# Compute Allan Variance
tau, avar = bar.compute_allan_variance(rel_alt, sampling_freq, m_steps='exponential')
rel_alt_a_dev = np.sqrt(avar).reshape(-1)

# Estimate R and q values
if spanish:
    title_plot = "Desviacion de Allan de la medición del barómetro"
else:
    title_plot = "Barometer measurement Allan Deviation"
R, q, tauwn, taurw = bar.auto_estimate_R_q_from_allan(tau, rel_alt_a_dev, sampling_freq, u='m', title=title_plot, plot=True, spanish=spanish)

# Show results
if spanish:
    print(f">>> Número de muestras en el archivo de calibración: {n_samples}")
    print(f">>> Varianza del ruido blanco de medición del barómetro [-]: {R}")
    print(f">>> Intensidad de la caminata aleatoria del sesgo del barómetro [(-)/s]: {q}")
else:
    print(f">>> Number of samples in the calibration file: {n_samples}")
    print(f">>> Barometer white measurement–noise variance [-]: {R}")
    print(f">>> Barometer bias random–walk intensity [(-)/s]: {q}")

# Save data if required
if save:
    np.savetxt("characterization result data/R_q_bar_alt.csv", (R, q), delimiter=',')

# Show time data and simulated data.
sim_data = bar.simulate_sensor_data(n_samples, sampling_freq, R, q, temp)

if spanish:
    show_time_data(np.vstack([rel_alt, sim_data]).T, sampling_freq, legend=["Señal medida", "Señal simulada"], xlabel="Tiempo [s]", ylabel="[m]", title="Comparación de señales - Barómetro")
else:
    show_time_data(np.vstack([rel_alt, sim_data]).T, sampling_freq, ["Logged Signal", "Simulated Signal"], ylabel="[m]", title="Signal comparison - Barometer")

