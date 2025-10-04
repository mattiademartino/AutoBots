from vex import *
import time

brain = Brain()
#MOTOR CONTROLLING FUNCTIONS


def spin_motor(motor, speed_percent):
    """
    Spins a motor at a certain speed and direction.
    
    Args:
        motor: The motor object to control
        speed_percent: Speed in percentage (-100 to 100). 
                      Positive values = forward, negative = reverse
    """
    if motor:
        try:
            if speed_percent > 0:
                motor.spin(FORWARD, abs(speed_percent), PERCENT)
            elif speed_percent < 0:
                motor.spin(REVERSE, abs(speed_percent), PERCENT)
            else:
                motor.stop()
        except:
            pass

def spin_motor_to_position(motor, position_degrees, speed_percent=50):
    """
    Spins a motor to a specific position.
    
    Args:
        motor: The motor object to control
        position_degrees: Target position in degrees
        speed_percent: Speed percentage (1-100, default 50)
    """
    if motor:
        try:
            motor.spin_to_position(position_degrees, DEGREES, abs(speed_percent), PERCENT)
        except:
            pass

def stop_motor(motor):
    """
    Stops a specific motor.
    
    Args:
        motor: The motor object to stop
    """
    if motor:
        try:
            motor.stop()
        except:
            pass

def set_motor_torque(motor, torque_percent):
    """
    Forces a motor to apply a certain torque.
    
    Args:
        motor: The motor object to control
        torque_percent: Torque percentage (-100 to 100).
                       Positive = forward torque, negative = reverse torque
    """
    if motor:
        try:
            if torque_percent > 0:
                motor.set_torque(abs(torque_percent), PERCENT)
                motor.spin(FORWARD)
            elif torque_percent < 0:
                motor.set_torque(abs(torque_percent), PERCENT)
                motor.spin(REVERSE)
            else:
                motor.stop()
        except:
            pass



MOTOR_1_PORT = Ports.PORT7
MOTOR_2_PORT = Ports.PORT8

# DEVICES
touch_sensor = None
optical_sensor = None
distance_sensor = None
bumper_sensor = None
motor_1 = None


motor_1 = Motor(MOTOR_1_PORT)
motor_2 = Motor(MOTOR_2_PORT)
# Test if motor is actually connected by trying to read position
#motor_1.position(DEGREES)
move_motor_1 = True
move_motor_2 = False
if move_motor_1:
    for i in range(30):
        motor_1.set_position(0, DEGREES)
        #motor_2.set_position(0,DEGREES)
        spin_motor_to_position(motor_1, -980, 40)
        #spin_motor_to_position(motor_2,80,100)
        time.sleep(0.1)
        spin_motor_to_position(motor_1, 0, 100)
        #spin_motor_to_position(motor_2,0,10)
    #while True:
        #motor_1.set_position(0, DEGREES)
        #spin_motor_to_position(motor_1, 360, 25)
    #set_motor_torque(motor_1,100)
if move_motor_2:
    rot_ctr = 0
    desired_rot_deg = 935
    while rot_ctr < desired_rot_deg:
        motor_1.set_position(0,DEGREES)
        rot_ctr += 10
        spin_motor_to_position(motor_2,-rot_ctr,100)
        print(rot_ctr)
    time.sleep(0.1)
    spin_motor_to_position(motor_2,0,100)
