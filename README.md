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

  $$
  b_{k+1} = b_k + w_k,\quad w_k \sim \mathcal{N}(0,\,qT_s)
  $$

* **Measurement equation**

  $$
  d_k = p_k + b_k + v_k,\quad v_k \sim \mathcal{N}(0,\,R)
  $$

where

* $d_k$ = barometric measurement (altitude),
* $p_k$ = true altitude,
* $b_k$ = bias (random walk),
* $v_k$ = white measurement noise,
* $q$ = bias random walk intensity \[m²/s],
* $R$ = measurement noise variance \[m²],
* $T_s$ = sampling period \[s].

From Allan deviation theory:

* **White noise region**

  $$
  \sigma(\tau) = \sqrt{\frac{R\,T_s}{\tau}}
  $$

* **Random walk bias region**

  $$
  \sigma(\tau) = \sqrt{\frac{q}{3}} \,\sqrt{\tau}
  $$

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

  ```
 Barometric altimeter white measurement–noise variance [m²]: 0.00023450677604763102
 Barometric altimeter bias random–walk intensity [m²/s]: 0.0002943081206920378
  ```
* Visualization of white noise (−½ slope) and random walk (+½ slope) regions

![Allan Deviation Plot](characterization%20result%20images/allan_dev_plot.png)

![Real vs Simulated data](characterization%20result%20images/real_vs_sim.png)

--

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

