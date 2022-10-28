from os import device_encoding
from pickle import NONE
import xml.etree.ElementTree as ET

class Diac_Util:

    def addIEEE1451Block(address, port_diac, filepath, name, tim_uuid, transducer_id, geoloc_x, geoloc_y, units):
        Diac_Util.addFunctionBlock(address, port_diac, filepath, "IEEE1451_SENSOR_CONTINUOUS_UUID", name, "", 0, 0, tim_uuid, transducer_id, geoloc_x, geoloc_y, units)


    def getRoot(filepath):
        root = ET.parse(filepath).getroot()
        return root


    def getFB(type, name, comment, x, y, tim_uuid, transducer_id):

        attributes = {'Name': name, 'Type': type, 'Comment': comment, 'x': str(x), 'y': str(y)}
        fb = ET.Element("FB", attrib=attributes)

        attributes = {'Name': "TIM_UUID", 'Value': str(tim_uuid)}
        ET.SubElement(fb, "Parameter", attrib = attributes)     
        attributes = {'Name': "TRANSDUCER_ID", 'Value': str(transducer_id)}
        ET.SubElement(fb, "Parameter", attrib = attributes)   

        return fb

    def getFBName(root, name):
        for sub in root.iter('SubAppNetwork'):
            subAppNetwork = sub

        max = -1

        for fb in subAppNetwork.iter('FB'):
            if( (name in fb.get('Name')) and ('IEEE1451' in fb.get('Type')) ):
                str_list = fb.get('Name').split('_')
                index = int(str_list[1])
                if(index > max):
                    max = index
        
        return name + "_" + str(max+1)

    def updateFBxy(root, fb_name, x, y):
        for sub in root.iter('SubAppNetwork'):
            subAppNetwork = sub

        for fb in subAppNetwork.iter('FB'):
            if( (fb_name == fb.get('Name'))):
                fb.set('x', x)
                fb.set('y', y)

    def addFB2Application(root, fb, tim_uuid, transducer_id):

        for sub in root.iter('SubAppNetwork'):
            subAppNetwork = sub

        add = True

        for f in subAppNetwork.iter('FB'):
            if(f.get('Type') == "IEEE1451_SENSOR_CONTINUOUS_UUID"):
                for param in f.iter('Parameter'):
                    if(param.get('Name') == "TIM_UUID"):
                        if(param.get('Value') == tim_uuid):
                            add = False
                    if(param.get('Name') == "TRANSDUCER_ID"):
                        if(param.get('Value') != transducer_id):
                            add = True
                            
        if(add == True):

            count = 0
            for f in subAppNetwork.iter('FB'):
                count = count + 1

            subAppNetwork.insert(count, fb)

        return root, add
    
    def addFB2Device(address, port_diac, root, fb):
        device = None

        for dev in root.iter('Device'):
            for param in dev.iter('Parameter'):
                if(param.get('Name') == "MGR_ID"):
                    add = param.get('Value')
                    break

            if((address + ":" + str(port_diac) in add)):
                device = dev
                break        
        
        if(device != None):

            for fbNet in device.iter("FBNetwork"):
                fbNetwork = fbNet              

            count = 0
            for f in fbNetwork.iter('FB'):
                count = count + 1

            fbNetwork.insert(count, fb)
        
        else:

            attributes = {'Name': "Dinasore", 'Type': "FORTE_PC", 'Comment': "", 'x': "0", 'y': "0"}
            device = ET.Element("Device", attrib=attributes)

            attributes = {'Name': "MGR_ID", 'Value': "\"" + address + ":" + str(port_diac) + "\""}
            ET.SubElement(device, "Parameter", attrib=attributes)

            attributes = {'Name': "Profile", 'Type': "STRING", 'Value': "HOLOBLOC", 'Comment': "device profile"}
            ET.SubElement(device, "Attribute", attrib=attributes)
            attributes = {'Name': "Color", 'Type': "STRING", 'Value': "179,205,35", 'Comment': "color"}
            ET.SubElement(device, "Attribute", attrib=attributes)
            
            fbNetwork = ET.Element("FBNetwork")
            fbNetwork.append(fb)
            attributes = {'Name': "EMB_RES", 'Type': "EMB_RES", 'Comment': "", 'x': "0.0", 'y': "0.0"}
            resource = ET.Element("Resource", attrib=attributes)
            resource.append(fbNetwork)

            device.append(resource)

            attributes = {'SegmentName': "Ethernet", 'CommResource': device.get('Name'), 'Comment': ""}
            link = ET.Element("Link", attrib=attributes)

            root.append(device)
            root.append(link)
            
        return [root, device.get('Name')]


    def addMapping(root, device_name, fb):
        
        for app in root.iter('Application'):
            application = app
        appName = application.get('Name')
        fbName = fb.get('Name')

        attributes = {'From': appName + "." + fbName, 'To': device_name + ".EMB_RES." + fbName}
        mapping = ET.Element("Mapping", attrib=attributes)

        root.append(mapping)

        return root


    def getConnection(source, destination):

        attributes = {'Source': source, 'Destination': destination, 'Comment': ""}
        conn = ET.Element("Connection", attrib=attributes)

        return conn

    def verifyGeoLocConnection(root, x1, y1):
        fb_subs = None
        y_subs = None

        for sub in root.iter('SubAppNetwork'):
            subAppNetwork = sub
        
        for fb in subAppNetwork.iter('FB'):

            if(fb.get('Type') == 'GEOLOC_SUBSCRIBER_SINGLE'):
                for param in fb.iter('Parameter'):
                    if(param.get('Name') == 'X'):
                        x2 = float(param.get('Value'))
                    if(param.get('Name') == 'Y'):
                        y2 = float(param.get('Value'))
                if(x1 == x2 and y1 == y2):
                    fb_subs = fb.get('Name')
                    y_subs = fb.get('y')
                    break
        
        if(fb_subs != None):

            for event in subAppNetwork.iter('EventConnections'):
                eventConnections = event
            
            for conn in eventConnections.iter('Connection'):

                if(conn.get('Destination') == fb_subs + '.RUN'):
                    fb_subs = None

        return fb_subs, y_subs

    def verifyUnitsConnection(root, units1):
        
        fb_subs = None
        y_subs = None

        for sub in root.iter('SubAppNetwork'):
            subAppNetwork = sub

        for fb in subAppNetwork.iter('FB'):

            if(fb.get('Type') == 'UNITS_SUBSCRIBER_SINGLE'):
                for param in fb.iter('Parameter'):
                    if(param.get('Name') == 'UNITS'):
                        units2 = param.get('Value').replace('\'','')
                if(units1 == units2):
                    fb_subs = fb.get('Name')
                    y_subs = fb.get('y')

                    for event in subAppNetwork.iter('EventConnections'):
                        eventConnections = event
                    
                    for conn in eventConnections.iter('Connection'):
                        if(conn.get('Destination') == fb_subs + '.RUN'):
                            fb_subs = None
                            break
                    
                    if(fb_subs != None):
                        break

        return fb_subs, y_subs

    def addConn2Application(root, event_conn, data_conn):

        for sub in root.iter('SubAppNetwork'):
            subAppNetwork = sub

        event_connections = None
        data_connections = None
        for event in subAppNetwork.iter('EventConnections'):
            event_connections = event
        for data in subAppNetwork.iter('DataConnections'):
            data_connections = data

        if(event_connections == None):
            event_connections = ET.Element("EventConnections")
            subAppNetwork.append(event_connections)
        if(data_connections == None):
            data_connections = ET.Element("DataConnections")
            subAppNetwork.append(data_connections)
        
        event_connections.append(event_conn)
        data_connections.append(data_conn)

        return root

    def addConn2Device(root, device_name, event_conn, data_conn):

        for dev in root.iter('Device'):
            if(dev.get('Name') == device_name):
                device = dev
                break

        if(device != None):

            for fbNet in device.iter("FBNetwork"):
                fbNetwork = fbNet

            event_connections = None
            data_connections = None
            for event in fbNetwork.iter('EventConnections'):
                event_connections = event
            for data in fbNetwork.iter('DataConnections'):
                data_connections = data

            if(event_connections == None):
                event_connections = ET.Element("EventConnections")
                fbNetwork.append(event_connections)
            if(data_connections == None):
                data_connections = ET.Element("DataConnections")
                fbNetwork.append(data_connections)        

            event_connections.append(event_conn)
            data_connections.append(data_conn)

        return root


    def addFunctionBlock(address, port_diac, filepath, type, name, comment, x, y, tim_uuid, transducer_id, geoloc_x, geoloc_y, units):

        root = Diac_Util.getRoot(filepath)

        fb_name = Diac_Util.getFBName(root, name)
        fb_comment = "GeoLoc: [" + str(geoloc_x) + "," + str(geoloc_y) + "]"
        
        fb = Diac_Util.getFB(type, fb_name, fb_comment, x, y, tim_uuid, transducer_id)
        root, add = Diac_Util.addFB2Application(root, fb, tim_uuid)

        if(add == True):
            [root, device_name] = Diac_Util.addFB2Device(address, port_diac, root, fb)
            root = Diac_Util.addMapping(root, device_name, fb)
        
            fb_subs_geoloc, y_geoloc = Diac_Util.verifyGeoLocConnection(root, geoloc_x, geoloc_y)
            if(fb_subs_geoloc != None):
                event_conn = Diac_Util.getConnection(fb_name + ".READ_O", fb_subs_geoloc + ".RUN")
                data_conn = Diac_Util.getConnection(fb_name + ".VALUE", fb_subs_geoloc + ".VALUE")
                root = Diac_Util.addConn2Application(root, event_conn, data_conn)
                root = Diac_Util.addConn2Device(root, device_name, event_conn, data_conn)

            fb_subs_units, y_units = Diac_Util.verifyUnitsConnection(root, units)
            if(fb_subs_units != None):
                event_conn = Diac_Util.getConnection(fb_name + ".READ_O", fb_subs_units + ".RUN")
                data_conn = Diac_Util.getConnection(fb_name + ".VALUE", fb_subs_units + ".VALUE")
                root = Diac_Util.addConn2Application(root, event_conn, data_conn)
                root = Diac_Util.addConn2Device(root, device_name, event_conn, data_conn)
            
            y_subs = "0.0"
            if(y_geoloc != None):
                y_subs = y_geoloc
            else:
                if(y_units != None):
                    y_subs = y_units

            Diac_Util.updateFBxy(root, fb_name, str(x), y_subs)

            Diac_Util.writeSystem(filepath, root)


    def removeFunctionBlock(filepath, name):
        tree = ET.parse(filepath)
        root = tree.getroot()

        for sub in root.iter('SubAppNetwork'):
            subAppNetwork = sub

        eventConnections = subAppNetwork.find('EventConnections')

        if(eventConnections != None):
            for connection in eventConnections.findall('Connection'):
                print("hey")
                source = connection.get('Source')
                destination = connection.get('Destination')
                print(source)
                print(destination)
                if(name + '.' in source or name + '.' in destination):
                    eventConnections.remove(connection)

        dataConnections = subAppNetwork.find('DataConnections')

        if(dataConnections != None):
            for connection in dataConnections.findall('Connection'):
                print("hey2")
                source = connection.get('Source')
                destination = connection.get('Destination')
                print(source)
                print(destination)
                if(name + '.' in source or name + '.' in destination):
                    dataConnections.remove(connection)

        for FB in subAppNetwork.findall('FB'):
            nameFB = FB.get('Name')
            if(nameFB == name):
                subAppNetwork.remove(FB)

        Diac_Util.writeSystem(filepath, root)

    
    def clearWorkspace(filepath):
        pass

    def writeSystem(filepath, system):
        ET.indent(system)
        xml = (bytes('<?xml version="1.0" encoding="UTF-8"?>\n', encoding='utf-8') + ET.tostring(system))
        xml = xml.decode('utf-8')

        with open(filepath, 'w+') as f:
            f.write(xml)
            f.close()

            print("- FB inserted in 4diac IDE")