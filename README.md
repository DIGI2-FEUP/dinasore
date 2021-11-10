![logo](https://github.com/DIGI2-FEUP/dinasore/wiki/images/logo.png)


**D**ynamic **IN**telligent **A**rchitecture for **S**oftware and M**O**dular **RE**configuration - **DINASORE** - is a distributed platform that enables reconfiguration of **Cyber-Physical System** (CPS). The DINASORE platform allows the implementation of Function Block (FB) based pipelines for sensor integration, data processing, and systems control. The FBs are implemented in Python and can be redistributed across the DINASORE nodes. The DINASORE uses the **4DIAC-IDE** as graphical user interface (GUI) implementing the **IEC61499** standards. This version is targeted to the **Industry 4.0** applications, for that, it also uses the **OPC-UA** protocol to allow communication with the other industrial components.

## Contents

* [Home Wiki](https://github.com/DIGI2-FEUP/dinasore/wiki)
* [Install](https://github.com/DIGI2-FEUP/dinasore/wiki/1.-Install)
* [Function Blocks and 4DIAC-IDE](https://github.com/DIGI2-FEUP/dinasore/wiki/2.-Function-Blocks-and-4DIAC)
* [Build new Function Blocks](https://github.com/DIGI2-FEUP/dinasore/wiki/2.1.-Build-new-Function-Blocks)
* [Function Blocks Repository](https://github.com/DIGI2-FEUP/dinasore_function_blocks)
* [OPC-UA Data Model](https://github.com/DIGI2-FEUP/dinasore/wiki/2.3.-OPC-UA-Data-Model)
* [Behavioral Anomaly Detection](https://github.com/DIGI2-FEUP/dinasore/wiki/2.2.-Behavioral-Anomaly-Detection-functionality)
* [Tutorials Resume](https://github.com/DIGI2-FEUP/dinasore/wiki/3.-Tutorials-Resume)
  * [Sensorization - "Hello World!"](https://github.com/DIGI2-FEUP/dinasore/wiki/3.1.-Hands-On:-Sensorization-"Hello-World!")
  * [Sensorization - Distributed CPS](https://github.com/DIGI2-FEUP/dinasore/wiki/3.2.-Hands-On:-Distributed-Sensorization)
  * [Optimization](https://github.com/DIGI2-FEUP/dinasore/wiki/3.3.-Hands-On:-Optimization)
  * [OPC-UA - Generating and calling methods](https://github.com/DIGI2-FEUP/dinasore/wiki/3.4.-Hands-On:-OPC-UA-Generating-and-calling-methods)

<!---
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
 -->

## Other Resources

* [Medium Article](https://medium.com/@jrffmatias/dinasore-a-tool-for-distributed-function-block-based-systems-f2613a37e1ca)
* [DIGI2 Summer Intership Youtube Presentation](https://www.youtube.com/watch?v=OXgMPQflZSA&t=45s)
* [SAM IoT Paper](http://ceur-ws.org/Vol-2739/paper_9.pdf)
* [SAM IoT Presentation](https://events.eclipse.org/2020/sam-iot/presentations/M1-Presentation.pdf)
* [SAM IoT Youtube Presentation](https://www.youtube.com/watch?v=wiOu3vu0_tk)

## Citations

Please use the following citation, or the BibTex entry (if you are using LaTex) for citation purposes:

- E. Pereira, J. Reis, and G. Gonçalves, “DINASORE: A Dynamic Intelligent Reconfiguration Tool for Cyber-Physical Production Systems,” in Eclipse Conference on Security, Artificial Intelligence, and Modeling for the Next Generation Internet of Things (Eclipse SAM IoT), 2020, pp. 63–71, [Online]. Available: http://ceur-ws.org/Vol-2739/#paper_9.

```
@inproceedings{pereira2020dinasore,
    title = {DINASORE: A Dynamic Intelligent Reconfiguration Tool for Cyber-Physical Production Systems},
    author={Pereira, Eliseu and Reis, Joao and Gon{\c{c}}alves, Gil},
    booktitle={Eclipse Conference on Security, Artificial Intelligence, and Modeling for the Next Generation Internet of Things (Eclipse SAM IoT)},
    year={2020},
    pages = {63--71},
    url = {http://ceur-ws.org/Vol-2739/#paper_9}
}
```
