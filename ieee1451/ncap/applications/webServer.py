from functools import partial
from urllib.parse import *
import threading
import time
import base64

from http.server import BaseHTTPRequestHandler, HTTPServer
from util import *
from args import *

class Handler(BaseHTTPRequestHandler):

    def __init__(self, ncap, *args, **kwargs):

        self.ncap = ncap
        super().__init__(*args, **kwargs)

    def do_GET(self):

        print("### Web Server ###")
        
        path = urlparse(self.path).path
        parameters = parse_qs(urlparse(self.path).query)
        print("Path: " + path)

        message = None

        if(path == '/1451/Discovery/TIMDiscovery'):
            
            moduleIds = self.ncap.transducerServices.reportCommModule()

            timIds = []

            for moduleId in moduleIds:
                timIds.extend(self.ncap.transducerServices.reportTims(moduleId))

            message = str(timIds)

        elif(path == '/1451/Discovery/TransducerDiscovery'):

            timId = int(parameters['timId'][0])

            [channelIds, names] = self.ncap.transducerServices.reportChannels(timId)

            message = str([timId, channelIds, names])

        elif(path == '/1451/TransducerAccess/ReadData'):
            
            timId = int(parameters['timId'][0])
            channelId = int(parameters['channelId'][0])
            timeout = int(parameters['timeout'][0])
            samplingMode = int(parameters['SamplingMode'][0])

            transCommId = self.ncap.transducerServices.open(timId, channelId)
            transducerData = self.ncap.transducerServices.readData(transCommId, timeout, samplingMode)
            self.ncap.transducerServices.close(transCommId)

            if(transducerData != None):
                message = str([timId, channelId, Codec.argumentArray2Json(transducerData)])

        elif(path == '/1451/TransducerAccess/StartReadData'):
            # Call startReadData()
            pass
    
        elif(path == '/1451/TransducerAccess/MeasurementUpdate'):
            # Call measurementUpdate()
            pass

        elif(path == '/1451/TEDSManager/ReadTeds'):
            
            timId = int(parameters['timId'][0])
            channelId = int(parameters['channelId'][0])
            timeout = int(parameters['timeout'][0])
            TEDSType = int(parameters['TEDSType'][0])

            transCommId = self.ncap.transducerServices.open(timId, channelId) 
            tedsArgArray = self.ncap.transducerServices.readTeds(transCommId, timeout, TEDSType)
            self.ncap.transducerServices.close(transCommId)
            
            if(tedsArgArray != None):
                message = str([timId, channelId, TEDSType, Codec.argumentArray2Json(tedsArgArray)])

        elif(path == '/1451/TEDSManager/ReadRawTeds'):

            timId = int(parameters['timId'][0])
            channelId = int(parameters['channelId'][0])
            timeout = int(parameters['timeout'][0])
            TEDSType = int(parameters['TEDSType'][0])

            transCommId = self.ncap.transducerServices.open(timId, channelId)
            tedsOctetArray = self.ncap.transducerServices.readRawTeds(transCommId, timeout, TEDSType)
            self.ncap.transducerServices.close(transCommId)

            if(tedsOctetArray != None):
                message = str([timId, channelId, TEDSType, base64.standard_b64encode(tedsOctetArray).decode('utf-8')])

        elif(path == '/1451/TedsManager/UpdateTedsCache'):

            timId = int(parameters['timId'][0])
            channelId = int(parameters['channelId'][0])
            timeout = int(parameters['timeout'][0])
            TEDSType = parameters['TEDSType'][0]

            transCommId = self.ncap.transducerServices.open(timId, channelId)
            self.ncap.transducerServices.updateTedsCache(transCommId, timeout, TEDSType)
            self.ncap.transducerServices.close(transCommId)

            message = str([timId, channelId, TEDSType])
            
        elif(path == '/1451/TransducerManager/StartCommand'):
            # Call startCommand():
            pass

        elif(path == '/1451/TransducerManager/CommandComplete'):
            # Call commandComplete():
            pass

        self.send_response(200)
        self.send_header('Content-type','text')
        self.end_headers()

        if(message == None):
            message = "No information available"

        print("Response: " + message)

        self.wfile.write(bytes(message, "utf8"))


    def do_POST(self):

        print("### Web Server ###")

        path = urlparse(self.path).path
        parameters = parse_qs(urlparse(self.path).query)
        print("Path: " + path)

        message = None

        if(path == '/1451/TransducerAccess/WriteData'):
            timId = int(parameters['timId'][0])
            channelId = int(parameters['channelId'][0])
            timeout = int(parameters['timeout'][0])
            samplingMode = int(parameters['SamplingMode'][0])

            transducerData = Codec.json2ArgumentArray(parameters['transducerData'][0])

            transCommId = self.ncap.transducerServices.open(timId, channelId)
            self.ncap.transducerServices.writeData(transCommId, timeout, samplingMode, transducerData)
            self.ncap.transducerServices.close(transCommId)

            message = str([timId, channelId])

        elif(path == '/1451/TransducerAccess/StartWriteData'):
            # Call startWriteData()
            pass

        elif(path == '/1451/TEDSManager/WriteTeds'):
            
            timId = int(parameters['timId'][0])
            channelId = int(parameters['channelId'][0])
            timeout = int(parameters['timeout'][0])
            TEDSType = int(parameters['tedsType'][0])
            
            tedsArgArray = Codec.json2ArgumentArray(parameters['teds'][0]) 

            transCommId = self.ncap.transducerServices.open(timId, channelId)
            self.ncap.transducerServices.writeTeds(transCommId, timeout, TEDSType, tedsArgArray)
            self.ncap.transducerServices.close(transCommId)

            message = str([timId, channelId, TEDSType])

        elif(path == '/1451/TEDSManager/WriteRawTeds'):
            
            timId = int(parameters['timId'][0])
            channelId = int(parameters['channelId'][0])
            timeout = int(parameters['timeout'][0])
            TEDSType = int(parameters['tedsType'][0])

            rawTEDS = base64.standard_b64decode(parameters['rawTEDS'][0].encode('utf-8'))

            transCommId = self.ncap.transducerServices.open(timId, channelId)
            self.ncap.transducerServices.writeRawTeds(transCommId, timeout, TEDSType, rawTEDS)
            self.ncap.transducerServices.close(transCommId)

            message = str([timId, channelId, TEDSType])

        elif(path == '/1451/TransducerManager/SendCommand'):
            # Call sendCommand()
            pass

        elif(path == '/1451/TransducerManager/Trigger'):
            # Call trigger()
            pass

        elif(path == '/1451/TransducerManager/StartTrigger'):
            # Call startTrigger()
            pass
        
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        if(message == None):
            message = "No information available"

        print("Response: " + message)

        self.wfile.write(bytes(message, "utf8"))


    def log_message(self, format, *args):
        return


class WebServer:

    def __init__(self, ncap, address, port):

        self.ncap = ncap

        self.port = port
        self.address = address
    
    def run(self):
        print("Starting HTTP Server")
        handler = partial(Handler, self.ncap)
        self.server = HTTPServer((self.address, self.port), handler)
        self.server.serve_forever()
    
    def stop(self):
        self.server.shutdown()



class ThreadWebServer:

    def __init__(self, ncap, address, port):

        self.ncap = ncap

        self.exit_request = False
        self.address = address
        self.port = port
        self.server = WebServer(ncap, '', 8000)
    
    def run(self):
        self.exit_request = False
        self.thread = threading.Thread(target = self.thread_task, daemon = True)
        self.thread.start()

    def stop(self):
        self.exit_request = True
        if self.thread.is_alive():
            self.thread.join()
    
    def thread_task(self):
        self.server.run()
    
    def shutdown(self):
        self.server.stop()
        self.stop()


if __name__ == '__main__':

    thread = ThreadWebServer('',8000)
    thread.start()

    t1 = time.time()
    while time.time() - t1 < 10:
        time.sleep(1)
        print("1 sec")

    while True:
        pass