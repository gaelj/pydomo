#!/usr/bin/python3
from gajActuators import *
with Shutter(shutterNumber=1, name='FrontSingle', initialState=0) as shutter:
    shutter.SetState(0)

