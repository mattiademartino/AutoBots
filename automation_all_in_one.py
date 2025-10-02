# automation.py
from vex import *
import time

brain = Brain()

# PARAMETERS
DISTANCE_THRESHOLD = 300   # mm
DRIVE_SPEED = 40 # maybe more?
GRAB_SPEED = 60 # maybe less?
SLOT_DISTANCE_DEGREES = 360 # needs to be measured, how many rolls is each "cube" on the field
RETURN_SPEED = 40
MAX_RETRIES = 2

# PORTS
motor_gripper = Motor(Ports.PORT6)
motor_ejecter = Motor(Ports.PORT7)
motor_trolley = Motor(Ports.PORT8)
distance_sensor = Distance(Ports.PORT4)
bumper_sensor = Bumper(Ports.PORT10)
optical_sensor = Optical(Ports.PORT12)

# ALL in degrees, test dummy vals, distance from 0
SLOT_BLUE_DEG = 1100
SLOT_RED_DEG = 500
SLOT_GREEN_DEG = 100
DIST_TO_HARVESTING_SITE = 1500

# ----------------- SETUP (already given) -----------------
def setup():
    global touch_sensor, optical_sensor, distance_sensor, bumper_sensor
    global motor_1, motor_2, motor_3, motor_4
    print("Init...")
    # PORTS


    try:
        touch_sensor = Touchled(SENSOR_TOUCH_PORT)
        print("TouchLED OK")
    except:
        print("TouchLED Error")






    motor_gripper.position(DEGREES)
    motor_trolley.position(DEGREES)
    motor_ejecter.position(DEGREES)






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
            return distance_sensor.object_distance(MM)
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















# # --------- Movement ---------
# def move_to_position(target_degrees, speed=DRIVE_SPEED):
#     motor_3.set_position(0, DEGREES)
#     motor_4.set_position(0, DEGREES)
#     while abs(motor_3.position(DEGREES)) < abs(target_degrees):
#         if target_degrees > 0:
#             spin_motor(motor_3, speed)
#             spin_motor(motor_4, speed)
#         else:
#             spin_motor(motor_3, -speed)
#             spin_motor(motor_4, -speed)
#     stop_motor(motor_3)
#     stop_motor(motor_4)



# --------- Gripper ---------
def grab_cube():
    print("Grabbing cube...")
    start_time = time.time()
    delta_time = 0
    success = True
    while get_distance() > 1:
        print("retrieving cube")
        print(get_distance())
        spin_motor(motor_gripper, -GRAB_SPEED)
        delta_time = time.time() - start_time
        if delta_time > 6:  # timeout after 6 seconds
            print("Timeout reached while grabbing cube.")
            if get_distance() < 20: # tbd deal with error handling
                success = True
            else:
                success = False
            break
    spin_motor(motor_gripper, 0)
    print("FINISHED GRABBING, SUCCESS:")
    print(success)
    return success
    # think about error handling ######################



def release_gripper():
    print("moving gripper all the way in front")
    start_time = 0
    delta_time = 0
    while delta_time < 4:
        spin_motor(motor_gripper, -GRAB_SPEED)
        delta_time = time.time() - start_time
    # move all the way to the maximum
    spin_motor(motor_gripper, 0)



def release_cube():
    print("Releasing cube...")
    start_time = time.time()
    delta_t = 0
    print(time.time())
    # move gripper back to allow ejecter to eject cube
    while delta_t < 2.5:
        spin_motor(motor_gripper, GRAB_SPEED)
        delta_t = time.time() - start_time
    print(time.time())
    
    stop_motor(motor_gripper)
    print("Gripper moved to end pos")
    print("ejecting cube")
    spin_motor_to_position(motor_ejecter,-500,-100)
    wait(500, MSEC)
    print("ejected cube")
    spin_motor_to_position(motor_ejecter,0,100)

def grab_with_retry():
    for attempt in range(1, MAX_RETRIES + 1):
        grab_cube()
        wait(200, MSEC)
        if get_distance() > DISTANCE_THRESHOLD:
            #print(f"Grab successful on attempt {attempt}")
            return True
        else:
            #print(f"Grab failed on attempt {attempt}, retrying...")
            release_cube()
            wait(300, MSEC)
    print("All grab attempts failed. Skipping cube.")
    return False



def return_to_start():
    print("Returning to start...")
    while not bumper_pressed():
        spin_motor(motor_3, -RETURN_SPEED)
        spin_motor(motor_4, -RETURN_SPEED)
    stop_motor(motor_3)
    stop_motor(motor_4)

# --------- Sorting ---------
def place_cube(color, absolute_pos):
    print("Placing cube:")
    print(color)
    if color == "green":
        spin_motor_to_position(motor_trolley, -SLOT_GREEN_DEG, 100)
    elif color == "red":
        spin_motor_to_position(motor_trolley, -SLOT_RED_DEG, 100)
    elif color == "blue":
        spin_motor_to_position(motor_trolley, -SLOT_BLUE_DEG, 100)
        print("Dropping cube into trash chute")
    release_cube()
    wait(300, MSEC)

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


# --------- Autonomous ---------
def autonomous_run():
    
    setup()
    print("System ready")

    # start from centered at base, arm fully extended
    absolute_pos = DIST_TO_HARVESTING_SITE
    start_time_run = time.time()
    passed_time = 0
    while passed_time < 600: # tbd more discrete timing
        spin_motor_to_position(motor_trolley, -absolute_pos, 100) # move to mining area
        print("spinned_motor to first pos")
        mov_step = 50
        # look for cube
        print("checking for cube...")


        while True: # add break point
            spin_motor_to_position(motor_trolley, -absolute_pos - mov_step, 10)

            dist = get_distance()
            print("Distance: ")

            print(dist)
            absolute_pos += mov_step
            if 0 < dist < DISTANCE_THRESHOLD:
                break

        # move distance so cube is centered
        spin_motor_to_position(motor_trolley, -absolute_pos - 180, 100)


        # cube detected, retrieve it
        if grab_cube(): # success
            # get color
            print("cube aligned with cart")
            
            color = get_color()
            if color == "none":
                print("no color detected")

            #print(f"Cube detected, color: {color}, Distance: {dist}mm")
            place_cube(color, absolute_pos)

        else: # failed
            print("Failed to grab cube, aborting mission.")
        
        while not bumper_pressed():
            spin_motor(motor_trolley,50)
        motor_trolley.set_position(0, DEGREES)
        passed_time = time.time() - start_time_run

        # # move to sorting facility
        # spin_motor_to_position(motor_trolley, DIST_TO_HARVESTING_SITE-1000,100)
        

            #     color = get_color()
            #     print(f"Cube detected, color: {color}, Distance: {dist}cm")
            #     if grab_with_retry():
            #         return_to_start()
            #         place_cube(color)
            #         return_to_start()
            #     else:
            #         print("Skipping cube after failed grabs.")
            # else:
            #     spin_motor(motor_3, DRIVE_SPEED)
            #     spin_motor(motor_4, DRIVE_SPEED)
            #     wait(100, MSEC)


autonomous_run()
