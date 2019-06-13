![logo](resources/images/logo.png)

**D**ynamic **IN**telligent **A**rchitecture for **S**oftware and M**O**dular **RE**configuration - **DINASORE** - is a distributed platform that runs at the
fog computing level, enabling the pre-processing of data using algorithms, that are encapsulated inside function blocks.

The principal advantage of this platform is the redistribution of the running code over a distributed fog network. 
So the user can develop their own code, in python, and them upload it to the different dinasore nodes in the network. 

## Architecture

![distributed_arch](resources/images/iec61499Disitribution.png)

As you can see in the previous image, each dinasore node in the network is responsible of running one part of the configuration, 
so this way we're able to redistribute the data processing over all the dinasore nodes.

## Features

- [x] Communication between the DINASORE and the 4DIAC-IDE 
- [x] Encapsulation of a function block inside the DINASORE
- [x] Execution of multiple function blocks inside the DINASORE
- [x] Distributed execution of a configuration (with multiple function blocks) on multiple machines across the network
- [x] Monitoring of all function blocks using the watch option at the 4DIAC-IDE
- [x] Remote stop of a configuration that is running
- [x] Docker integration
- [ ] Opc-Ua integration
- [ ] Self-description file usage

## Installation

For the normal installation process you need to first to install the Python3.6, after that you must clone the repository.

```bash
git clone https://github.com/eliseu31/dinasore.git
```

After cloning the repository you must change to the dinasore folder:

```bash
cd dinasore/
```

And then you could run the DINASORE node with the following instruction, where the flag -a corresponds to the ip address and the flag -p corresponds to the port.

```bash
python3.6 core/main.py -a localhost -p 61499
```

### Docker

If you want to install the DINASORE using docker, you must use the following commands.
The first to pull the image from the docker hub and the second to run the container.

```bash
docker pull systecfof/dinasore:<processor_architecture>-<_release>

docker run --network="host" systecfof/dinasore:<processor_architecture>-<_release> -a <ip_address> -p <_port>
```

You must replace the <processor_architecture>, <_release>, <ip_address> and <_port> by the respectively values.
The processor_architecture cloud be amd64 or arm. The next example shows the commands with examples of replaced values:

```bash
docker pull systecfof/dinasore:amd64-0.1

docker run --network="host" systecfof/dinasore:amd64-0.1 -a 127.0.0.1 -p 61499
```

### 4DIAC-IDE

To draw the function block distributed architecture you need to use the 4DIAC-IDE, you can download him in this [link](https://www.eclipse.org/4diac/en_dow.php).

## Usage

In this section we gonna show how you develop a new function block and after that how you develop a new configuration integrating
all the functions blocks using the 4DIAC-IDE.

### Function Blocks Development

Here we gonna show how the process to develop a new function block that is compatible with the 4DIAC-IDE and the DINASORE. 

#### XML definition file

To develop a new function block first we need to define the interface attributes that the function block uses. 
That interface is composed by events and variables, both of them can be inputs or outputs. 
The difference between an event and a variable is that the event triggers the execution of a certain functionality.

The following code show the definition in xml of a function block with 2 input events, 2 output events, 2 input variables and 2 output variables. 
This kind of file is a .fbt file witch represents the function block terminology.

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE FBType>
<FBType Comment="" Name="FB_EXAMPLE">
  <SelfDiscription FBType="DEVICE.SENSOR" ID="ab3d2a3a-135a-11e9-ab14-d663bd873d93"/>
  <InterfaceList>
    <EventInputs>
      <Event Comment="" Name="E_IN1" Type="Event" OpcUa="Method">
        <With Var="VAR_IN1"/>
        <With Var="VAR_IN2"/>
      </Event>
      <Event Comment="" Name="E_IN2" Type="Event"/>
    </EventInputs>
    <EventOutputs>
      <Event Comment="" Name="E_OUT1" Type="Event"/>
      <Event Comment="" Name="E_OUT2" Type="Event"/>
    </EventOutputs>
    <InputVars>
      <VarDeclaration Comment="" Name="VAR_IN1" Type="INT" OpcUa="Subscription"/>
      <VarDeclaration Comment="" Name="VAR_IN2" Type="INT"/>
    </InputVars>
    <OutputVars>
      <VarDeclaration Comment="" Name="VAR_OUT1" Type="INT" OpcUa="Variable"/>
      <VarDeclaration Comment="" Name="VAR_OUT2" Type="INT" OpcUa="Variable"/>
    </OutputVars>
  </InterfaceList>
</FBType>
```

##### Opc-Ua/Self-description file integration

If you want to virtualize any fb using opc-ua you need to add the "SelfDiscription" tag to the function block xml.
This tag has as attributes the "FBType" witch could be a DEVICE.SENSOR, DEVICE.ACTUATOR, DEVICE.EQUIPMENT or a SERVICE.
The other attribute that you need to specify is the unique ID of that function block.

You need also to add the attribute OpcUa="Variable" inside each variable you want to virtualize.


###### Connection-Interfaces

- Device(fb) (1x1)
    - description.name: fb_name
    - description.SourceType: fb_type
    - methods: input_events
    - variables: output_variables
    - subscriptions: (context subs)

- ServiceInstance(fb) (1x1)
    - service.id: fb_name
    - service.name: fb_type
    - methods(run_method): input_events
    - subscriptions
        - context: only opc-ua
        - data: connections between fb
        - hardcoded: write a hardcoded value
    
(device_id: fb)
(service_id: service_instance_id, ...)
(service_instance_id: fb)

If we upload the previous file to the 4DIAC-IDE, we will see the following image as result. 
In that image we see the graphic representation of the function block, with all the interface attributes that characterise it. 

![fb](resources/images/fb.png)

#### Python file development

The second step to make a function block is encapsulate the code that you develop, inside the following the class.
1. First you must replace the class name (FB_NAME) by your new function block type.
2. Implement the state machine (inside schedule method) that checks what event was received and them execute the respective method.
3. Specify the returned attributes (output_events and output_variables) according to the order specified in the definition file.
4. Integrate the developed methods (if the method is shared between the function block instances put it inside the shared resources class,
otherwise put it inside the function block class).


```python
# This class contains the shared resources 
# between all the function blocks instances
class SharedResources:

    def __init__(self):
        self.shared_resource_attribute = 23
        
    def shared_method(self):
        print('this is a shared method')
        return self.shared_resource_attribute
    
# This class represents the function block    
class FB_EXAMPLE:
    # shared resources between all the instantiated objects from that class
    resources = SharedResources()
    
    def __init__(self):
        # Initialize the output variables
        self.VAR_OUT1 = 0
        self.VAR_OUT2 = 0

    # Method responsible to check what event operation has to run
    # Receives as method arguments the event name, the event value and all the variables values
    def schedule(self, event_input_name, event_input_value, VAR_IN1, VAR_IN2):
        # Checks what events receive
        if event_input_name == 'E_IN1':
            self.VAR_OUT1 = self.resources.shared_method()
            # Returns all the events values and all the variable values
            # The order most be the same like the xml events/variables order
            return [event_input_value, None, self.VAR_OUT1, self.VAR_OUT2]
            
        elif event_input_name == 'E_IN2':
            self.VAR_OUT2 = self.intern_method(VAR_IN1, VAR_IN2)
            # Returns all the events values and all the variable values
            # The order most be the same like the xml events/variables order
            return [None, event_input_value, self.VAR_OUT1, self.VAR_OUT2]

    def intern_method(self, VAR_IN1, VAR_IN2):
        print('this is an intern method')
        return  VAR_IN1 + VAR_IN2
```

#### Integrating the function block with the 4DIAC-IDE

To integrate the new function block with the 4DIAC-IDE you must copy the .fbt file to the library folder:

**.../4diac-ide/typelibrary/new_folder_for_python_fb** 

If you have a started project you must copy to the project library:

**.../4diac-ide/workspace/project_name/new_folder_for_python_fb**


### Configuration Modeling (4DIAC-IDE)

The usage of 4DIAC-IDE is shown at the following tutorials:

* [Simple Local Configuration](https://www.eclipse.org/4diac/en_help.php?helppage=html/4diacIDE/use4diacLocally.html) - 
in this page we find a simple tutorial, in this tutorial we see how to create configuration using function blocks.

* [Distributed Configuration](https://www.eclipse.org/4diac/en_help.php?helppage=html/4diacIDE/distribute4diac.html) - 
that tutorial is the continuation of the previous, in this case we use a distributed architecture.

**NOTE:** You must only use the python function blocks (inside **.../4diac-ide/typelibrary/new_folder_for_python_fb** and 
**.../4diac-ide/workspace/project_name/new_folder_for_python_fb** folders).


