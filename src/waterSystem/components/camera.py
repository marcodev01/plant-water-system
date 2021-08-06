from picamera import PiCamera
from datetime import datetime
import logging


camera = PiCamera()
logger = logging.getLogger('water.system')

def take_picture():
    """Take a picutre with Pi Camera and save with timestamp"""
    now = datetime.now()
    time_stamp = now.isoformat()
    camera.capture('/home/pi/Projects/plantWaterSystem/src/db/pictures/plant_image_%s.jpg' % time_stamp)
    logger.info('[-PICTURE-] Successfully took picture! Saved in /db/pictures')
