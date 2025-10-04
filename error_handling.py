## in this file, i have put together some functions that
# serve as alternatives to the ones we currently have, hope it helps..

# Questions:

# - how do we measure the distance to the dump slots, considering the real
# course will be longer than it is now? perhaps some clarification is needed

# some set in stone helper functions

def smooth_distance(samples=4, delay=0.05):
    # i tried a similar thing for the color but for distance for better reading
    vals = []
    for _ in range(samples):
        d = get_distance()
        if 0 < d < 1000:
            vals.append(d)
        time.sleep(delay)
    return sum(vals)/len(vals) if vals else -1

def has_cube(threshold=40):
    # is the cube inside the gripper?
    d = smooth_distance()
    return 0 < d < threshold

def safe_stop_all():
    # stops all critical motors
    stop_motor(motor_gripper)
    stop_motor(motor_trolley)
    stop_motor(motor_ejecter)

def grab_cube(max_retries=2, timeout=6):
    """
    grabs -> not successful -> retries -> recovers
    how it notices this: timeout or no reduction in distance sensor
    """

    print("starting grab")
    for attempt in range(1, max_retries + 1):
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
            print(f"cube successfully grabbed at attempt {attempt})")
            set_led("green")
            return True

        print(f"attempt {attempt} failed, retry")
        release_gripper()
        wait_safe(0.5)

    print("all attempts faield, skipping cube")
    set_led("red")
    safe_stop_all()
    return False


## if cube dropppeed during transport

def monitor_transport(expected_min_dist=15, check_interval=0.2):
    # continuously checking if cube is still present during transport
    # if dropped (distance suddenly >>), attempts recovery

    print("monitoring cube")
    last_ok = time.time()
    while True:
        d = get_distance()
        if d == -1: # i'm not sure if -1 can be an output of get_distance, need to verify
            continue
        if d > 200:
            print("cube dropped during movement")
            set_led("yellow")
            handle_cube_drop()
            return False

        if 0 < d < expected_min_dist:
            last_ok = time.time()
        time.sleep(check_interval)


def handle_cube_drop():
    """
    handles cube drop: stops movement, backs up, retries once
    """
    print("handling dropped cube")
    safe_stop_all()
    spin_motor(motor_trolley, -RETURN_SPEED)
    wait_safe(0.7)
    stop_motor(motor_trolley)
    release_gripper()
    open_thumb()
    set_led("blue")
    print("recovery successful") # do we need to check again if it's successful?

# sensor fail ?

def check_sensor():
    # runs basic checks for both sensors

    dist = get_distance()
    color = get_color()

    if dist < 0 or dist > 2000:
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
    print(f"reinitializing {sensor_type} sensor...")
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
                set_led("green")
                return True

    except Exception as e:
        print(f"[recovery] reinit failed: {e}")

    print(f"{sensor_type} sensor still offline")
    set_led("red")
    return False


# machine not moving on the track (stuck somewhere)

def detect_trolley_stall(speed_threshold=2, timeout=5):
 
    start = time.time()
    try:
        while time.time() - start < timeout:
            vel = abs(motor_trolley.velocity(0.99)) # i think vex has a velocity function but im unsure if the percentage is in percent units or decimal...
            if vel < speed_threshold:
                print("possible jam")
                handle_trolley_stuck()
                return True
            time.sleep(0.1)
    except:
        pass
    return False

def handle_trolley_stuck():
    # recovery process: stop -> reverse slightly -> retry
    print("trolley jam detected")
    set_led("white")
    stop_motor(motor_trolley)
    spin_motor(motor_trolley, -30)
    wait_safe(0.5)
    stop_motor(motor_trolley)
    spin_motor(motor_trolley, 30)
    wait_safe(0.5)
    stop_motor(motor_trolley)
    print("trolley movement restored")
    set_led("green")

# cube ejector stuck

def safe_release_cube():
    """
    ensures proper release: opens thumb -> ejects -> verifies cube gone?
    """
    set_led("blue")

    open_thumb()
    wait_safe(0.3)
    spin_motor_to_position(motor_ejecter, -500, 80)
    wait_safe(0.3)
    spin_motor_to_position(motor_ejecter, 0, 80)
    wait_safe(0.3)

    # Verify if cube still present
    if has_cube():
        print("cube still detected - retrying eject")
        spin_motor_to_position(motor_ejecter, -600, 90)
        wait_safe(0.3)
        spin_motor_to_position(motor_ejecter, 0, 90)

        if has_cube():
            print("ejecter jam persists")
            set_led("red")
            safe_stop_all()
            return False
    print("cube released successfully")
    set_led("green")
    return True