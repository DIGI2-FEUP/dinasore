![logo](resources/images/logo.png)

**D**ynamic **IN**telligent **A**rchitecture for **S**oftware and M**O**dular **RE**configuration - **DINASORE** - is a distributed platform that runs at the
fog computing level, enabling the pre-processing of data using algorithms, that are encapsulated inside function blocks. 

## Architecture

## Features

- [x] Communication between the DINASORE and the 4DIAC-IDE 
- [x] Encapsulation of a function block inside the DINASORE
- [x] Execution of multiple function blocks inside the DINASORE
- [x] Distributed execution of a configuration (with multiple function blocks) on multiple machines across the network
- [x] Monitoring of all function blocks using the watch option at the 4DIAC-IDE
- [x] Remote stop of a configuration that is running
- [x] Docker integration

## Installation

### Docker

If you want to install the DINASORE using docker, you must use the following commands.
The first to pull the image from the docker hub and the second to run the container.

```dockerfile
docker pull systecfof/dinasore:(processor_architecture and version)

docker run --network="host" systecfof/dinasore:(processor_architecture and version) -a (ip_address) -p (port)
```

You must replace the (processor_architecture and version), (ip_address) and (port) by the respectively values.
The processor_architecture cloud be amd64 or arm. The next example shows the commands with examples of replaced values:

```dockerfile
docker pull systecfof/dinasore:amd64-0.1

docker run --network="host" systecfof/dinasore:amd64-0.1 -a 127.0.0.1 -p 61499
```

## Usage

In this section we gonna show how you develop a new function block and after that how you develop a new configuration integrating
all the functions blocks using the 4DIAC-IDE.

### Function Blocks Development

Here we gonna show how the process to develop a new function block that is compatible with the 4DIAC-IDE and the DINASORE. 

To develop a new function block first we need define the interface attributes that the function block uses. 
That interface is composed by events and variables, both of them can be inputs or outputs. 
The difference between an event and a variable is that the event triggers the execution of a certain functionality.

The following code show the definition in xml of a function block with 2 input events, 2 output events, 2 input variables and 2 output variables. 
This kind of file is a .fbt file witch represents the function block terminology.

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE FBType>
<FBType Comment="" Name="FB_EXAMPLE">
  <InterfaceList>
    <EventInputs>
      <Event Comment="" Name="EVENT_INPUT_1" Type="Event"/>
      <Event Comment="" Name="EVENT_INPUT_2" Type="Event"/>
    </EventInputs>
    <EventOutputs>
      <Event Comment="" Name="EVENT_OUTPUT_1" Type="Event"/>
      <Event Comment="" Name="EVENT_OUTPUT_2" Type="Event"/>
    </EventOutputs>
    <InputVars>
      <VarDeclaration Comment="" Name="VARIABLE_INPUT_1" Type="INT"/>
      <VarDeclaration Comment="" Name="VARIABLE_INPUT_2" Type="INT"/>
    </InputVars>
    <OutputVars>
      <VarDeclaration Comment="" Name="VARIABLE_OUTPUT_1" Type="INT"/>
      <VarDeclaration Comment="" Name="VARIABLE_OUTPUT_2" Type="INT"/>
    </OutputVars>
  </InterfaceList>
</FBType>
```

If we upload the previous file to the 4DIAC-IDE, we will see the following image as result. 
In that image we see the graphic representation of the function block, with all the interface attributes that characterise it. 

![fb](resources/images/fb.png) 

The second step to make a function block is encapsulate the code that you develop, inside the following the class.
* First you must replace the class name (FB_NAME) by your new function block type.
* Implement the state machine (inside schedule method) that checks what event was received and them execute the respective method.
* Specify the returned attributes (output_events and output_variables) according to the order specified in the definition file.
* Integrate the developed methods (if the method is shared between the function block instances put it inside the shared resources class,
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

    # Method responsible to check what event operation has to run
    # Receives as method arguments the event name, the event value and all the variables values
    def schedule(self, event_input_name, event_input_value, VARIABLE_INPUT_1, VARIABLE_INPUT_2):
        # Initialize the output events
        EVENT_OUTPUT_1 = None
        EVENT_OUTPUT_2 = None
        # Initialize the output variables
        VARIABLE_OUTPUT_1 = 0
        VARIABLE_OUTPUT_2 = 0
        # Checks what events receive
        if event_input_name == 'EVENT_INPUT_1':
            VARIABLE_OUTPUT_1 = self.resources.shared_method()
            EVENT_OUTPUT_1 = event_input_value
        elif event_input_name == 'EVENT_INPUT_2':
            VARIABLE_OUTPUT_2 = self.intern_method(VARIABLE_INPUT_1, VARIABLE_INPUT_2)
            EVENT_OUTPUT_2 = event_input_value
        # Returns all the events values and all the variable values
        # The order most be the same like the xml events/variables order
        return [EVENT_OUTPUT_1, EVENT_OUTPUT_2, VARIABLE_OUTPUT_1, VARIABLE_OUTPUT_2]

    def intern_method(self, VARIABLE_INPUT_1, VARIABLE_INPUT_2):
        print('this is an intern method')
        return  VARIABLE_INPUT_1 + VARIABLE_INPUT_2
```

#### Integrating the function block with the 4DIAC-IDE

To integrate the new function block with the 4DIAC-IDE you must copy the .fbt file to the library folder:

.../4diac-ide/typelibrary/new_folder_for_python_fb 

If you have a started project you must copy to the project library:

.../4diac-ide/workspace/project_name/new_folder_for_python_fb


### Configuration Modeling (4DIAC-IDE)

The usage of 4DIAC-IDE is shown at the following tutorials:

* [Simple Local Configuration](https://www.eclipse.org/4diac/en_help.php?helppage=html/4diacIDE/use4diacLocally.html) - 
in this page we find a simple tutorial, in this tutorial we see how to create configuration using function blocks.

* [Distributed Configuration](https://www.eclipse.org/4diac/en_help.php?helppage=html/4diacIDE/distribute4diac.html) - 
that tutorial is the continuation of the previous, in this case we use a distributed architecture.

**NOTE:** You must only use the python function blocks (inside .../4diac-ide/typelibrary/new_folder_for_python_fb and 
.../4diac-ide/workspace/project_name/new_folder_for_python_fb folders).

## Contributions


