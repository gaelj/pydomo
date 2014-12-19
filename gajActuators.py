import subprocess

fldChacon =        r'/home/pi/433Utils/RPi_utils/codesend/'
fldDio =           r'/home/pi/hcc/'

cmdChacon =        r'codesend' 
cmdDio =           r'radioEmission'

ShutterCode =      r'11111111' # r'15515426'
SocketCode =       r'0FF'

settingsFileName = r'actuators_settings.txt'



class Power:
    Off = 0
    On = 1

class Direction:
    Down = 0
    Up = 1


class Actuator():
    '''
    Generic actuator class
    Inherited by the specific actuator classes
    '''
    def PersistState(self):
        c = dict()
        try:
            with open(settingsFileName, mode='r') as f:
                for line in f:
                    line = line.strip()
                    if line == '':
                        continue                    
                    d = line.split('\t')
                    c[d[0]] = d[1]            
        except Exception as e:
            print(e)

        finally:
            c[self.name] = str(self.state)
            
        with open(settingsFileName, mode='w') as f:
            for d in c:
                f.write(str.format('%s\t%s\n' % (d, c[d])))
    
    def RestoreState(self):
        try:
            with open(settingsFileName, mode='r') as f:
                for line in f:
                    line = line.strip()
                    d = line.split('\t')
                    if d[0] == self.name:
                        self.state = int(d[1])
        except Exception as e:
            print(e)
            with open(settingsFileName, mode='w') as f:
                f.write('')

    def __enter__(self):
        self.RestoreState()
        return self
    
    def __exit__(self, type, value, traceback):
        self.PersistState()
    
    def SetStateIfNeeded(self, state):
        if state != self.state:
            self.SetState(state)
            return True
        return False
    


class Socket(Actuator):
    def __init__(self, name, socketNumber, initialState=Power.Off):
        assert(socketNumber >= 0 and socketNumber < 3)
        assert(initialState == Power.On or initialState == Power.Off)
        self.name = name
        self.socketNumber = socketNumber
        self.state = initialState
        
    def SetState(self, state):
        assert(state == Power.Off or state == Power.On)
        params = SocketCode
        for i in range(8):
            if self.socketNumber == i:
                params += '0'
            else:
                params += 'F'
        params += str(state)
        subprocess.call(fldChacon + cmdChacon + ' ' + params, shell = True)
        self.state = state



class Shutter(Actuator):
    def __init__(self, name, shutterNumber, initialState=Direction.Up):
        assert(shutterNumber >= 0 and shutterNumber < 3)
        assert(initialState == Direction.Up or initialState == Direction.Down)
        self.name = name
        self.shutterNumber = shutterNumber
        self.state = initialState
        
    def SetState(self, state):
        assert(state == Direction.Up or state == Direction.Down)    
        if state == Direction.Down: stateString = 'off'
        elif state == Direction.Up: stateString = 'on'
        
        print(fldDio + cmdDio, '0', ShutterCode, self.shutterNumber, stateString)
        
        subprocess.call(fldDio + cmdDio + ' 0 ' + ShutterCode + ' ' + str(self.shutterNumber) + ' ' + stateString, shell = True)
        self.state = state