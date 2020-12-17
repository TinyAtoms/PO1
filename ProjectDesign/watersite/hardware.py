import random

def getwaterlevel():
    print("Simulated distance sensor")
    return random.randint(1, 20)

def activate_relay(group, time):
    print("simulated relay activation", group, time)
    pass