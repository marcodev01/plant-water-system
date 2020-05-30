import time
from components import Relay

PIN = 5
relay = Relay(PIN)


def main():
    while True:
        relay.on()
        time.sleep(2)
        relay.off()
        time.sleep(2)
    

main()
