import random

def getwaterlevel():
    print("Simulated distance sensor")
    return random.randint(10,20)

def activate_relay(group, time):
    # waterpan = 220 mm deep
    print("simulated relay activation", group, time)
    pass