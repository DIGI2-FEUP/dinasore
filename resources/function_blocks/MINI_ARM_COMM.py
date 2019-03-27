import serial
import time


class MINI_ARM_COMM:
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
        command = self.build_command(base, shoulder, elbow, wrist, gripper, time2sleep)
        self.ser.write(command.encode(encoding='utf-8'))

        time.sleep(time2sleep / 1000)

    def build_command(self, base, shoulder, elbow, wrist, gripper, time2sleep):
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


mini_comm = MINI_ARM_COMM()
mini_comm.open_connection('/dev/ttyUSB0')
mini_comm.send_2_init()
time.sleep(5)
mini_comm.disconnect()
