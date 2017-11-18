#!/usr/bin/python3
from gajActuators import *
with Shutter(shutterNumber=0, name='Garden', initialState=0) as shutter:
    shutter.SetState(0)

