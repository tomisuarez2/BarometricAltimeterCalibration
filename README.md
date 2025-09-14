# 🌡️ Barometric Altimeter Calibration (MS5611 / GY-63)

This repository provides tools to **characterize and analyze the noise of barometric altimeters** using Allan Deviation analysis.
It is based on the **MS5611 pressure sensor**, commonly found on the **GY-63 module**.

The goal is to model and understand the sensor’s noise processes (white noise, bias random walk) and prepare the ground for future **automatic calibration** methods.

---

## ⚙️ How It Works

The repository implements a workflow to record, process, and analyze barometric altitude data:

1. **Raw Data Acquisition**

   * Data is collected from an MS5611 (GY-63) sensor.
   * Measurements are logged at a fixed sampling rate (default: about 80 Hz ).

2. **Allan Deviation Analysis**

   * From the altitude time series, Allan deviation (ADEV) is computed across multiple averaging times (τ).
   * This reveals how different noise sources dominate at different time scales:

     * **White noise (σ ∝ 1/√τ)**
     * **Random walk bias (σ ∝ √τ)**

3. **Noise Parameter Estimation**

   * The slopes of the Allan deviation curve are fitted to extract:

     * **R** → Measurement noise variance (white noise level).
     * **q** → Random walk bias intensity.

---

## 📐 Mathematical Background

Given a discrete-time sensor model:

* **Bias evolution**

$${b_{k+1} = b_k + w_k,\quad w_k \sim \mathcal{N}(0, Q)}$$ 

$Q = qT_s$

* **Measurement equation**

$$d_k = p_k + b_k + v_k,\quad v_k \sim \mathcal{N}(0, R)$$

where

* $d_k$ = barometric measurement (altitude),
* $p_k$ = true altitude,
* $b_k$ = bias (random walk),
* $v_k$ = white measurement noise,
* $q$ = bias random walk intensity \[m²/s],
* $R$ = measurement noise variance \[m²],
* $T_s$ = sampling period \[s].

We form cluster $i$ (block) averages of length $m$ samples: $\tau = mT_s$, then from Allan variance definition (discrete sampling):

$$
\bar d^{(m)}_i = \frac{1}{m}\sum_{k=0}^{m-1} d_{i m + k},
\qquad \tau = m T_s
$$

The Allan variance at averaging time $\tau$ is

$$
\sigma^2(\tau) = \frac{1}{2}\,\mathbb{E}\Big[ \big(\bar d^{(m)}_{i+1}-\bar d^{(m)}_{i}\big)^2 \Big]
$$

We will evaluate $\sigma^2(\tau)$ for the two noise types mentioned above.

---

### White measurement noise $v_k$

Assume $d_k = p_0 + v_k$ (ignore bias for the moment). For the block average,

$$
\bar v_i = \frac{1}{m}\sum_{j=0}^{m-1} v_{im+j}
$$

Because the $v$'s are independent with $\mathrm{Var}(v_k)=R$,

$$
\mathrm{Var}(\bar v_i) = \frac{1}{m^2}\sum_{j=0}^{m-1}\mathrm{Var}(v_{im+j})
= \frac{mR}{m^2} = \frac{R}{m}
$$

Now

$$
\mathrm{Var}(\bar v_{i+1}-\bar v_i) = \mathrm{Var}(\bar v_{i+1})+\mathrm{Var}(\bar v_i)
= 2\frac{R}{m},
$$

(averages from disjoint blocks are independent), so Allan variance

$$
\sigma^2(\tau) = \frac{1}{2}\cdot 2\frac{R}{m} = \frac{R}{m}
$$

Substitute $m=\tau/T_s$:

$$
\sigma^2(\tau) = \dfrac{R}{m} = \dfrac{R\,T_s}{\tau}
$$

Equivalently,

$$
\sigma(\tau) = \sqrt{\dfrac{RT_s}{\tau}}
$$

So on a log–log Allan plot the white measurement noise region appears as a straight line of slope $-\tfrac{1}{2}$. From the intercept $a_{\text{wn}}$ of the fit:

$$
\log_{10}\sigma(\tau) = -\tfrac12\log_{10}\tau + a_{\text{wn}},
$$

we get 

$$
R = \tfrac big(10^{a_{\text{wn}}}\big)^2 T_s
$$

---

### Random-walk bias $b_k$

Bias evolves $b_{k+1} = b_k + w_k$ with increments $w_k$ independent and $\mathrm{Var}(w_k)=qT_s$.

We want $\sigma^2(\tau)=\tfrac12\mathbb{E}[(\overline{b}_{i+1}-\overline{b}_i)^2]$ for block averages $\overline b_i$ over $m$ samples.

We need to:

* Write $b_{k}$ as cumulative sum of increments: $b_{k} = b_0 + \sum_{j=0}^{k-1} w_j$.
* Express block average $\overline b_i = \frac1m \sum_{n=0}^{m-1} b_{im+n}$ as a double sum of increments $w_j$ with triangular weights.

Then:

$$\overline b_i = \frac1m \sum_{n=0}^{m-1} (b_0 + \sum_{j=0}^{im+n-1} w_j)$, we can assume for the derivation $b_0 = 0$$

$$\overline b_i = \frac1m \sum_{n=0}^{m-1} (\sum_{j=0}^{im-1} w_j + \sum_{t=0}^{n} w_{im+t})$

$$\overline b_i = \frac1m \sum_{n=0}^{m-1} \sum_{j=0}^{im-1} w_j + \frac1m \sum_{n=0}^{m-1} \sum_{t=0}^{n} w_{im+t}$$

$$\overline b_i = \sum_{j=0}^{im-1} w_j + \frac1m \sum_{n=0}^{m-1} (m-n) w_{im+n}$$

---
### Expression for $\bar b_{i+1}-\bar b_i$

Compute similarly $\bar b_{i+1}$ and subtract:

$$
\bar b_{i+1} = \sum_{j=0}^{(i+1)m-1} w_j + \frac{1}{m}\sum_{n=0}^{m-1} (m-n)w_{(i+1)m+n}
$$

Subtract $\bar b_i$. The common sum $\sum_{j=0}^{im-1} w_j$ cancels. Collect terms:

* Terms with indices $j=im + n$ (the middle block) appear from the expansion of $\bar b_{i+1}$ as full sum and from $\bar b_i$ with coefficient $(m-n)/m$. Their net coefficient is

  $$
  1 - \frac{m-n}{m} = \frac{n}{m}
  $$
  
* Terms with indices $j=(i+1)m + n$ (the next block) appear only in $\bar b_{i+1}$ with coefficient $(m-n)/m$.

Thus

$$
\bar b_{i+1}-\bar b_i = \frac{1}{m}\sum_{n=0}^{m-1} \bigg( nw_{im+n} + (m-n)w_{(i+1)m+n}\bigg)
$$

This is a linear combination of $2m$ independent increments $w$ with known deterministic coefficients.

---

## 3) Variance of the difference (exact finite-$m$ expression)

Because the $w$'s are independent, the variance of the linear combination equals $Q$ times the sum of squared coefficients:

$$
\begin{aligned}
\mathrm{Var}(\bar b_{i+1}-\bar b_i)
&= \frac{Q}{m^2}\sum_{n=0}^{m-1} \big( n^2 + (m-n)^2 \big) \\
&= \frac{Q}{m^2}\Big( \sum_{n=0}^{m-1} n^2 + \sum_{n=0}^{m-1} (m-n)^2 \Big)
\end{aligned}
$$

Evaluate the sums. Use the known formula:

$$
\sum_{n=0}^{m-1} n^2 = \frac{(m-1)m(2m-1)}{6},\qquad
\sum_{k=1}^{m} k^2 = \frac{m(m+1)(2m+1)}{6}
$$

Noting $\sum_{n=0}^{m-1}(m-n)^2 = \sum_{k=1}^{m} k^2$, sum them:

$$
\begin{aligned}
S &= \sum_{n=0}^{m-1} n^2 + \sum_{k=1}^{m} k^2
= \frac{(m-1)m(2m-1)}{6} + \frac{m(m+1)(2m+1)}{6} \\
&= \frac{m}{6}\Big[ (m-1)(2m-1) + (m+1)(2m+1)\Big] \\
&= \frac{m}{6}\Big[(2m^2-3m+1) + (2m^2+3m+1)\Big] \\
&= \frac{m}{6}(4m^2 + 2) \;=\; \frac{m(2m^2+1)}{3}.
\end{aligned}
$$

Therefore

$$
\mathrm{Var}(\bar b_{i+1}-\bar b_i)
= \frac{Q}{m^2}\cdot \frac{m(2m^2+1)}{3}
= Q\,\frac{2m^2+1}{3m}.
$$

---

---

## 4) Allan variance (exact discrete expression)

Recall Allan variance is one half of the expected squared difference:

$$
\boxed{\;
\sigma^2(\tau) \;=\; \tfrac12\operatorname{Var}(\bar b_{i+1}-\bar b_i)
\;=\; \frac{Q}{2}\cdot\frac{2m^2+1}{3m}
\;=\; Q\,\frac{2m^2+1}{6m}.
\;}
$$

Replace $Q=qT_s$ and $m=\tau/T_s$ to express in $\tau$ and $T_s$. Two algebraically equivalent forms are useful:

1. Expand to isolate the dominant and correction terms:

$$
\boxed{\;
\sigma^2(\tau)
\;=\; \frac{q}{3}\,\tau \;+\; \frac{q\,T_s^{2}}{6\,\tau}.
\;}
$$

(derivation: substitute $Q=qT_s$ and simplify).

2. Or as a single fraction:

$$
\sigma^2(\tau)
\;=\; \frac{6\tau\,\sigma^2(\tau)}{2\tau^2 + T_s^2}\quad\text{(rearranged when solving for }q\text{)}.
$$

The first form is very instructive: it is the exact discrete formula and clearly shows the **leading term** $(q/3)\tau$ and the **finite-sample correction** $\dfrac{qT_s^2}{6\tau}$.

---

## 5) Asymptotic (continuous / large-$m$) approximation

For $m\gg 1$ (i.e. $\tau \gg T_s$), the correction term is negligible. Then

$$
\sigma^2(\tau) \approx \frac{q}{3}\,\tau
\qquad\Longrightarrow\qquad
\sigma(\tau) \approx \sqrt{\frac{q}{3}}\,\sqrt{\tau}.
$$

So on a log–log Allan plot the random-walk region appears as a straight line of slope $+\tfrac{1}{2}$. From the intercept $a_{\text{rw}}$ of the fit

$$
\log_{10}\sigma(\tau) = \tfrac12\log_{10}\tau + a_{\text{rw}},
$$

we get (neglecting finite-sample correction)

$$
\boxed{\;q \approx 3\cdot\big(10^{a_{\text{rw}}}\big)^2.\;}
$$

This is the common practical formula used when $\tau$ is comfortably larger than $T_s$.

---
Summarazing:

* **White noise region**

  $\sigma(\tau) = \sqrt{\frac{RT_s}{\tau}}$

* **Random walk bias region**

  $\sigma(\tau) = \sqrt{\frac{q}{3}}\sqrt{\tau}$

These relationships allow estimation of $R$ and $q$ directly from logged data.

---

## ✨ Features

* 📊 Allan deviation analysis of barometric data
* 🔎 Automatic estimation of **white noise variance (R)** and **random walk intensity (q)**
* 📈 Visualization tools for ADEV curves and slope fitting
* 🧩 Modular Python implementation
* 🔌 Includes Arduino sketch for raw data acquisition via I2C/UART

---

## 👨‍💻 Authors

**Tomás Suárez, Agustín Corazza, Rodrigo Pérez**  
Mechatronics Engineering Students 
Universidad Nacional de Cuyo  
📧 suareztomasm@gmail.com
📧 corazzaagustin@gmail.com
📧 rodrigoperez2110@gmail.com

---

## 📁 Project Structure

```text
BarometricAltimeterCalibration/
├── arduino code/                    # Arduino interface for MS5611
│   ├── connection.png               # Wiring diagram (Arduino UNO ↔ GY-63)
│   ├── MS5611/                      # Arduino library (C++ .h/.cpp)
│   ├── MS5611_simple.ino            # Arduino sketch for UART streaming
│   └── ms5611-datasheet.pdf         # Sensor datasheet
├── BarometricAltimeterCalibration/  # Core Python modules
│   ├── bar_altimeter_calibration.py # Main calibration logic
│   └── utils.py                     # Helpers and data loaders
├── CalibrationTests/                # Example test scripts
├── characterization data/           # Example CSV datasets
├── characterization result images/  # Sample plots (simulated vs real)
├── characterization result data/    # CSV of computed signal characterization parameters
├── LICENSE                          # MIT License
├── README.md                        # This file
└── requirements.txt                 # Python dependencies
```

---

## 🚀 Quick Start

### 1. 📥 Clone the Repository

```bash
git clone https://github.com/tomisuarez2/BarometricAltimeterCalibration
cd BarometricAltimeterCalibration
```

### 2. 📦 Install Requirements

```bash
pip install -r requirements.txt
```

### 3. ▶️ Run Example Analysis

```bash
python -m CalibrationTests.test_signal_characerization
```

---

## 📊 Example Output

* **Allan deviation curve** with fitted slopes
* Estimated noise parameters:

 ```bash
 Barometric altimeter white measurement–noise variance [m²]: 0.00023450677604763102
 Barometric altimeter bias random–walk intensity [m²/s]: 0.0002943081206920378
 ```
* Visualization of white noise (−½ slope) and random walk (+½ slope) regions

![Allan Deviation Plot](characterization%20result%20images/allan_dev_plot.png)

![Real vs Simulated data](characterization%20result%20images/real_vs_sim.png)

---
## ⚠️ Important Note on Power Supply and Thermal Drift

During experimentation with the **GY-63 breakout module (MS5611)**, a long-term first-order thermal drift was observed in the altitude signal when powering the board at **5 V** and/or tying the **protocol selection pin** (PS) to VCC.

- **Cause:**  
  - Powering the module from 5 V engages the on-board LDO regulator, which generates heat close to the sensor package.  
  - Driving the protocol select pin (PS) to 3.3 V is unnecessary for I²C mode, since the sensor already includes internal pull-ups. This extra current path also adds heat.  
  - Both effects cause the sensor die to **continuously heat up** for several hours (≈3 h at 20 °C ambient), producing an apparent first-order drift in the altitude readings.

- **Solution:**  
  - Power the module directly at **3.3 V** (bypassing the on-board regulator).  
  - Leave the protocol select pin **unconnected** when using I²C.  

- **Result:**  
  - The sensor stabilizes much faster (≈15 min warm-up).  
  - Thermal drift is greatly reduced, and altitude readings behave as expected.

* Continuously heat up at 5 V power after 3 hours

![Temp vs Alt 5V 3h](characterization%20result%20images/temp_vs_rel_alt_5_V_3_h.png)

* Visualization of measured relative altitude vs measured ambient temperature after 15 minutes warm up (5 V vs 3.3 V)

![Temp vs Alt 5V](characterization%20result%20images/temp_vs_rel_alt_5_V.png)

![Temp vs Alt 3.3V](characterization%20result%20images/temp_vs_rel_alt_3_3_V.png)



👉 If you are using the MS5611 in long-duration experiments, make sure to power the GY-63 module correctly to avoid mistaking thermal self-heating for atmospheric effects.

---
## 📈 Input Data Format

CSV with raw magnetometer values:
```bash
h, temp
```

- h, temp: MS5611 readings
- Consistent sampling rate recommended (default Arduino code: about 80 Hz)

---

## 📟 Arduino Data Logger

The repository includes an Arduino sketch (MS5611_simple.ino) to acquire data:
- Configurable sampling frequency by means of over sampling rate paramater
- I2C communication (Wire.h)
- Data-ready timer based interruption
- UART output:
```bash
h, temp

```

👉 Install the included **MS5611 Arduino library** by copying the folder to your Arduino libraries/ directory.

### 👏 Acknowledgements

This Arduino library for sensor comunnication is based on the excellent open-source library provided by [**nichtgedacht**](https://github.com/nichtgedacht/Arduino-MS5611-Interrupt).

---

## 🔮 Future Work

* Add **calibration routines** to reduce long-term drift
* Integrate **temperature compensation**
* Compare **Allan deviation vs Kalman ML identification** methods
* Provide **real-time tools** for UAV baro-sensor integration

--

## 🤝 Contributing

Contributions are welcome!
Fork, improve, and open a pull request 🚀

(Also check out our other related projects: [ImuCalibration](https://github.com/tomisuarez2/ImuCalibration) and [MagnetometerCalibration](https://github.com/tomisuarez2/MagnetometerCalibration))


--

## 🛰️ Contact

If you have questions or want to collaborate, feel free to reach out:
**Tomás Suárez**
Mechatronics Engineering Student
📧 [suareztomasm@gmail.com](mailto:suareztomasm@gmail.com)

