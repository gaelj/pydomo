#!/usr/bin/python3
from gajActuators import *
with Shutter(shutterNumber=2, name='FrontDouble', initialState=0) as shutter:
    shutter.SetState(0)

