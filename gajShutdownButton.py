import subprocess
import time
from gajResources import *
import RPi.GPIO as GPIO

ledpin = 3
switchpin = 5

GPIO.setmode(GPIO.BOARD)
GPIO.setup(ledpin, GPIO.OUT)
GPIO.setup(switchpin,GPIO.IN)

GPIO.output(ledpin,True)

ledstate = False
try:
    while True:
        input = GPIO.input(switchpin)
        if input == 0:
            print('Shutting down !')
            subprocess.call('shutdown now', shell = True)
        GPIO.output(ledpin,ledstate)
        ledstate = not ledstate
        time.sleep(1)
except:
    pass
finally:
    GPIO.output(ledpin,False)