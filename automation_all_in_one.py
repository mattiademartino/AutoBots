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
motor_thumb = Motor(Ports.PORT9)
distance_sensor = Distance(Ports.PORT4)
bumper_sensor = Bumper(Ports.PORT10)
optical_sensor = Optical(Ports.PORT12)
touch_sensor = Touchled(Ports.PORT11)

# ALL in degrees, test dummy vals, distance from 0
SLOT_BLUE_DEG = 950
SLOT_RED_DEG = 300
SLOT_GREEN_DEG = 100
DIST_TO_HARVESTING_SITE = 1300

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
    while get_distance() > 14:
        print("retrieving cube")
        print(get_distance())
        spin_motor(motor_gripper, -GRAB_SPEED)
        delta_time = time.time() - start_time
        time.sleep(0.07)
        if delta_time > 6:  # timeout after 6 seconds
            print("Timeout reached while grabbing cube.")
            if get_distance() < 25: # tbd deal with error handling
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
    start_time = time.time()
    delta_time = 0
    while delta_time < 2.5:
        spin_motor(motor_gripper, GRAB_SPEED)
        delta_time = time.time() - start_time
    # move all the way to the maximum
    spin_motor(motor_gripper, 0)
    print("Gripper moved to end pos")



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
    time.sleep(0.3)
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

def open_thumb():
    print("Opening thumb...")
    set_motor_torque(motor_thumb, 0)
    start_time = time.time()
    delta_time = 0
    while delta_time < 0.24:
        spin_motor(motor_thumb, 60)
        delta_time = time.time() - start_time
    spin_motor(motor_thumb, 0)


def close_thumb():

    print("Closing thumb...")
    start_time = time.time()
    delta_time = 0
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
        spin_motor_to_position(motor_trolley, -SLOT_GREEN_DEG, 100)
    elif color == "red":
        spin_motor_to_position(motor_trolley, -SLOT_RED_DEG, 100)
    elif color == "blue":
        spin_motor_to_position(motor_trolley, -SLOT_BLUE_DEG, 100)
        print("Dropping cube into trash chute")
    elif color == "none":
        print("Unknown color, placing in trash chute")
        spin_motor_to_position(motor_trolley, -SLOT_BLUE_DEG, 100)
    
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
    # start system
    setup()
    print("System ready")

    # start from centered at base, arm fully extended
    absolute_pos = DIST_TO_HARVESTING_SITE
    start_time_run = time.time()
    passed_time = 0

    while passed_time < 600: # tbd more discrete timing
        spin_motor_to_position(motor_trolley, -absolute_pos, 100) # move to mining area
        print("spinned_motor to first pos")
        mov_step = 75
        # look for cube
        print("checking for cube...")

        time_out_time = 22
        start_time_outtimer = time.time()
        d_t = 0
        success = False
        while d_t < time_out_time: # add break point
            spin_motor_to_position(motor_trolley, -absolute_pos - mov_step, 10)

            dist = get_distance()
            print("Distance: ")
            print(dist)

            absolute_pos += mov_step
            if 0 < dist < DISTANCE_THRESHOLD:
                success = True
                break
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
        spin_motor_to_position(motor_trolley, -absolute_pos - 150, 100) # old -180

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
            
            if passed_time >= 590: # stop timing
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
            close_thumb()
                
            if passed_time >= 590: # stop timing
                spin_motor(motor_trolley,0)
            
            #print(f"Cube detected, color: {color}, Distance: {dist}mm")

            place_cube(color, absolute_pos)
            set_led("off")

        else: # failed
            release_gripper()
            print("Failed to grab cube, aborting mission.")
        
        while not bumper_pressed():
            spin_motor(motor_trolley,100)
        motor_trolley.set_position(0, DEGREES)
        passed_time = time.time() - start_time_run



autonomous_run()
