
"""
Barometric Altimeter Calibration Module
Authors: Tomás Suárez, Agustín Corazza, Rodrigo Pérez
University: Universidad Nacional de Cuyo
"""
from typing import Literal, Optional, Tuple, Union 

import numpy as np
from scipy.stats import linregress

from . import utils

#====================================================================
#------------Functions for barometric atimeter calibration-----------
#====================================================================

#===========================================================
#----------Functions for synthetic data generation----------
#===========================================================

def simulate_sensor_data(
    N: int, 
    fs: float, 
    R: float, 
    q: float, 
    seed: int = None
) -> np.ndarray:
    """
    Simulate synthetic sensor data with white noise and bias random walk.

    Args:
        N: Number of samples.
        fs: Sampling frequency [Hz].
        R: White noise variance (per sample).
        q: Random walk variance (per sample).
        seed: Random seed for reproducibility.

    Returns:
        y: Synthetic sensor measurement array of length N.
    """
    if seed is not None:
        np.random.seed(seed)

    # White noise
    w = 0
    if not np.isnan(R):
        w = np.random.normal(0, np.sqrt(R*fs), size=N)

    # Random walk increments for bias
    u = 0
    if not np.isnan(q):
        u = np.random.normal(0, np.sqrt(q/fs), size=N)

    # Integrate random walk bias
    b = np.cumsum(u)

    # Synthetic measurements
    y = b + w

    return y

#===========================================================
#-----------Functions for signal characterization-----------
#===========================================================

def compute_allan_variance(
    data: np.ndarray, 
    fs: Union[int,float], 
    m_steps: Literal['linear', 'exponential'] = 'linear'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute the Allan Variance of the input data.

    Args:
        data: Input array of shape (N, n) where N is number of samples and n is number of signals.
        fs: Sampling rate in Hz.
        m_steps: Method for interval length variation:
                'linear' - linear spacing between intervals
                'exponential' - base-2 exponential spacing (default: 'linear')

    Returns:
        Tuple containing:
        - taus: Array of interval lengths in seconds
        - avar: Array of corresponding Allan Variance values

    Notes:
        - For 'linear', evaluates intervals from 2 samples to N//2 samples
        - For 'exponential', evaluates intervals as powers of 2 up to N//2
        - Minimum of 2 intervals required for variance calculation
    """
    n_samples = data.shape[0]

    # Generate interval lengths (tau in samples)
    if m_steps == 'linear':
        max_m = n_samples // 2                   
        taus = np.arange(2, max_m, dtype=int) 
    elif m_steps == 'exponential':
        max_power = int(np.floor(np.log2(n_samples // 2)))
        taus = 2**np.arange(1, max_power + 1)
    else:
        raise ValueError("m_steps must be either 'linear' or 'exponential'")
             
    # Pre-allocate array for Allan Variance resuts
    avar = np.empty((len(taus), 1 if data.ndim == 1 else data.shape[1]))

    for i, tau in enumerate(taus):
        # Reshape data into intervals of length tau
        n_intervals = n_samples // tau
        reshaped = data[:n_intervals * tau].reshape(n_intervals, tau, -1)

        # Compute means and differences 
        interval_means = reshaped.mean(axis=1)
        diffs = np.diff(interval_means, axis=0)

        # Compute the Allan Variance
        avar[i] = 0.5 * np.mean(diffs**2, axis=0)

    return taus / fs, avar

def auto_estimate_R_q_from_allan(
    tau: np.ndarray, 
    sigma: np.ndarray, 
    slope_tol: float=0.1, 
    min_points: int=3,
    plot: bool=False
) -> Tuple[float, float, Tuple[int, int], Tuple[int, int]]:
    """
    Automatically estimate R and q from Allan deviation curve.
    It is assumed the standard 1-state random–walk + white-noise measurement model
    for the altimeter signal.

    d_k = p_k + b_k + v_k ,    v_k ~ N(0, R)
    b_{k+1} = b_k + w_k ,      w_k ~ N(0, q·T_s)

    where:
        - d_k = barometer measurement (altitude)
        - p_k = true altitude
        - R   = white measurement–noise variance [m²]
        - b_k = barometer bias at step k
        - q   = bias random–walk intensity [m²/s]
        - T_s = sampling time [s]

    Args:
        tau: Array of interval lengths in seconds.
        sigma : Array of corresponding Allan Deviation values [m].
        slope_tol : Allowed deviation from ideal slopes (-0.5, +0.5).
        min_points : Minimum number of consecutive points to accept a region.

    Returns:
        R : Measurement noise variance [m^2].
        q : Random walk intensity [m^2/s].
        tau_white_region : (min_tau, max_tau) used for white noise fit.
        tau_rw_region : (min_tau, max_tau) used for random walk fit.
    """
    logtau = np.log10(tau)
    logsig = np.log10(sigma)

    # Local slopes between adjacent points
    slopes = np.diff(logsig) / np.diff(logtau)
    
    def find_region(
        target_slope: float
    ) -> Optional[Tuple[int, int]]:
        """"
        Find regions whit an desired slope.

        Args:
            target_slop: Desired slope.
        
        Returns:
            A tuple containing the indices of the region.
        """
        mask = np.abs(slopes - target_slope) < slope_tol
        # Group consecutive True values
        regions = []
        start = None
        for i, m in enumerate(mask):
            if m and start is None:
                start = i
            elif not m and start is not None:
                if i - start + 1 >= min_points:
                    regions.append((start, i))
                start = None
        if start is not None and len(slopes)-start >= min_points:
            regions.append((start, len(slopes)-1))
        if not regions:
            return None
        # Choose longest region
        region = max(regions, key=lambda r: r[1]-r[0])
        return region
    
    # White noise region 
    reg_w = find_region(-0.5)
    if reg_w:
        idx = range(reg_w[0], reg_w[1]+1)
        _, intercept_w, *_ = linregress(logtau[idx], logsig[idx])
        # Model: sigma = sqrt(R)/sqrt(tau) => log10(sigma) = -0.5*log10(tau) + log10(sqrt(R))
        sqrtR = 10**intercept_w
        R = sqrtR**2
        tau_white = (tau[idx[0]], tau[idx[-1]])
    else:
        R, tau_white = np.nan, None

    # Random walk region 
    reg_rw = find_region(0.5)
    if reg_rw:
        idx = range(reg_rw[0], reg_rw[1]+1)
        _, intercept_rw, *_ = linregress(logtau[idx], logsig[idx])
        # Model: sigma = sqrt(q/3) * sqrt(tau) => log10(sigma) = 0.5*log10(tau) + log10(sqrt(q/3))
        sqrt_q_over_3 = 10**intercept_rw
        q = 3 * (sqrt_q_over_3**2)
        tau_rw = (tau[idx[0]], tau[idx[-1]])
    else:
        q, tau_rw = np.nan, None

    if plot:
        utils.show_loglog_data(tau, np.vstack([sigma,np.sqrt(R)/np.sqrt(tau),np.sqrt(q/3)*np.sqrt(tau)]).T, 
                               legend=["Relative altitude Allan Dev.","White-Gaussian Noise","Random-Walk bias"],
                               xlabel="Interval Length [s]", ylabel="Allan Deviation [m]",
                               title="Altitude signal Allan Deviation")

    return R, q, tau_white, tau_rw





    
