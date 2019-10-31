![logo](resources/images/logo.png)

**D**ynamic **IN**telligent **A**rchitecture for **S**oftware and M**O**dular **RE**configuration - **DINASORE** - is a distributed platform that runs at the
fog computing level, enabling the pre-processing of data using algorithms, that are encapsulated inside modules (function blocks).

The principal advantage of this platform is the redistribution of the running modules across a distributed fog network. 
So the user can develop their own code, in Python, and them upload it to the different DINASORE nodes in the network.
To draw the system it's used the 4DIAC-IDE witch is according the IEC61499 standards. 

This version is targeted to the Industry4.0 applications, for that it was also used the UPC-UA protocol to allow the communication with the other industrial components.

## Content

* [Install](https://github.com/SYSTEC-FoF-FEUP/dinasore-ua/wiki/1.-Install)
* [Function Blocks and 4DIAC-IDE](https://github.com/SYSTEC-FoF-FEUP/dinasore-ua/wiki/2.-Function-Blocks-and-4DIAC)
* Tutorials
  * [Sensorization - "Hello World!"](https://github.com/SYSTEC-FoF-FEUP/dinasore-ua/wiki/3.1.-Hands-On:-Sensorization-%22Hello-World!%22)
  * [Sensorization - CPS](https://github.com/SYSTEC-FoF-FEUP/dinasore-ua/wiki/3.2.-Hands-On:-Sensorization)
  * [Optimization](https://github.com/SYSTEC-FoF-FEUP/dinasore-ua/wiki/3.3.-Hands-On:-Optimization)
* [Build new Function Blocks](https://github.com/SYSTEC-FoF-FEUP/dinasore-ua/wiki/4.-Build-new-Function-Blocks)
* Use Cases
  * [Painting Area Simulation](https://github.com/SYSTEC-FoF-FEUP/dinasore-ua/wiki/5.1.-Painting-Area-Simulation)
  * Industrial Sensorization using Modbus
  * Universal Robots and 3D printed Gripper Control
  * Anomaly Detection in a Servo Motor Robotic Arm

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
- [ ] Kill all process
- [ ] Update automatically the python and xml file (use os.stat())
- [ ] Download function blocks from 4DIAC-IDE repository
- [ ] Edit the function blocks in the 4DIAC-IDE and automatically update the code in the nodes
- [ ] Test with complex variables (lists, arrays, methods (strings))

## Project Structure

* **communication** - files that allow the communication with the 4DIAC-IDE; 
* **core** - files that run the function blocks pipeline (configuration);
* **data_model** - files responsible to store the actual configuration and make the interface between the FB pipeline and the OPC-UA model;
* **opc_ua** - files that implement some high level methods based in OPC-UA; 
* **resources** - folder that stores all the resources in the project (YOU ONLY NEED TO USE THAT FOLDER);
  * **function_blocks** - folder where are stored the function blocks (Python + XML);
    * EMB_RES.* - function block used to start the pipeline;
    * SLEEP.* - function block used to run in loop the DEVICE.SENSOR and POINT.STARTPOINT function blocks;
    * TEST...* - function blocks used for the unitary tests. 
  * data_model.xml - file where is stored the current configuration;
  * error_list.log - file that stores all the execution errors.
* **tests** - unitary test used to validate each package in the project.



