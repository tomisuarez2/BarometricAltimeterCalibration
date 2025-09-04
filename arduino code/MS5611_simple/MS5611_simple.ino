/*                                                                                                                                                                                                  
  MS5611 Barometric Pressure & Temperature Sensor. Simple Example
  Library derived from https://github.com/jarzebski/Arduino-MS5611
*/

#define DEBUG

#include <Wire.h>
#include <MS5611.h>

double referencePressure;

void setup () {

    Serial.begin (38400);
    Serial.println ("Initialize MS5611 Sensor");

    // Initialize MS5611 sensor. First parameter oversampling Pressure
    // Second parameter oversampling Temperature
    // Other values please see MS5611.h

    if (!ms5611.begin (MS5611_ULTRA_HIGH_RES, MS5611_STANDARD)) {
        Serial.println ("MS5611 connection failed");
        while(1);
    }

    Serial.println ("MS5611 connection succesful");

    // warm up
    int i = 0;
    while (i < 100) {
        if (ms5611.data_ready) {
            ms5611.getPressure (true);
            i++;
        }
    }

    // get reference
    i = 0;
    while (i < 100) {
        if (ms5611.data_ready) {
            referencePressure += ms5611.getPressure (true);
            i++;
        }
    }
    referencePressure = referencePressure / 100;

    pinMode (LED_BUILTIN, OUTPUT);

    Serial.println ("Selected sampling frequency:");
    Serial.println (1.0/(ms5611.delta_t*1e-6));

    /* Waiting for confirmation */
    uint8_t proceed = 0;
    while(!proceed){
      if (Serial.available() > 0) {
        proceed = 1;
      }
    }

    Serial.println ("Getting data...");
}

void loop () {

    if (ms5611.data_ready) {    // flag is interrupt trigggered (timer1) and reset by ms5611.getPressure  

        digitalWrite (LED_BUILTIN, !digitalRead (LED_BUILTIN)); // 12.5 us on, 12.5 us off if
                                                                // MS5611_ULTRA_HIGH_RES, MS5611_STANDARD 
        long realPressure = ms5611.getPressure (true);
        double Temperature = ms5611.getTemperature (true);
        double relativeAltitude = ms5611.getAltitude (realPressure, referencePressure);

        Serial.print (relativeAltitude);
        Serial.println(",");
        Serial.println (Temperature);

    }
}
