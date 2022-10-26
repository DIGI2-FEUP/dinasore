import xml.etree.ElementTree as ET

class FBT:

    def __init__(self):
        self.workspace = "C:/Users/diogo/Desktop/workspace"
        self.project = "DissApp"
        self.FBfolder = "Type Library/ieee1451"

        self.folderpath = self.workspace + '/' + self.project + '/' + self.FBfolder

    def createFBT(self, name, type, events_in, events_out, data_in, data_out):
        
        root = ET.Element("FBType")
        root.set('Name', name)
        root.set('OpcUa', type)

        interfaceList = ET.Element("InterfaceList")
        root.append(interfaceList)

        eventInputs = ET.Element("EventInputs")
        interfaceList.append(eventInputs)

        eventOutputs = ET.Element("EventOutputs")
        interfaceList.append(eventOutputs)
        
        inputVars = ET.Element("InputVars")
        interfaceList.append(inputVars)

        outputVars = ET.Element("OutputVars")
        interfaceList.append(outputVars)

        for x in events_in:
            event = ET.Element("Event")
            event.set('Name', x.Name)
            event.set('Type', x.Type)
            for y in x.WithVars:
                withVar = ET.Element("With")
                withVar.set('Var', y)
                event.append(withVar)
            eventInputs.append(event)

        for x in events_out:
            event = ET.Element("Event")
            event.set('Name', x.Name)
            event.set('Type', x.Type)
            for y in x.WithVars:
                withVar = ET.Element("With")
                withVar.set('Var', y)
                event.append(withVar)
            eventOutputs.append(event)

        for x in data_in:
            var = ET.Element("VarDeclaration")
            var.set('Name', x.Name)
            var.set('Type', x.Type)
            var.set('OpcUa', x.OpcUa)
            inputVars.append(var)
        
        for x in data_out:
            var = ET.Element("VarDeclaration")
            var.set('Name', x.Name)
            var.set('Type', x.Type)
            var.set('OpcUa', x.OpcUa)
            outputVars.append(var)
        
        self.filepath = self.folderpath + '/' + name + '.fbt'
        self.writeFBT(root)

    def writeFBT(self, system):
        ET.indent(system, space="\t", level=0)
        xml = (bytes('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<!DOCTYPE FBType SYSTEM "http://www.holobloc.com/xml/LibraryElement.dtd">\n', encoding='utf-8') + ET.tostring(system))
        xml = xml.decode('utf-8')
        with open(self.filepath, 'w+') as f:
            f.write(xml)

class VarDeclaration:

    def __init__(self, name, type, opcua):
        self.Name = name
        self.Type = type
        self.OpcUa = opcua

class Event:

    def __init__(self, name, type, vars_association):
        self.Name = name
        self.Type = type
        self.WithVars = vars_association


if (__name__ == '__main__'):

    events_in = [Event("INIT", "Event", ["a","b"]), Event("RUN", "Event", [])]
    events_out = [Event("INIT_O", "Event", []), Event("RUN_O", "Event", ["c", "d"])]

    vars_in = [VarDeclaration("FIRST_PIN", "INT", "VARIABLE")]
    vars_out = [VarDeclaration("TIMESTAMPS", "STRING", "VARIABLE")]

    fbt = FBT()

    fbt.createFBT("name", "tipo", events_in, events_out, vars_in, vars_out)