## Sensor and Actuator Use Case

This is an example of two different sensors - Temperature and Voltage - that can control a set of LEDs to show the state of the system. If the temperature is above a max value, LED 1 turns on, and if it is below min value, LED 2 turns on. Additionally, if Voltage is above a certain max value, the LED3 turns on. This scenario was explored together with UBI (Universidade da Beira Interior) and is part of a collaboration to bring together two standards, namely IEEE1451 and IEC61499.

The file named IEEE1451.rar is the 4DIAC configuration and the function_blocks.rar are the required XML and Python code for each new function block used. The Figure bellow presents the configuration used where 4 different types of function blocks are used. 

![SensorActuatorConfiguration](https://github.com/DIGI2-FEUP/dinasore-ua/blob/master/resources/use_cases/sensor_actuator/normal_ieee.PNG)
