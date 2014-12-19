'''
This script should be run continuously as a background task with root permissions
'''

from gajActuators import *
from gajConditions import *
 


def main():
    if DayTime().IsDayTimeNow(): direction = Direction.Up
    else: direction = Direction.Down
    print('direction: %s' % direction)
    with Shutter(shutterNumber=0, name='Garden', initialState=0) as shutterGarden:
        if shutterGarden.SetStateIfNeeded(direction): time.sleep(2)
    with Shutter(shutterNumber=1, name='FrontSingle', initialState=0) as shutterFrontSingle:
        if shutterFrontSingle.SetStateIfNeeded(direction): time.sleep(2)
    with Shutter(shutterNumber=2, name='FrontDouble', initialState=0) as shutterFrontLarge:
        shutterFrontLarge.SetStateIfNeeded(direction)

    #time.sleep(300) # 5 minutes    
    print("is home: %s" % Owner().IsHome())

if __name__ == '__main__':
    main()