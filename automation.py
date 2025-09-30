from vex import *
from robot_test_lib import *

# -------- CONFIG (TUNE THESE) --------
DISTANCE_THRESHOLD = 400   # mm: detection distance (distance is 40cm, i measured)
PICKUP_APPROACH_SPEED = 30
DRIVE_SPEED = 60
GRABBING_SPEED = 50

# Gripper angles (adjust for the mechanism)
GRIP_OPEN_POS = 90
GRIP_CLOSED_POS = 0

# Travel times to reach each zone (ms, need to measure on track)
# Each rectangle advancement is 30cm, at the beginning and end it is 15 cm
TIME_TO_GREEN = 2000
TIME_TO_BLUE = 4000
TIME_TO_RED = 6000
TIME_BACK_TO_START = 6500   # time to reverse from red end all the way back

SAMPLE_COLOR_COUNT = 3

# -------- HELPERS --------
def drive(speed):
    spin_motor(motor_3, speed)
    spin_motor(motor_4, speed)

def stop_drive():
    stop_motor(motor_3)
    stop_motor(motor_4)

def open_gripper():
    spin_motor_to_position(motor_1, GRIP_OPEN_POS, GRABBING_SPEED)
    wait(300, MSEC)
    stop_motor(motor_1)

def close_gripper():
    spin_motor_to_position(motor_1, GRIP_CLOSED_POS, GRABBING_SPEED)
    wait(300, MSEC)
    stop_motor(motor_1)

def sample_color():
    counts = {"red":0,"green":0,"blue":0,"unknown":0}
    for _ in range(SAMPLE_COLOR_COUNT):
        c = str(get_color()).lower()
        if "red" in c:
            counts["red"] += 1
        elif "green" in c:
            counts["green"] += 1
        elif "blue" in c:
            counts["blue"] += 1
        else:
            counts["unknown"] += 1
        wait(100, MSEC)
    return max(counts, key=counts.get)

def approach_and_grab():
    print("Approaching cube...")
    drive(PICKUP_APPROACH_SPEED)
    while True:
        d = get_distance()
        if 0 < d <= 35:
            break
        wait(50, MSEC)
    stop_drive()
    close_gripper()
    print("Cube grabbed!")

def go_to_zone(color):
    """Drive forward the right amount of time to reach the correct zone"""
    if color == "green":
        travel = TIME_TO_GREEN
    elif color == "blue":
        travel = TIME_TO_BLUE
    elif color == "red":
        travel = TIME_TO_RED
    else:
        # if unknown, default to blue zone
        travel = TIME_TO_BLUE
    print(f"Driving to {color} zone...")
    drive(DRIVE_SPEED)
    wait(travel, MSEC)
    stop_drive()

def place_cube():
    print("Placing cube...")
    open_gripper()
    wait(500, MSEC)
    close_gripper()
    print("Cube placed!")

def return_to_start():
    print("Returning to start...")
    drive(-DRIVE_SPEED)
    wait(TIME_BACK_TO_START, MSEC)
    stop_drive()
    print("Back at start!")

# -------- MAIN LOOP --------
def autonomous_run():
    setup()
    print("Autonomous run started!")

    while True:
        dist = get_distance()
        if 0 < dist < DISTANCE_THRESHOLD:
            color = sample_color()
            print("Cube detected:", color)

            approach_and_grab()
            go_to_zone(color)
            place_cube()
            return_to_start()

        else:
            wait(100, MSEC)

if __name__ == "__main__":
    autonomous_run()
