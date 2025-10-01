# robot_lib.py
from vex import *

brain = Brain()

# PORT CONFIG
SENSOR_TOUCH_PORT = Ports.PORT1
SENSOR_OPTICAL_PORT = Ports.PORT2
SENSOR_DISTANCE_PORT = Ports.PORT3
BUMPER_BUMPER_PORT = Ports.PORT4
MOTOR_1_PORT = Ports.PORT5
MOTOR_2_PORT = Ports.PORT6
MOTOR_3_PORT = Ports.PORT7
MOTOR_4_PORT = Ports.PORT8

# DEVICES
touch_sensor = None
optical_sensor = None
distance_sensor = None
bumper_sensor = None
motor_1 = None
motor_2 = None
motor_3 = None
motor_4 = None

# ----------------- SETUP -----------------
def setup():
    global touch_sensor, optical_sensor, distance_sensor, bumper_sensor
    global motor_1, motor_2, motor_3, motor_4
    print("Init...")

    try:
        touch_sensor = Touchled(SENSOR_TOUCH_PORT)
        print("TouchLED OK")
    except:
        print("TouchLED Error")

    try:
        optical_sensor = Optical(SENSOR_OPTICAL_PORT)
        print("Color OK")
    except:
        optical_sensor = None
        print("Color Error")

    try:
        distance_sensor = Distance(SENSOR_DISTANCE_PORT)
        print("Distance OK")
    except:
        distance_sensor = None
        print("Distance Error")

    try:
        bumper_sensor = Bumper(BUMPER_BUMPER_PORT)
        print("Bumper OK")
    except:
        print("Bumper Error")

    try:
        motor_1 = Motor(MOTOR_1_PORT)
        motor_1.position(DEGREES)
        print("Motor1 OK")
    except:
        motor_1 = None
        print("Motor1 Error")

    try:
        motor_2 = Motor(MOTOR_2_PORT)
        motor_2.position(DEGREES)
        print("Motor2 OK")
    except:
        motor_2 = None
        print("Motor2 Error")

    try:
        motor_3 = Motor(MOTOR_3_PORT)
        motor_3.position(DEGREES)
        print("Motor3 OK")
    except:
        motor_3 = None
        print("Motor3 Error")

    try:
        motor_4 = Motor(MOTOR_4_PORT)
        motor_4.position(DEGREES)
        print("Motor4 OK")
    except:
        motor_4 = None
        print("Motor4 Error")

# ----------------- SENSORS -----------------
def set_led(color):
    if not touch_sensor:
        return
    try:
        mapping = {
            "red": Color.RED, "green": Color.GREEN, "blue": Color.BLUE,
            "yellow": Color.YELLOW, "purple": Color.PURPLE, "white": Color.WHITE
        }
        if color == "off":
            touch_sensor.off()
        elif color in mapping:
            touch_sensor.set_color(mapping[color])
    except:
        pass

def led_pressed():
    try:
        return touch_sensor and touch_sensor.pressing()
    except:
        return False

def set_color_sensor_led(on=True):
    if optical_sensor:
        try:
            optical_sensor.set_light(100 if on else 0)
        except:
            pass

def get_color():
    if optical_sensor:
        try:
            c = optical_sensor.color()
            if c == Color.RED: return "red"
            if c == Color.GREEN: return "green"
            if c == Color.BLUE: return "blue"
        except:
            pass
    return "none"

def get_distance():
    if distance_sensor:
        try:
            return distance_sensor.object_distance(MM) / 10.0  # cm
        except:
            return -1
    return -2

def bumper_pressed():
    try:
        return bumper_sensor and bumper_sensor.pressing()
    except:
        return False

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
