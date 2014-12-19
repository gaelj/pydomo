# Chacon (white) remote control emulation
fldChacon =         r'/home/pi/433Utils/RPi_utils/'
cmdChacon =         r'codesend'
ChaconCode =        r'0FF'

# DIO (black) remote control emulation / DIO sensors control
fldDio =            r'/home/pi/hcc/'
cmdDio =            r'radioEmission'
DIOShutterCode =    r'11111111' # r'15515426'

# actuator state persistance file
settingsFileName =  r'actuators_settings.txt'

# weather collection service
weatherUrl =        r'http://wxdata.weather.com/wxdata/weather/local'
locationCode =      r'/FRNC0526:1:FR'

# temp sensors directory
baseTempDensorsDirs = ('/sys/bus/w1/devices/', '/mnt/pigarage/sys/bus/w1/devices/')

tempSensors = {
               '00000662a373': 'Pi Salon',
               '0000065c5371': 'Couloir',
               '0000065c6e8b': 'Salon',
               '0000065c09d5': 'Garage',
               '0000065ce7c6': 'Exterieur',
               '0000065d01ee': 'Salon 2'
               }
