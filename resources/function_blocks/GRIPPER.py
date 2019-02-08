import time
#import RPi.GPIO as GPIO


class SharedResources:

    def __init__(self):
        pin = 7
        freq = 50  # 50 Hz
        pos = 11  # initial duty cycle, position maximum open
        # GPIO.setmode(GPIO.BOARD)
        # GPIO.setup(pin, GPIO.OUT)
        # self.p = GPIO.PWM(pin, freq)
        # self.p.start(pos)  # initiate as open
        time.sleep(0.2)

    def open_gripper(self):
        print("start open")
        dc_open = 5  # duty cycle for gripper totally open
        # self.p.ChangeDutyCycle(dc_open)
        time.sleep(0.1)

    def close_gripper(self):
        print("start close")
        dc_close = 11  # duty cycle for gripper totally closed
        # self.p.ChangeDutyCycle(dc_close)
        time.sleep(0.1)

    def reset_gripper(self):
        print('reset gripper')
        # self.p.stop()


class GRIPPER:
    resources = SharedResources()

    def schedule(self, event_name, event_value, OPE):
        if event_name == 'REQ':
            if OPE == 1:
                self.resources.open_gripper()
            elif OPE == 2:
                self.resources.close_gripper()
            elif OPE == 3:
                self.resources.reset_gripper()

            return [event_value]
