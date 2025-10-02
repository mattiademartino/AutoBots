# automation.py
from vex import *

# PARAMETERS
DISTANCE_THRESHOLD = 400   # mm
DRIVE_SPEED = 40 # maybe more?
GRAB_SPEED = 50 # maybe less?
SLOT_DISTANCE_DEGREES = 360 # needs to be measured, how many rolls is each "cube" on the field
RETURN_SPEED = 40
MAX_RETRIES = 2

# --------- Gripper ---------
def grab_cube():
    print("Grabbing cube...")
    spin_motor(motor_1, GRAB_SPEED)
    spin_motor(motor_2, GRAB_SPEED)
    wait(500, MSEC)
    stop_motor(motor_1)
    stop_motor(motor_2)

def release_cube():
    print("Releasing cube...")
    spin_motor(motor_1, -GRAB_SPEED)
    spin_motor(motor_2, -GRAB_SPEED)
    wait(500, MSEC)
    stop_motor(motor_1)
    stop_motor(motor_2)

def grab_with_retry():
    for attempt in range(1, MAX_RETRIES + 1):
        grab_cube()
        wait(200, MSEC)
        if get_distance() > DISTANCE_THRESHOLD:
            print(f"Grab successful on attempt {attempt}")
            return True
        else:
            print(f"Grab failed on attempt {attempt}, retrying...")
            release_cube()
            wait(300, MSEC)
    print("All grab attempts failed. Skipping cube.")
    return False

# --------- Movement ---------
def move_to_position(target_degrees, speed=DRIVE_SPEED):
    motor_3.set_position(0, DEGREES)
    motor_4.set_position(0, DEGREES)
    while abs(motor_3.position(DEGREES)) < abs(target_degrees):
        if target_degrees > 0:
            spin_motor(motor_3, speed)
            spin_motor(motor_4, speed)
        else:
            spin_motor(motor_3, -speed)
            spin_motor(motor_4, -speed)
    stop_motor(motor_3)
    stop_motor(motor_4)

def return_to_start():
    print("Returning to start...")
    while not bumper_pressed():
        spin_motor(motor_3, -RETURN_SPEED)
        spin_motor(motor_4, -RETURN_SPEED)
    stop_motor(motor_3)
    stop_motor(motor_4)

# --------- Sorting ---------
def place_cube(color):
    print("Placing cube:", color)
    if color == "green":
        move_to_position(-SLOT_DISTANCE_DEGREES, 40)
    elif color == "red":
        move_to_position(SLOT_DISTANCE_DEGREES, 40)
    elif color == "blue":
        print("Dropping cube into trash chute")
    release_cube()
    wait(300, MSEC)

# --------- Autonomous ---------
def autonomous_run():
    setup()
    print("System ready")

    while True:
        dist = get_distance()
        if 0 < dist < DISTANCE_THRESHOLD:
            color = get_color()
            print(f"Cube detected, color: {color}, Distance: {dist}cm")
            if grab_with_retry():
                return_to_start()
                place_cube(color)
                return_to_start()
            else:
                print("Skipping cube after failed grabs.")
        else:
            spin_motor(motor_3, DRIVE_SPEED)
            spin_motor(motor_4, DRIVE_SPEED)
            wait(100, MSEC)
