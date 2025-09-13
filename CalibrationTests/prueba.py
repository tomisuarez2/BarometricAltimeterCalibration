import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

from BarometricAltimeterCalibrationModules.utils import extract_barometric_altimeter_data, show_time_data


def estimate_first_order(T, y, dt, max_delay_secs=60):
    """
    Estimate discrete first-order model b[k] = alpha*b[k-1] + beta*T[k-d]
    Returns: alpha, beta, delay_samples
    """
    # Preprocess: remove means (use T0 = mean(T))
    T0 = np.mean(T)
    Tc = T - T0
    yc = y - np.mean(y)

    # estimate delay via cross-correlation
    maxlag = int(max_delay_secs / dt)
    corr = signal.correlate(yc, Tc, mode='full')
    lags = np.arange(-len(Tc)+1, len(yc))
    # limit search to +/- maxlag
    center = len(corr)//2
    search_slice = slice(center - maxlag, center + maxlag + 1)
    best_idx = np.argmax(corr[search_slice])
    lag = lags[search_slice][best_idx]
    delay_samples = -lag  # sign convention: if T leads y, we'll have positive delay
    if delay_samples < 0: delay_samples = 0

    # Build regression for samples where k-1 and k-d available
    N = len(y)
    d = int(delay_samples)
    rows = []
    rhs = []
    # We'll model b ~ alpha*b_prev + beta*T_shifted. Replace b by y if bias dominates.
    for k in range(max(1, d+1), N):
        rows.append([y[k-1], Tc[k-d]])
        rhs.append(y[k])
    A = np.array(rows)
    bvec = np.array(rhs)
    # least squares
    theta, *_ = np.linalg.lstsq(A, bvec, rcond=None)
    alpha, beta = theta[0], theta[1]

    # recover tau and K
    if alpha <= 0 or alpha >= 1:
        tau = None
        K = None
    else:
        tau = -dt / np.log(alpha)
        K = beta / (1 - alpha)

    return dict(alpha=alpha, beta=beta, tau=tau, K=K, delay_samples=d, T0=T0)

def simulate_model(T, dt, params, sigma_w=0.02, sigma_rw=0.0, seed=None, add_spikes=False):
    np.random.seed(seed)
    N = len(T)
    T0 = params['T0']
    alpha = params['alpha']
    beta = params['beta']
    d = params['delay_samples']
    y = np.zeros(N)
    rw = 0.0
    for k in range(1, N):
        Tk = T[k-d] - T0 if k-d >= 0 else T[0]-T0
        y[k] = alpha*y[k-1] + beta*Tk
        if sigma_rw > 0:
            rw += np.random.randn()*sigma_rw
        y[k] += rw
        y[k] += np.random.randn()*sigma_w
    if add_spikes:
        # randomly inject some spikes
        idx = np.random.choice(np.arange(N), size=int(N*0.001), replace=False)
        y[idx] += np.random.choice([+5.0, -5.0], size=len(idx))
    return y

# --- Usage example ---
# Suppose you loaded arrays time (s), T_meas (degC), y_meas (m)
file_name = "characterization data/bar_alt_data_3_hours.csv" 
parameters, bar_data = extract_barometric_altimeter_data(file_name)
T_meas = bar_data[:,0]
y_meas = bar_data[:,1]
n_samples = bar_data.shape[0]

sampling_freq, t_init = parameters
time = np.arange(0, n_samples, 1) / sampling_freq
dt = 1 / sampling_freq
params = estimate_first_order(T_meas, y_meas, dt)
print(params)
y_sim = simulate_model(T_meas, dt, params, sigma_w=0.02, sigma_rw=1e-4, seed=42, add_spikes=True)
plt.plot(time, y_meas, label='meas')
plt.plot(time, y_sim, label='sim', alpha=0.8)
plt.legend(); plt.show()
