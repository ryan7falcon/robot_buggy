import robot_io.robot_io as io
from gpiozero import Robot
import time
from SM.SM import SM
from datetime import datetime

class StopSM(SM):
    def get_next_values(self, state, inp):
        return (None, io.Action)

def print_sensor_input():
    t = datetime.now()
    print(f'{io.SensorInput()}, time: {t.strftime("%X")}:{t.microsecond}')

def main():
    # setup motors
    robby = Robot(left=(10,9), right=(8,7))

    # start motors
    robby.forward()
    print_sensor_input()
    time.sleep(0.1)
    print_sensor_input()
    time.sleep(0.1)
    print_sensor_input()
    time.sleep(0.1)
    print_sensor_input()
    robby.stop()
    print_sensor_input()
    

if __name__ == '__main__':
    main()