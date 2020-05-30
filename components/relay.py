from grove.gpio import GPIO


class Relay(GPIO): 
    '''
    Class for Relay and Relay 2 Channel
    
    Args:
        pin(int): number of digital pin the relay connected
    '''
    def __init__(self, pin):
        super(Relay, self).__init__(pin, GPIO.OUT)

    def on(self):
        self.write(1)

    def off(self):
        self.write(0)
