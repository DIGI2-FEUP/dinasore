![logo](https://github.com/DIGI2-FEUP/dinasore/wiki/images/logo.png)


**D**ynamic **IN**telligent **A**rchitecture for **S**oftware and M**O**dular **RE**configuration - **DINASORE** - is a distributed platform that runs at the fog computing level, enabling the pre-processing of data using algorithms, that are encapsulated inside modules, i.e. Function Blocks (FBs).

The principal advantage of this platform is the redistribution of the running modules across a **Cyber-Physical System** (CPS). So the user can develop their own code, in Python, and then upload it to the different DINASORE nodes in the CPS. To draw the system it's used the **4DIAC-IDE** which is according the **IEC61499** standards. This version is targeted to the **Industry4.0** applications, for that, it also uses the **OPC-UA** protocol to allow communication with the other industrial components.

## Content

* [Home Wiki](https://github.com/DIGI2-FEUP/dinasore/wiki)
* [Install](../../wiki/1.-Install)
* [Function Blocks and 4DIAC-IDE](../../wiki/2.-Function-Blocks-and-4DIAC)
* [Build new Function Blocks](../../wiki/4.-Build-new-Function-Blocks)
* [OPC-UA Data Model](../../wiki/2.3.-OPC-UA-Data-Model)
* [Behavioral Anomaly Detection](../../wiki/2.2.-Behavioral-Anomaly-Detection-functionality)
* [Tutorials Resume](../../wiki/3.-Tutorials-Resume)
  * [Sensorization - "Hello World!"](../../wiki/3.1.-Hands-On:-Sensorization-"Hello-World!")
  * [Sensorization - Distributed CPS](../../wiki/3.2.-Hands-On:-Distributed-Sensorization)
  * [Optimization](../../wiki/3.3.-Hands-On:-Optimization)

## Features
- [x] Communication between the DINASORE and the 4DIAC-IDE 
- [x] Encapsulation of a function block inside the DINASORE
- [x] Execution of multiple function blocks inside the DINASORE
- [x] Distributed execution of a configuration across the network
- [x] Monitoring of all function blocks using the watch option at the 4DIAC-IDE
- [x] Remote stop of a configuration that is running
- [x] Docker integration
- [x] Opc-Ua integration
- [x] Configuration storage
- [x] Test with complex variables (lists, arrays, methods (strings))


