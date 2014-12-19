'''
This script should be run continuously as a background task with root permissions
'''

from gajActuators import *
from gajConditions import *
 


def main():
    # define conditions
    ih = Owner().IsHome()
    print("is home: %s" % ih)

    tnw = datetime.datetime.now().time()

    dtn = DayTime().IsDayTimeNow()
    print("is daytime: %s" % dtn)

    if dtn: direction = Direction.Up
    else: direction = Direction.Down
    print('direction: %s' % direction)
    
    
    # socket actions
    if ih and not dtn and (tnw > datetime.time(16, 0, 0) or tnw < datetime.time(3, 0, 0)): lampDesiredState = Power.On
    else: lampDesiredState = Power.Off
    print('lamp state: %s' % lampDesiredState)
    
    with Socket(name = 'Lampe', socketNumber = 1) as lp:
        if lp.SetStateIfNeeded(lampDesiredState): time.sleep(2)
    
    
    
    # shutter actions
    with Shutter(shutterNumber=1, name='FrontSingle', initialState=0) as shutterFrontSingle:
        if shutterFrontSingle.SetStateIfNeeded(direction): time.sleep(2)
        
    with Shutter(shutterNumber=2, name='FrontDouble', initialState=0) as shutterFrontLarge:
        if shutterFrontLarge.SetStateIfNeeded(direction): time.sleep(60)

    with Shutter(shutterNumber=0, name='Garden', initialState=0) as shutterGarden:
        if shutterGarden.SetStateIfNeeded(direction): pass #time.sleep(2)
        
    
    

        
        
if __name__ == '__main__':
    main()