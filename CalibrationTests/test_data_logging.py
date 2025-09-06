"""
Barometric Altimeter logging data test
Authors: Tomás Suárez, Agustín Corazza, Rodrigo Pérez
University: Universidad Nacional de Cuyo
For this example we use an arduino UNO connected with a GY-63 barometer module, containing a MS5611 barometer, as indicated in "connection.png" with 
"MS5611_simple.ino" code, both found in "arduiono code" folder.
"""

from BarometricAltimeterCalibrationModules.utils import log_data_from_barometric_altimeter

file_name = log_data_from_barometric_altimeter('COM7', 38400, t_log=3600*3) # Signal characterization data log
print(f"\nData has been saved in the following file: {file_name}")

