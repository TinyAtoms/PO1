import random


def sense_distance():
    ms = timedelta(microseconds=1)
    GPIO.setmode(GPIO.BCM)
    trigger = 23
    echo = 24
    GPIO.setup(trigger, GPIO.OUT)
    GPIO.setup(echo, GPIO.IN)
    print("Reseting triggers")

    # reset trigger pin, and let the sensor settle
    GPIO.output(trigger, False)
    time.sleep(2)
    print("Trigger it")
    # send a 10 us pulse to the trigger pin
    GPIO.output(trigger, True)
    time.sleep(11E-3)
    GPIO.output(trigger, False)

    print("waiting for input")
    # the time we want is the total time echo = HI so we take the last timestamp
    # it was LO and the last timestamp it was HI, take the diff between them
    while GPIO.input(echo) == 0:
        pulse_start = datetime.now()
    while GPIO.input(echo) == 1:
        pulse_end = datetime.now()
    time_delta = (pulse_end - pulse_start) / (2 * ms)
    time_delta -= 0  # we need to calibrate this
    # like, 1mm is een dt van ~3us, en in deze order of magnitude zijn spelen processing shit een rol
    # distance is time in ms * speed of sound in mm/ms
    distance = time_delta * 0.343
    GPIO.cleanup()
    return distance


def getwaterlevel():
    return 220 - random.randint(150, 157)
    distance = sense_distance()
    # bottom of bucket - distance to waterlevel = distance waterbucket bottom
    return 220 - distance
    # to waterlevel


def activate_relay(group, t):
    GPIO.setmode(GPIO.BCM)
    trigger = 18
    if group in [0, 1, 2, 3, 4]:  # we'd need to specify which triggers to use
        # if we have multiple relays
        trigger = 18
    GPIO.setup(trigger, GPIO.OUT)

    # reset trigger pin, and let the sensor settle
    GPIO.output(trigger, True)
    time.sleep(t)
    GPIO.output(trigger, False)
    time.sleep(1)
    GPIO.cleanup()
