'''
read temperature of all sensors connnected to the pi
write values to a temp file
write temp file contents in a mySQL database
'''
import os, glob, time, datetime

# db connection parameters
# load kernel modules to interface temp sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
# temp sensors directory
base_dir = '/sys/bus/w1/devices/'

def roundTime(dt=None, roundTo=60):
   """Round a datetime object to any time laps in seconds
   dt : datetime.datetime object, default now.
   roundTo : Closest number of seconds to round to, default 1 minute.
   Author: Thierry Husson 2012 - Use it as you want but don't blame me.
   """
   if dt == None : dt = datetime.datetime.now()
   seconds = (dt - dt.min).seconds
   # // is a floor division, not a comment on following line:
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)
   
def device_files():
    '''
    return a list of tuples: (deviceID, deviceFilePath)
    '''
    return map( lambda device_folder: (device_folder.replace(base_dir, '')[3:], device_folder + '/w1_slave'), \
        glob.glob(base_dir + '28*'))

def read_temp_raw(device_file):
    '''
    read a sensor's raw value
    '''
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temps():
    '''
    read all sensors and return a list of CSVs: date;sensorID;temp
    '''
    temps = list() # return value
    
    # get current date/time
    date_time = roundTime(None, 300).strftime("%Y-%m-%d %H:%M:%S")
    #time.strftime("%Y-%m-%d %H:%M:%S", roundTime(None, 300))
    max_retries = 3
    
    # iterate on each sensor
    for (deviceID, device_file) in device_files():
        retry = 1
        while retry <= max_retries: 
        
            # read raw temp
            lines = read_temp_raw(device_file)
            
            if lines[0].strip()[-3:] == 'YES': # CRC is OK
                # find the text "t=" and log the temperature located after it
                equals_pos = lines[1].find('t=')
                if equals_pos != -1:
                    # temp string found
                    temp_string = lines[1][equals_pos+2:]
                    temp_c = round(float(temp_string) / 1000.0, 2)
                    temps.append(";".join([date_time, deviceID, str(temp_c)]))
                    break                    
            # try again if CRC is not OK
            retry += 1
            time.sleep(0.2)
            
    return temps

def main():
    # main: read tempeatures, save to file, save contents of file to SQL
    try:
        rt = read_temps()
        print(rt)
        
    except Exception as e:
        print("Erreur : " + str(e))
        
if __name__ == '__main__':
    main()