import xml.etree.ElementTree as ETree
from threading import Event
import sys
import os
import serial
import time


class RobotCommunication:
    MIN_SERVO = 500
    MAX_SERVO = 2500

    def __init__(self):
        self.ser = None

    def open_connection(self, port_name):
        self.ser = serial.Serial(port=port_name,
                                 baudrate=9600,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 bytesize=serial.EIGHTBITS)

    def disconnect(self):
        self.ser.write('#0P0#1P0#2P0#3P0#4P0\r'.encode(encoding='utf-8'))
        self.ser.close()

    def send_2_init(self):
        self.send_command(1500, 1500, 1500, 1500, 1500, 1000)

    def send_command(self, base, shoulder, elbow, wrist, gripper, time2sleep):
        command = self._build_command(base, shoulder, elbow, wrist, gripper, time2sleep)
        self.ser.write(command.encode(encoding='utf-8'))

        time.sleep(time2sleep / 1000)

    def _build_command(self, base, shoulder, elbow, wrist, gripper, time2sleep):
        message = ''

        if (base >= self.MIN_SERVO) and (base <= self.MAX_SERVO):
            message = message + '#0P{0}'.format(base)
        if (shoulder >= self.MIN_SERVO) and (shoulder <= self.MAX_SERVO):
            message = message + '#1P{0}'.format(shoulder)
        if (elbow >= self.MIN_SERVO) and (elbow <= self.MAX_SERVO):
            message = message + '#2P{0}'.format(elbow)
        if (wrist >= self.MIN_SERVO) and (wrist <= self.MAX_SERVO):
            message = message + '#3P{0}'.format(wrist)
        if (gripper >= self.MIN_SERVO) and (gripper <= self.MAX_SERVO):
            message = message + '#4P{0}'.format(gripper)
        if time2sleep > 0:
            message = message + 'T{0}\r'.format(time2sleep)
        else:
            message = message + 'T500\r'

        return message

    @staticmethod
    def read_configuration(config_name):
        moves = dict()
        sequence_list = []
        # Gets the file path to the configuration file
        config_path = os.path.join(os.path.dirname(sys.path[0]),
                                   'resources',
                                   'function_blocks',
                                   'arm_config',
                                   config_name + '.xml')
        tree = ETree.parse(config_path)
        # Gets the root element
        root = tree.getroot()
        for info in root:
            if info.tag == 'Position':
                moves[info.attrib['Name']] = [info.attrib['Base'],
                                              info.attrib['Shoulder'],
                                              info.attrib['Elbow'],
                                              info.attrib['Wrist'],
                                              info.attrib['Gripper'],
                                              info.attrib['Time']]

            elif info.tag == 'Sequences':
                for sequence in info:
                    if sequence.tag == 'Sequence':
                        sequence_list.append(sequence.attrib['position_name'])

        return moves, sequence_list


class ARM_COMM:
    comm = RobotCommunication()

    def __init__(self):
        self.is_stopped = Event()
        self.sequence_index = 0
        self.moves = None
        self.sequence_list = None

    def __del__(self):
        try:
            self.comm.disconnect()
        except serial.SerialException:
            pass

    def schedule(self, event_name, event_value, serial_port, file_name):
        # INPUT VARIABLES
        # PORT - serial port to communicate with the robotic arm
        # F_NAME - file name of the configuration with the sequence of moves

        # OUTPUT EVENTS
        # INIT_O - init output
        # MOVE_END - movement ended

        # OUTPUT VARIABLES
        # STATE - actual state

        if event_name == 'INIT':
            self.comm.open_connection(serial_port)
            self.comm.send_2_init()
            self.moves, self.sequence_list = self.comm.read_configuration(file_name)
            self.is_stopped.clear()
            return [event_value, None, 0]

        elif event_name == 'MOVE':
            if not self.is_stopped.is_set():
                # restarts the cycle
                if self.sequence_index == len(self.sequence_list):
                    self.sequence_index = 0

                actual_move = self.sequence_list[self.sequence_index]
                self.comm.send_command(int(self.moves[actual_move][0]),
                                       int(self.moves[actual_move][1]),
                                       int(self.moves[actual_move][2]),
                                       int(self.moves[actual_move][3]),
                                       int(self.moves[actual_move][4]),
                                       int(self.moves[actual_move][5]))
                self.sequence_index += 1
                return [None, event_value, 0]

            else:
                # returns no events because is already stopped
                return [None, None, 1]

        elif event_name == 'STOP':
            self.is_stopped.set()
            return [None, None, 1]

        elif event_name == 'CONTINUE':
            self.is_stopped.clear()
            return self.schedule('MOVE', event_value, serial_port, file_name)


# arm = ARM_COMM()
# arm.schedule('INIT', 1, '/dev/ttyUSB0', 'sequence_1')
# arm.schedule('MOVE', 1, '/dev/ttyUSB0', 'sequence_1')
# arm.schedule('MOVE', 1, '/dev/ttyUSB0', 'sequence_1')
# arm.schedule('STOP', 1, '/dev/ttyUSB0', 'sequence_1')
# print('stopped')
# time.sleep(3)
# arm.schedule('CONTINUE', 1, '/dev/ttyUSB0', 'sequence_1')
# arm.schedule('MOVE', 1, '/dev/ttyUSB0', 'sequence_1')
# arm.schedule('MOVE', 1, '/dev/ttyUSB0', 'sequence_1')
# arm.schedule('MOVE', 1, '/dev/ttyUSB0', 'sequence_1')

# for i in range(16):
#     arm.schedule('MOVE', 1, '/dev/ttyUSB0', 'sequence_1')

