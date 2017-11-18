# Chacon (white) remote control emulation
fldChacon =         r'/home/pi/433Utils/RPi_utils/'
cmdChacon =         r'codesend'
ChaconCode =        r'0FF'

# DIO (black) remote control emulation / DIO sensors control
fldDio =            r'/home/pi/hcc/'
cmdDio =            r'radioEmission'
DIOShutterCode =    r'11111111' # r'15515426'
DIOBoilerCode =     r'06051979'
DIOBoilerNumber =   0

# actuator state persistance file
settingsFileName =  r'actuators_settings.txt'

# weather collection service
weatherUrl =        r'http://wxdata.weather.com/wxdata/weather/local'
locationCode =      r'/FRNC0526:1:FR'

# db connection parameters
mySQLhost =         '192.168.30.100'
mySQLuser =         'pi'
mySQLpasswd =       'ET4bAwC6'
mySQLdb =           'pi'

# local owner presence
OwnerMac =          '9C:04:EB:22:98:16' # mac address of owner's smartphone
presenceTimeout =   300 # local owner presence timeout in seconds

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
