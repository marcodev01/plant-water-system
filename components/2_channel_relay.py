from grove.gpio import GPIO

class TwoChannnelRelay:
    """
    [Digital GPIO]
    2-Channel Relay class for:
        2-Channel SPDT Relay (https://wiki.seeedstudio.com/Grove-2-Channel_SPDT_Relay/)

    -- A relay is an electrically operated switch --
    Note: 2-Channel SPDT Relay runs only on 5v

    GPIO mode is set on BCM

    Args:
        pin1(int): number of GPIO pin the relay switch 1 is connected
        pin2(int): number of GPIO pin the relay switch 2 is connected
    """
    def __init__(self, pin1, pin2):
        self.channel_1 = GPIO(pin1, GPIO.OUT)
        self.channel_2 = GPIO(pin2, GPIO.OUT)

    def on_channel_1(self):
        self.channel_1.write(True)

    def on_channel_2(self):
        self.channel_2.write(True)

    def off_channel_1(self):
        self.channel_1.write(False)

    def off_channel_2(self):
        self.channel_2.write(False)
