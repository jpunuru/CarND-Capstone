
import rospy
import math
from pid import PID
from lowpass import LowPassFilter

GAS_DENSITY = 2.858
ONE_MPH = 0.44704
DEBUG = False


class Controller(object):
    def __init__(self, *args, **kwargs):
        self.vehicle_mass = args[0]
        self.fuel_capacity = args[1]
        self.brake_deadband = args[2]
        self.decel_limit = args[3]
        self.accel_limit = args[4]
        self.wheel_radius = args[5]
        self.wheel_base = args[6]
        self.steer_ratio = args[7]
        self.max_lat_accel = args[8]
        self.max_steer_angle = args[9]

        self.pid_velocity = PID(0.05, 0.0, 0.01)
        self.pid_steering = PID(10.0, 0.0, 1.0)
        sample_time = 0.02 # 1.0 / 50 (hz)
        self.lowpass_velocity = LowPassFilter(self.accel_limit, sample_time)

    def control(self, *args, **kwargs):
    	""" vehicle controller
    	arguments:
    	- proposed linear velocity
    	- proposed angular velocity (radians)
    	- current linear velocity
    	- elapsed time
    	- dbw_enabled status
    	"""
        target_vel = args[0]
        target_steer = args[1]
        cur_vel = args[2]
        time_elapsed = args[3]
        dbw_enabled = args[4]

        vel_error = target_vel - cur_vel
        velocity = self.pid_velocity.step(vel_error, time_elapsed)
        if (velocity < 0.005) and (velocity > -0.005):
            velocity = 0.0
        velocity = self.lowpass_velocity.filt(velocity)

        steer_error = target_steer
        steer = self.pid_steering.step(steer_error, time_elapsed)

        if DEBUG:
        	rospy.logerr('ctrl velocity: {}'.format(velocity))
        	rospy.logerr('ctrl steer: {}'.format(steer))

        throttle = max(velocity, 0.0)
        brake = math.fabs(min(0.0, velocity)) * 10000 # TODO: tune this multiplier or find a better way...

        # Return throttle, brake, steer
        return throttle, brake, steer

    def pid_reset(self):
        self.pid_velocity.reset()
        self.pid_steering.reset()
        #self.lowpass_steering.reset()
        self.lowpass_velocity.reset()
