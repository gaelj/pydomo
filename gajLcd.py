#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

    
    
import MySQLdb #, os, glob, time, datetime
import time
from RPLCD import CharLCD
from RPLCD import Alignment, CursorMode, ShiftMode
from RPLCD import cursor, cleared

try:
    input = raw_input
except NameError:
    pass

try:
    unichr = unichr
except NameError:
    unichr = chr
    
    
from gajActuators import *
from gajConditions import *

lcd = CharLCD(rows=2, cols=16, pin_rs=15, pin_e=23, pins_data=[16,19,21,22], dotsize=8)

# db connection parameters
mySQLhost = '192.168.30.100'
mySQLuser = 'pi'
mySQLpasswd = 'ET4bAwC6'
mySQLdb = 'pi'




sql_sensors = r'''
    SELECT sensorName FROM temp_sensors'''
    
sql_temps = r'''
    SELECT date_time, sensorName, temp, prev_temp, var FROM pi.last_temps;
    '''

def GetDataBySensor():
    '''
    return {sensor => [(date_time, temperature)]}
    '''
    
    sensors = list()
    temp_data = list()
    temps_by_sensor = dict()
    
    try:    
        con = MySQLdb.connect(host=mySQLhost, user=mySQLuser, passwd=mySQLpasswd, db=mySQLdb)

        with con: 
            cur = con.cursor()
            cur.execute(sql_temps)
            temp_data = cur.fetchall()
            
            cur2 = con.cursor()
            cur2.execute(sql_sensors)
            sensors = cur2.fetchall()
        
        # instantiate the dictionary (create the keys and assign an empty list)
        for s in sensors:
            temps_by_sensor[s[0]] = list()
            
        # populate the lists with all values of (date_time, temperature)
        for d in temp_data:        
            print(d)
            temps_by_sensor[d[1]].append(((d[0], float(d[2]), d[4])))
            
    except Exception as e:
        print(e)
        
    finally:
        con.close()
    
    return temps_by_sensor
    
    
up = (  0b00100, 
        0b01110, 
        0b01110, 
        0b10101, 
        0b00100, 
        0b00100, 
        0b00100, 
        0b00100)
        
dn = (  0b00100, 
        0b00100, 
        0b00100, 
        0b00100, 
        0b10101, 
        0b01110, 
        0b01110, 
        0b00100)
        
dg = (  0b01100, 
        0b10010, 
        0b10010, 
        0b01100, 
        0b00000, 
        0b00000, 
        0b00000, 
        0b00000)

lcd.create_char(0, up)
lcd.create_char(1, dn)
lcd.create_char(2, dg)

def main():
    lcd.write_string("WELCOME BACK !!! ")
    time.sleep(3)
    
    while (True):
        # main: read tempeatures, save to file, save contents of file to SQL
        try:
            lcd.clear()
            

            lcd.write_string("fetching data...")
            time.sleep(1)
            dbs = GetDataBySensor()
            for i in range(3):
                lcd.clear()
                #lcd.write_string("is home: %s" % Owner().IsHome())
                #time.sleep(3)
                
                for sensor in dbs:
                    try:
                        lcd.clear()
                        lcd.cursor_pos = (0, 0)
                        lcd.write_string(sensor)
                        
                        lcd.cursor_pos = (0, 15)
                        lcd.write_string(str(int(Owner().IsHome()))) # 1 in top right corner if owner is home, else 0
                        
                        lcd.cursor_pos = (1, 0)
                        lcd.write_string(str(dbs[sensor][0][1])) # temperature
                        lcd.write_string(unichr(2)) # °
                        lcd.write_string('C')
                        
                        lcd.cursor_pos = (1, 15) # display temperature variation icon in lower right corner
                        if dbs[sensor][0][2] > 0.003:
                            lcd.write_string(unichr(0))
                        elif dbs[sensor][0][2] < -0.003:
                            lcd.write_string(unichr(1))
                        else:
                            lcd.write_string("=")
                        
                        time.sleep(3)
                    except Exception as e:
                        print("Erreur : " + str(e))
                        time.sleep(1)
                
        except Exception as e:
            print("Erreur : " + str(e))
            lcd.write_string("ERROR temp main")
            time.sleep(1)
        
if __name__ == '__main__':
    main()