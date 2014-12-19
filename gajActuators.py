import subprocess
from gajResources import *




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
        
        print("state persisted.\n")
    
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
                
        print("state restored.\n")

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
    '''
    Chacon socket control
    '''
    def __init__(self, name, socketNumber, initialState=Power.Off):
        self.Code = ChaconCode

        assert(socketNumber >= 0 and socketNumber < 4)
        assert(initialState == Power.On or initialState == Power.Off)
        self.name = name
        self.socketNumber = socketNumber
        self.state = initialState
        
    def SetState(self, state):
        assert(state == Power.Off or state == Power.On)
        params = self.Code
        for i in range(8):
            if self.socketNumber == i:
                params += '0'
            else:
                params += 'F'
        params += str(state)
        print(fldChacon + cmdChacon + ' ' + params)
        subprocess.call(fldChacon + cmdChacon + ' ' + params, shell = True)
        self.state = state



class Shutter(Actuator):
    '''
    Shutter control with DIO
    '''
    def __init__(self, name, shutterNumber, initialState=Direction.Up):
        self.Code = DIOShutterCode

        assert(shutterNumber >= 0 and shutterNumber < 3)
        assert(initialState == Direction.Up or initialState == Direction.Down)
        self.name = name
        self.shutterNumber = shutterNumber
        self.state = initialState
        
    def SetState(self, state):
        assert(state == Direction.Up or state == Direction.Down)    
        if state == Direction.Down: stateString = 'off'
        elif state == Direction.Up: stateString = 'on'
        
        print(fldDio + cmdDio, '0', self.Code, self.shutterNumber, stateString)
        
        subprocess.call(fldDio + cmdDio + ' 0 ' + self.Code + ' ' + str(self.shutterNumber) + ' ' + stateString, shell = True)
        self.state = state



class Boiler(Actuator):
    '''
    Boiler control with DIO
    '''
    def __init__(self, name, initialState=Power.Off):
        self.Code = DIOBoilerCode

        assert(DIOBoilerNumber >= 0 and DIOBoilerNumber < 3)
        assert(initialState == Power.Off or initialState == Power.On)
        self.name = name
        self.BoilerNumber = DIOBoilerNumber
        self.state = initialState
        
    def SetState(self, state):
        assert(state == Power.Off or state == Power.On)
        if state == Power.Off: stateString = 'off'
        elif state == Power.On: stateString = 'on'
        
        print(fldDio + cmdDio, '0', self.Code, self.BoilerNumber, stateString)
        
        subprocess.call(fldDio + cmdDio + ' 0 ' + self.Code + ' ' + str(self.shutterNumber) + ' ' + stateString, shell = True)
        self.state = state
        
        
if __name__ == '__main__':
    
    with Socket(name = 'Lampe', socketNumber = 1) as lp:
        lp.SetStateIfNeeded(Power.Off)