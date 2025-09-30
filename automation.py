from vex import *
from robot_test_lib import *   # <- import your sensor/motor functions

# PARAMETERS
DISTANCE_THRESHOLD = 100  # mm - if an object is closer than 100mm to the sensor, assume it is a cube
GRABBING_SPEED = 50
DRIVE_SPEED = 60

def grab_cube():
    """Pre-given function that spins the motors in a certain speed"""
    """Assuming motors 1 and 2 are on the side that grabs the box"""

    spin_motor(motor_1, GRABBING_SPEED)
    spin_motor(motor_2, GRABBING_SPEED)
    
    while True:
        if bumper_pressed():  # cube hit bumper inside intake
            break
        dist = get_distance()
        if dist > 0 and dist < 40:  # cube close inside
            break
        wait(50, MSEC)
    
    stop_motor(motor_1)
    stop_motor(motor_2)


def transport_to_facility():

    spin_motor(motor_3, DRIVE_SPEED)
    spin_motor(motor_4, DRIVE_SPEED)
    
    while not bumper_pressed():
        wait(50, MSEC)
    
    stop_motor(motor_3)
    stop_motor(motor_4)
    print("Arrived at facility!")


# cube placing mechanism is needed
def place_cube():


def return_to_start():
    """Reverse drive motors to start position"""
    print("Returning to start...")
    spin_motor(motor_3, -DRIVE_SPEED) # - drive speed pulls the cart back
    spin_motor(motor_4, -DRIVE_SPEED)
    wait(2000, MSEC) # ? how long does it take to drive along the track (back to the beginning)
    stop_motor(motor_3)
    stop_motor(motor_4)

def autonomous_run():
    setup()
    set_led("green") # green - all good

    while True:
        dist = get_distance()
        if dist > 0 and dist < DISTANCE_THRESHOLD:
            color = get_color()

            print("Cube detected, color:", color)

            grab_cube()
            transport_to_facility()
            place_cube()
            return_to_start()
        else:
            # Idle scanning
            wait(100, MSEC)


# --------------------------
if __name__ == "__main__":
    autonomous_run()
