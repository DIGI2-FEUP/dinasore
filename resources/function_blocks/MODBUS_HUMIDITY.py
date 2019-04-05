from modbus_tk.modbus_rtu import RtuMaster
import modbus_tk.defines as cts
from modbus_tk.modbus import ModbusError
import serial
import time


class SharedResources:

    def __init__(self):
        self.master = None

    def open(self, port):
        if self.master is None:
            # ser = serial.Serial(port=port, baudrate=9600, bytesize=8, parity='E', stopbits=1)
            # self.master = RtuMaster(ser)
            # self.master.set_timeout(1)
            pass


class MODBUS_HUMIDITY:
    resources = SharedResources()

    def __init__(self):
        self.master = None

    def schedule(self, event_name, event_value, port):
        if event_name == 'INIT':
            return self.open_channel(event_value, port)

        elif event_name == 'REQ':
            return self.read_value(event_value)

    def open_channel(self, event_value, port):
        self.resources.open(port)
        return [event_value, None, 0.0]

    def read_value(self, event_value):
        humidity = 0.0
        try:
            # response = self.resources.master.execute(1, cts.READ_HOLDING_REGISTERS, 1000, 125)
            # humidity = float(response[34]) / 1000
            humidity = 0.0
            time.sleep(0.3)
        except ModbusError as exc:
            print(exc)
            print(exc.get_exception_code())

        return [None, event_value, humidity]

