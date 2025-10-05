# automation.py
from vex import *
import time

brain = Brain()

# PARAMETERS
DISTANCE_THRESHOLD = 320   # mm
DRIVE_SPEED = 40 # maybe more?
GRAB_SPEED = 60 # maybe less?
SLOT_DISTANCE_DEGREES = 360 # needs to be measured, how many rolls is each "cube" on the field
RETURN_SPEED = 40
MAX_RETRIES = 2

red_cube_ctr = 0
green_cube_ctr = 0

# PORTS
motor_gripper = Motor(Ports.PORT6)
motor_ejecter = Motor(Ports.PORT7)
motor_trolley = Motor(Ports.PORT8)
motor_thumb = Motor(Ports.PORT9)
distance_sensor = Distance(Ports.PORT4)
bumper_sensor = Bumper(Ports.PORT10)
optical_sensor = Optical(Ports.PORT12)
touch_sensor = Touchled(Ports.PORT11)

# ALL in degrees, test dummy vals, distance from 0
SLOT_BLUE_DEG = 1900
SLOT_RED_DEG = 1080
SLOT_GREEN_DEG = 420
DIST_TO_HARVESTING_SITE = 2320

# ----------------- SETUP (already given) -----------------
def setup():
    global touch_sensor, optical_sensor, distance_sensor, bumper_sensor
    global motor_1, motor_2, motor_3, motor_4
    print("Init...")
    # PORTS



    motor_gripper.position(DEGREES)
    motor_trolley.position(DEGREES)
    motor_ejecter.position(DEGREES)
    motor_thumb.position(DEGREES)






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
                print("sett backwawrd torque")
                motor.set_torque(abs(torque_percent), PERCENT)
                motor.spin(REVERSE)
            else:
                motor.stop()
        except:
            pass








# sensor fail ?

def check_sensor():
    # runs basic checks for both sensors

    dist = get_distance()
    color = get_color()

    if dist < 0:
        print("distance sensor fault")
        return recover_sensor("distance")
    if color == "none":
        return recover_sensor("color")
    return True

# tries recovery for distance and color sensor.
# if fail is detected, reinitializes the port thus renitializes the sensor
# checks again to see if it works. (this is quite hard coded but i feel like
# it should work...)
def recover_sensor(sensor_type):
    print('reinitializing sensor...')
    set_led("purple")
    time.sleep(0.2)

    try:
        if sensor_type == "distance":
            from vex import Distance, Ports
            global distance_sensor

            # reinitializing distance sensor
            distance_sensor = Distance(Ports.PORT4)
            time.sleep(0.3)

            if get_distance() > 0:
                print("distance sensor restored")
                set_led("green")
                return True

        elif sensor_type == "color":
            from vex import Optical, Ports
            global optical_sensor
            optical_sensor = Optical(Ports.PORT12)
            optical_sensor.set_light(100)
            time.sleep(0.3)

            if get_color() != "none":
                print("color sensor restored")
                #set_led("green")
                return True

    except Exception as e:
        print('[recovery] reinit failed:')

    print(' sensor still offline')
    #set_led("red")
    return False


def has_cube(threshold=40):
    # is the cube inside the gripper?
    d = get_distance()
    return 0 < d < threshold


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


def release_gripper():
    print("moving gripper all the way in front")
    start_time = time.time()
    delta_time = 0
    while delta_time < 3.5:
        spin_motor(motor_gripper, GRAB_SPEED)
        delta_time = time.time() - start_time
    # move all the way to the maximum
    
    spin_motor(motor_gripper, 0)
    set_motor_torque(motor_gripper, 80)

    print("Gripper moved to end pos")


# --------- Gripper ---------
# def grab_cube():
#     print("Grabbing cube...")
#     start_time = time.time()
#     delta_time = 0
#     success = True
#     while get_distance() > 14:
#         print("retrieving cube")
#         print(get_distance())
#         set_motor_torque(motor_gripper, 0)
#         spin_motor(motor_gripper, -GRAB_SPEED)
#         delta_time = time.time() - start_time
#         time.sleep(0.1)
#         if delta_time > 3.5:  # timeout after 6 seconds
#             print("Timeout reached while grabbing cube.")
#             if get_distance() < 25: # tbd deal with error handling
#                 success = True
#             else:
#                 success = False
#             break
#     spin_motor(motor_gripper, 0)
#     print("FINISHED GRABBING, SUCCESS:")
#     print(success)
#     return success
#     # think about error handling ######################
def grab_cube(max_retries=2, timeout=3.5):
    """
    grabs -> not successful -> retries -> recovers
    how it notices this: timeout or no reduction in distance sensor
    """

    print("starting grab")
    for attempt in range(1, max_retries + 1):
        if attempt >= max_retries:
            print("last attempt")
            spin_motor(motor_trolley,-100)
            time.sleep(0.25)
            spin_motor(motor_trolley,0)
        set_led("yellow")
        start = time.time()
        success = False

        while time.time() - start < timeout:
            dist = get_distance()
            spin_motor(motor_gripper, -GRAB_SPEED)
            if 0 < dist < 25:
                success = True
                break
            time.sleep(0.05)

        stop_motor(motor_gripper)
        if success and has_cube():
            print('cube successfully grabbed at attempt )')
            print(attempt)
            #set_led("green")
            return True

        print('attempt  failed, retry')
        print(attempt)
        release_gripper()
        time.sleep(0.2)

    print("all attempts faield, skipping cube")
    set_led("purple")
    safe_stop_all()
    return False





def release_cube():
   # print("Releasing cube...")
   # start_time = time.time()
   # delta_t = 0
   # print(time.time())
    # move gripper back to allow ejecter to eject cube
   # while delta_t < 2.5:
   #     spin_motor(motor_gripper, GRAB_SPEED)
   #     delta_t = time.time() - start_time
   # print(time.time())
    
   # stop_motor(motor_gripper)
   # print("Gripper moved to end pos")
    
    open_thumb()
    time.sleep(0.4)
    print("ejecting cube")
    spin_motor_to_position(motor_ejecter,-320,-80)
    wait(300, MSEC)
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


def open_thumb():
    print("Opening thumb...")
    #set_motor_torque(motor_thumb, 0)
    start_time = time.time()
    delta_time = 0
    while delta_time < 0.28:
        spin_motor(motor_thumb, 85)
        delta_time = time.time() - start_time
    spin_motor(motor_thumb, 0)
    set_motor_torque(motor_thumb, 90)


def close_thumb():
    print("Closing thumb...")
    start_time = time.time()
    delta_time = 0
    set_motor_torque(motor_thumb, 0)
    while delta_time < 1:
        spin_motor(motor_thumb, -100)
        delta_time = time.time() - start_time
    set_motor_torque(motor_thumb, -100)
    


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
        global green_cube_ctr
        green_cube_ctr += 1
        if green_cube_ctr >= 4:
    
            global SLOT_GREEN_DEG
            SLOT_GREEN_DEG-= 320
            green_cube_ctr = -4
        spin_motor_to_position(motor_trolley, -SLOT_GREEN_DEG, 100)
    elif color == "red":

        global red_cube_ctr
        red_cube_ctr += 1
        if red_cube_ctr >= 4:
        
            global SLOT_RED_DEG 
            SLOT_RED_DEG -= 320
            red_cube_ctr =-4
        spin_motor_to_position(motor_trolley, -SLOT_RED_DEG, 100)
    elif color == "blue":
        spin_motor_to_position(motor_trolley, -SLOT_BLUE_DEG, 100)
        print("Dropping cube into trash chute")
    elif color == "none":
        print("Unknown color, placing in trash chute")
        spin_motor_to_position(motor_trolley, -SLOT_BLUE_DEG, 100)
    
    release_cube()
    wait(300, MSEC)

def safe_stop_all():
    # stops all critical motors
    stop_motor(motor_gripper)
    stop_motor(motor_trolley)
    stop_motor(motor_ejecter)

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
def backup_error_function():
    print("###############")
    dist = get_distance()
    print(dist)
    if 17< dist <= 30:
        release_cube()
        return False
    return True
    
        # cube not there as it should be

# --------- Autonomous ---------
def autonomous_run():
    continue_run = False
    setup()
    #check_sensor()
    print("System ready")

    # start from centered at base, arm fully extended
    
    start_time_run = time.time()
    passed_time = 0

    while passed_time < 590: # tbd more discrete timing
        
        if continue_run:
            continue_run = False
            absolute_pos = absolute_pos + 60
        else:
            absolute_pos = DIST_TO_HARVESTING_SITE

        set_led("off")
        open_thumb()
        spin_motor_to_position(motor_trolley, -absolute_pos, 100) # move to mining area
        print("spinned_motor to first pos")
        mov_step = 57
        # look for cube
        print("checking for cube...")

        time_out_time = 26
        start_time_outtimer = time.time()
        d_t = 0
        success = False
        while absolute_pos < 5750: # limit of wall
            dist = get_distance()
            print("Distance: ")
            print(dist)

            if 0 < dist < DISTANCE_THRESHOLD:
                success = True
                break
            spin_motor_to_position(motor_trolley, -absolute_pos - mov_step, 100)

            absolute_pos += mov_step


            d_t = time.time() - start_time_outtimer
        if passed_time >= 590:
            spin_motor(motor_trolley,0)
            break
        if not success:
            while not bumper_pressed():
                spin_motor(motor_trolley,100)
                motor_trolley.set_position(0, DEGREES)
            continue

        # move distance so cube is centered
        spin_motor_to_position(motor_trolley, -absolute_pos - 136, 70) # old -180

        if passed_time >= 590: # stop timing
            spin_motor(motor_trolley,0)

        # cube detected, retrieve it
        if grab_cube(): # success
            # get color
            print("cube aligned with cart")
            set_color_sensor_led(True)
            time.sleep(0.2)
            color = get_color()
            print(color)
            ctr = 0
            
            if passed_time >= 592: # stop timing
                spin_motor(motor_trolley,0)
            while ctr < 5:
                color_test = get_color()
                ctr += 1
                if color_test != color:
                    ctr = 0
                print(color_test)
            color = color_test
            set_color_sensor_led(False)
            set_led(color)

            #release the gripper immediately after grabbing the cube

            release_gripper()
            if get_distance() < 32:
                close_thumb()
            else:
                open_thumb()
                break
            if passed_time >= 590: # stop timing
                spin_motor(motor_trolley,0)
            
            #print(f"Cube detected, color: {color}, Distance: {dist}mm")
            if not backup_error_function():
                continue_run = True
                continue

            place_cube(color, absolute_pos)
            set_led("off")

        else: # failed
            #release_gripper()
            print("Failed to grab cube, aborting mission.")
        
        while not bumper_pressed():
            spin_motor(motor_trolley,100)
        motor_trolley.set_position(0, DEGREES)
        passed_time = time.time() - start_time_run

    set_led("purple")
    safe_stop_all()
    ctr = 0
    while ctr < 3:
        set_led("off")
        time.sleep(0.3)
        set_led("purple")
        time.sleep(0.3)
        ctr += 1



autonomous_run()
