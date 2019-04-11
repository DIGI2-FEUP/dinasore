from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from threading import Event
import time


class HttpHandler(BaseHTTPRequestHandler):
    payload = None
    init_event = None
    assembly_end = None
    stop = None
    resume = None

    # GET
    def do_GET(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        if self.path == '/assembly_start':
            # Write content as utf-8 data
            message = '{0} {1}'.format(self.payload[0], self.payload[1])
            self.wfile.write(bytes(message, "utf8"))

        elif self.path == '/inspection_result':
            # Write content as utf-8 data
            message = '{0}'.format(self.payload[2])
            self.wfile.write(bytes(message, "utf8"))

    def do_POST(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        if self.path == '/init':
            self.init_event.set()

        elif self.path == '/assembly_end':
            self.assembly_end.set()

        elif self.path == '/stop':
            self.stop.set()

        elif self.path == '/resume':
            if self.resume.is_set():
                self.resume.clear()
            else:
                self.resume.set()

        # content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        # post_data = self.rfile.read(content_length)  # <--- Gets the data itself


class ServerThread(Thread):

    def __init__(self, ip_address, port, payload, init_event, assembly_end, stop, resume):
        Thread.__init__(self, name='serverThread')
        HttpHandler.payload = payload
        HttpHandler.init_event = init_event
        HttpHandler.assembly_end = assembly_end
        HttpHandler.stop = stop
        HttpHandler.resume = resume

        # Choose port 8080, for port 80, which is normally used for a http server, you need root access
        server_address = (ip_address, port)
        self.httpd = HTTPServer(server_address, HttpHandler)

    def run(self):
        # Server settings
        self.httpd.serve_forever()

    def disconnect(self):
        self.httpd.shutdown()


class INTERFACE_HTTP:

    def __init__(self):
        self.server_http = None
        self.payload = [0, 0, 0]

        self.init_event = Event()
        self.assembly_end = Event()
        self.stop = Event()
        self.resume = Event()

        self.resume.set()

    def __del__(self):
        self.server_http.disconnect()

    def schedule(self, event_name, event_value, product_id, process_time, vs_out, ip_address, port):
        # INPUT VARIABLES
        # P_ID - product id (PROCESS_SC)
        # TIME - process time (PROCESS_SC)
        # VS_OUT - result from vision system inspection (PROCESS_SC)

        # OUTPUT EVENTS
        # INIT_PROCESS - starts the PROCESS_SC
        # ASB_END - ended the assembly
        # NEW_PRODUCT - sends a new product request to PROCESS_SC

        # checks if resume is activated
        self.resume.wait()

        # check if stop is activated
        if self.stop.is_set():
            self.stop.clear()
            # simulates INIT state
            self.init_event.wait()
            self.init_event.clear()
            return [event_value, None, None]

        # INIT -
        if event_name == 'INIT':
            self.server_http = ServerThread(ip_address,
                                            port,
                                            self.payload,
                                            self.init_event,
                                            self.assembly_end,
                                            self.stop,
                                            self.resume)
            self.server_http.start()
            self.init_event.wait()
            self.init_event.clear()
            return [event_value, None, None]

        # ASB - starts the assembly
        elif event_name == 'ASB':
            self.payload[0] = product_id
            self.payload[1] = process_time

            self.assembly_end.wait(process_time/1000)
            self.assembly_end.clear()
            # ends the assembly process
            return [None, event_value, None]

        # INS
        elif event_name == 'INS':
            self.payload[2] = vs_out
            # processes a new product
            return [None, None, event_value]


# http_interface = INTERFACE_HTTP()
# http_interface.schedule('INIT', 1, 1, 1000, 20, '127.0.0.1', 8081)
# del http_interface
