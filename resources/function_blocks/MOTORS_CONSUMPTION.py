import serial


class MOTORS_CONSUMPTION:

    def __init__(self):
        self.ser = None

    def schedule(self, event_name, event_value, port_name):
        if event_name == 'OPEN':
            self.open_channel(port_name)

            return [event_value, None,
                    None, None, None, None,
                    None, None, None, None]

        elif event_name == 'READ':
            message = self.read()
            return [None, event_value,
                    float(message[0]), float(message[1]), float(message[2]), float(message[3]),
                    float(message[4]), float(message[5]), float(message[6]), float(message[7])]

    def open_channel(self, port_name):
        self.ser = serial.Serial(port=port_name,
                                 baudrate=9600,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 bytesize=serial.EIGHTBITS)

    def read(self):
        split_str = []
        while len(split_str) != 8:
            message_bytes = self.ser.readline()
            try:
                split_str = message_bytes.decode("utf-8").split(',')
            except UnicodeDecodeError as e:
                print(e)

        return split_str

