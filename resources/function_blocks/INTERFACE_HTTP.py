from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from threading import Event
import json
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
            message = {'p_id': self.payload[0], 'time': self.payload[1]}
            self.wfile.write(bytes(json.dumps(message), "utf8"))

        elif self.path == '/inspection_result':
            # Write content as utf-8 data
            result_list = []

            if self.payload[2] != '!':
                message_list = self.payload[2].split()
                for i in range(int(len(message_list) / 4)):
                    image_obj = {'x': float(message_list[i * 4]),
                                 'y': float(message_list[i * 4 + 1]),
                                 'z': float(message_list[i * 4 + 2]),
                                 'color': message_list[i * 4 + 3]}
                    result_list.append(image_obj)

            self.wfile.write(bytes(json.dumps(result_list), "utf8"))

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
        self.payload = [0, 0, '0']

        self.init_event = Event()
        self.assembly_end = Event()
        self.stop = Event()
        self.resume = Event()
        self.move_index = 0

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
        # STOP - stops the robotic arm
        # RESUME - continue the movement of the robotic arm

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

            self.payload[0] = 0
            self.payload[1] = 0
            self.payload[2] = '0'

            self.init_event.wait()
            self.init_event.clear()
            return [event_value, None, None, None, None, self.move_index]

        # ASB - starts the assembly
        elif event_name == 'ASB':
            self.payload[0] = product_id
            self.payload[1] = process_time

            self.assembly_end.wait()

            self.payload[0] = 0
            self.payload[1] = 0
            self.payload[2] = '0'

            self.assembly_end.clear()
            # ends the assembly process
            return [None, event_value, None, None, None, self.move_index]

        # INS - sends the inspection result
        elif event_name == 'INS':
            self.payload[2] = vs_out
            # processes a new product
            return [None, None, event_value, None, None, self.move_index]

        elif event_name == 'WAIT':
            if self.stop.is_set() or self.stop_sent:
                self.resume.wait()
                self.stop.clear()
                self.resume.clear()
                self.stop_sent = False
                return [None, None, None, None, event_value, self.move_index]

            else:
                if self.move_index == 3:
                    self.move_index = 0
                self.move_index += 1

                # waits for the end of movement or the stop event
                print('waiting')
                self.stop.wait(5)
                print('end_wait')

                if self.stop.is_set():
                    # stop the movement
                    self.stop_sent = True
                    return [None, None, None, event_value, None, self.move_index]
                else:
                    # continues the movement
                    return [None, None, None, None, event_value, self.move_index]


# http_interface = INTERFACE_HTTP()
# http_interface.schedule('INIT', 1, 1, 1000, 20, '127.0.0.1', 8081)
# del http_interface

topic = "AST/AGV_ID"
message = {
    "battery_level": 12,
    "total_odometry": 120,  # km
    "partial_odometry": 11,  # cm
    "zone": "zone_id",  # zone identifier or value
    "actual_velocity": 1.3,
    "actual_state": "state_id",
    "target_state": "state_id",
    "load_state": "state_id",
    "actual_route": "route_id",
    "target_route": "route_id",
    "actual_tag": "tag_id",
    "next_tag": "tag_id",
    "direction": "direction_id",  # direction identifier or value
    "hydraulic_state": "state_id",
    "magnetic_band_front": True,  # true if magnetic band are detected by the front sensor
    "magnetic_band_back": False,  # true if magnetic band are detected by the back sensor
    "brakes_state": "state_id",
    "errors_list": [10301, 20901, 20505]  # list with the actual error codes
}
