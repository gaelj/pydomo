#!/usr/bin/python
# -*- coding: utf-8 -*-
    
import MySQLdb #, os, glob, time, datetime
import time
from gajPid import *
from gajResources import *
from datetime import datetime



sql_sensors = r'''
    SELECT sensorName FROM pi.temp_sensors;
    '''
    
sql_temps = r'''
    SELECT * FROM pi.vw_temperatures where date_time > date_add(now(), INTERVAL -1 DAY) order by date_time;
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
            # print(d)
            temps_by_sensor[d[1]].append((d[0], float(d[2])))
            
    except Exception as e:
        print(e)
        
    finally:
        con.close()
    
    return temps_by_sensor
    
def main():
    pid = PID(P=2.0, I=1.0, D=1.0)
    pid.setPoint(19.0)
    
    # main: read tempeatures, save to file, save contents of file to SQL
    try:
        dbs = GetDataBySensor()
                
        for sensor in dbs:
            if sensor == 'Salon':
                try:
                    # Owner().IsHome() # 1 if owner is home, else 0
                    for dt in dbs[sensor]: # temperature
                        _date = dt[0]
                        _temp = dt[1]
                        pidResult = pid.update(_temp)
                        
                        print('%s %s temp: %0.2f (target %0.2f) res: %0.2f' % (sensor, str(_date), _temp, pid.getPoint(), pidResult))
                except Exception as e:
                    print("Erreur : " + str(e))
            
    except Exception as e:
        print("Erreur : " + str(e))
        
if __name__ == '__main__':
    main()