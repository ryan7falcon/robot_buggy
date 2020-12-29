from gpiozero import DigitalInputDevice
import time
import math
from SM.SM import SM, Parallel, Wire, Cascade

# SETUP
# speed sensors
sp_left = DigitalInputDevice(pin=24, pull_up=False)
sp_right = DigitalInputDevice(pin=23, pull_up=False)


WHELL_DIAMETER = 66 # in mm
WHEEL_CIRCUMFERENCE = WHELL_DIAMETER * math.pi # circumference
SAMPLE_SIZE = 1# how many ticks to sample, there are 20 ticks in the circle
SAMPLE_DIST = (SAMPLE_SIZE * WHEEL_CIRCUMFERENCE / 20)

class RPSCalculator(SM):
    start_state = (0, 0, 0) # count, start, end
    def __init__(self):
        self.start()

    def get_next_values(self, state, inp):
        (count, start, end) = state
        rps = None

        if not count:
            start = time.time() # create start time
            # print(f'start {start}')
            count += 1
        else:
            # if accumulated enough measurements
            if count == SAMPLE_SIZE:
                end = time.time() # create end time
                # print(f'end {end}')
                delta = end - start # time taken to do a sample in seconds
                rps = round(((SAMPLE_SIZE / delta) / 20), 3) 
                count, start, end = 0, 0, 0 # reset the state
            else:
                count += 1
                # print(f'count {count}')
        return ((count, start, end), rps)

class SpeedSensorCalc(SM):
    def __init__(self):
        self.start_state = (0, 0, 0, 0) # rps, lspeed, total_dist, counter
    
    def get_next_values(self, state, inp):
        rps, lspeed, total_dist, counter = state
        
        new_counter, new_rps = inp
        if new_rps:
            rps = new_rps
            if new_counter:
                counter = new_counter
            
            lspeed = round(rps * WHEEL_CIRCUMFERENCE) # linear speed
            total_dist = counter * SAMPLE_DIST
        new_s = (rps, lspeed, total_dist, counter)
        return (new_s, new_s)

class BoolCounter(SM):
    start_state = 0
    def __init__(self):
        self.start()

    def get_next_values(self, state, inp):
        if inp is not None:
            state += 1
            return (state, state)
        return (state, None)
        
def get_sensor_calc():
    return Cascade(Cascade(RPSCalculator(), Parallel(BoolCounter(), Wire())), SpeedSensorCalc())

speed_sm_left = get_sensor_calc()
speed_sm_right = get_sensor_calc()

sp_left.when_activated = speed_sm_left.step
sp_right.when_activated = speed_sm_right.step

def SensorInput():
    return {
        'odometry': {
            'left': {
                'rps': speed_sm_left.state[1][0],
                'lspeed': speed_sm_left.state[1][1],
                'total_dist': speed_sm_left.state[1][2],
                'counter': speed_sm_left.state[1][3]
            },
            'right': {
                'rps': speed_sm_right.state[1][0],
                'lspeed': speed_sm_right.state[1][1],
                'total_dist': speed_sm_right.state[1][2],
                'counter': speed_sm_right.state[1][3]
            }
        }
    }