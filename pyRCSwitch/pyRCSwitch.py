'''
Created on 23 nov. 2014

@author: gael
'''
import math, wiringpi2 as wiringpi, threading, time
import code
from datetime import date
import datetime


O_CLOEXEC              = 0

NUM_PINS               =  17 # Deprecated

WPI_MODE_PINS          = 0
WPI_MODE_GPIO          = 1
WPI_MODE_GPIO_SYS      = 2
WPI_MODE_PHYS          = 3
WPI_MODE_PIFACE        = 4
WPI_MODE_UNINITIALISED = -1

# Pin modes
INPUT                  = 0
OUTPUT                 = 1
PWM_OUTPUT             = 2
GPIO_CLOCK             = 3

LOW                    = 0
HIGH                   = 1

# Pull up/down/none
PUD_OFF                = 0
PUD_DOWN               = 1
PUD_UP                 = 2

# PWM
PWM_MODE_MS            = 0
PWM_MODE_BAL           = 1

# Interrupt levels
INT_EDGE_SETUP         = 0
INT_EDGE_FALLING       = 1
INT_EDGE_RISING        = 2
INT_EDGE_BOTH          = 3





def threaded(fn):
    def wrapper(*args, **kwargs):
        return threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper


    
class pyRCSwitch(object):
    '''
    Remote controlled AC switches for Raspberry Pi, Python implementation 
    '''        
    __ReceivedValue = None
    __ReceivedBitlength = 0
    __ReceivedDelay = 0
    __ReceivedProtocol = 0
    __timings = list()
    __ReceiveTolerance = 60
    __thread = None
    
    string = ''
    
    def StartPolling(self):
        __rxstate = -1
        #print('polling started on pin %i' % self.__ReceiverInterrupt)
        while self.__ReceiverInterrupt != -1:
            
            wiringpi.delayMicroseconds(1)
            
            r = wiringpi.digitalRead(self.__ReceiverInterrupt)
            if r == 0: self.string += '_'
            elif r == 1: self.string += '-'
            if r != __rxstate:
                self.handleInterrupt()
                __rxstate = r
        #print('polling stopped on pin %i' % self.__ReceiverInterrupt)
                
        
    lastTime = None
    repeatCount = 0
    changeCount = 0
    
    def receiveProtocol_Chacon(self):
        delay = 300#self.__timings[2]
        
        pulses = [int(round(float(i)/float(delay))) for i in self.__timings]        
        print("pulses: %s" % pulses)
        
        
        
        self.__ReceivedValue = ''
        self.__ReceivedBitlength = len(self.__timings)
        self.__ReceivedDelay = delay
        self.__ReceivedProtocol = 3
        
        
    def receiveProtocol_DIO(self):
        code = 0
        string = ''
        
        delay = self.__timings[0] / 40        
        t = self.__ReceiveTolerance * 0.01
        
        m1 = 1
        m2 = 6
        
        delayTolerance1 = delay * m1 * t # 15 => [10;40]
        delayTolerance2 = delay * m2 * t # 15 => [10;40]
        
        #print('delay: %f - tolerance: %f' % (delay, delayTolerance))
        print('range 1: %f %f' % (delay*m1 - delayTolerance1, delay*m1 + delayTolerance1))
        print('range 2: %f %f' % (delay*m2 - delayTolerance2, delay*m2 + delayTolerance2))
        
        for i in range(2, len(self.__timings)):
            t = self.__timings[i]
            
            if delay*m1 - delayTolerance1 < t and t < delay*m1 + delayTolerance1:
                code += 0
                code = code << 1
                string += '0'
            elif delay*m2 - delayTolerance2 < t and t < delay*m2 + delayTolerance2:
                code += 1
                code = code << 1
                string += '1'
            else:
                code = 0
                print('failed to decode: %i' % t)
                break
            
        code = code >> 1
        
        if len(self.__timings) > 6:
            self.__ReceivedValue = code
            self.__ReceivedBitlength = len(self.__timings)
            self.__ReceivedDelay = delay
            self.__ReceivedProtocol = 4
        
        print('string: %s' % string )
        
        return (code != 0)
    
    
            
    def handleInterrupt(self):
        syncDur = 14000
        
        time = wiringpi.micros()
        if self.lastTime == None: self.lastTime = time
        duration = time - self.lastTime
                
        if len(self.__timings) > 2 and duration > syncDur: #and duration > self.__timings[0] - 200 and duration < self.__timings[0] + 200:
            #self.repeatCount += 1         
            
            print("=======================================================================")
            print("rep: %i chg: %i" % (self.repeatCount, len(self.__timings)))
            #if self.repeatCount >= 2:
                                
            #print("rep cnt: %i - duration: %i - count: %i - delay: %i" % (self.repeatCount, duration, len(self.__timings), delay))
            print(wiringpi.micros(), [int(50*round(t/50,0)) for t in self.__timings])
            

            #ucode = ""
            #scode = ""
            #for i in range(self.changeCount):
            #    p = self.__timings[i]
            #    ucode += " " + str(p)
            #    scode += str(p)
            #    if i % 4 == 0:
            #        ucode += " "
            #print("coded string: %s" % ucode)
            
            
            
            if self.receiveProtocol_Chacon():
                print('value: %s' % self.__ReceivedValue)
            
            if self.receiveProtocol_DIO():
                print('value: 0x%04X' % self.__ReceivedValue)
            
            #self.repeatCount = 0
            
            self.__timings = list()
            
        #elif len(self.__timings) > 2 and duration > syncDur:
        #    print('%i packets discarded (2)' % len(self.__timings))
        #    self.__timings = list()
            
        self.__timings.append(duration)
        self.lastTime = time

    
    def disableTransmit(self): self.__TransmitterPin = -1
    def disableReceive(self): 
        self.__ReceiverInterrupt = -1
        if self.__thread != None:
            self.__thread.join()
    def enableReceive(self, interrupt = None):
        if interrupt != None:
            self.__ReceiverInterrupt = interrupt
        if self.__ReceiverInterrupt != -1:
            pyRCSwitch.__ReceivedValue = None
            pyRCSwitch.__ReceivedBitlength = None
            self.__thread = threading.Thread(group=None, target=self.StartPolling, args=(), name=None)
            self.__thread.start()
                        
    def enableTransmit(self): 
        self.__TransmitterPin = self.__TXPIN
        wiringpi.pinMode(self.__TransmitterPin, OUTPUT)
    def setReceiveTolerance(self, Percent): pyRCSwitch.__ReceiveTolerance = Percent
    def setRepeatTransmit(self, RepeatTransmit): self.__RepeatTransmit = RepeatTransmit        
    def setPulseLength(self, PulseLength): self.__PulseLength = PulseLength
    def available(self): return pyRCSwitch.__ReceivedValue != None
    def resetAvailable(self): pyRCSwitch.__ReceivedValue = None
    def getReceivedValue(self): return pyRCSwitch.__ReceivedValue
    def getReceivedBitlength(self): return pyRCSwitch.__ReceivedBitlength
    def getReceivedDelay(self): return pyRCSwitch.__ReceivedDelay
    def getReceivedProtocol(self): return pyRCSwitch.__ReceivedProtocol
    def getReceivedRawdata(self): return pyRCSwitch.__timings
    def setProtocol(self, Protocol=None, PulseLength=None):
        self.protocol = Protocol
        if Protocol==1: PulseLength=350
        elif Protocol==2: PulseLength=650
        self.setPulseLength(PulseLength)    
    def __transmit(self, HighPulses, LowPulses):
        disabled_Receive = False
        ReceiverInterrupt_backup = self.__ReceiverInterrupt
        if self.__TransmitterPin != -1:
            if self.__ReceiverInterrupt != -1:
                #self.disableReceive()
                disabled_Receive = True                
                
            wiringpi.digitalWrite(self.__TransmitterPin, HIGH)
            wiringpi.delayMicroseconds(self.__PulseLength * HighPulses)
            
            wiringpi.digitalWrite(self.__TransmitterPin, LOW)
            wiringpi.delayMicroseconds(self.__PulseLength * LowPulses)
                        
            #if disabled_Receive:
            #    self.enableReceive(ReceiverInterrupt_backup)
    def __transmitRaw(self, timeH, timeL):
        disabled_Receive = False
        ReceiverInterrupt_backup = self.__ReceiverInterrupt
        if self.__TransmitterPin != -1:
            if self.__ReceiverInterrupt != -1:
                #self.disableReceive()
                disabled_Receive = True
                
            wiringpi.digitalWrite(self.__TransmitterPin, HIGH)
            wiringpi.delayMicroseconds(int(timeH))
            
            wiringpi.digitalWrite(self.__TransmitterPin, LOW)
            wiringpi.delayMicroseconds(int(timeL))
            
            #if disabled_Receive:
                #self.enableReceive(ReceiverInterrupt_backup)


    def __sendAcPlug(self, CodeWord):
        '''
        prise murale charcon colruyt
        '''
        self.setPulseLength(250)
        for Repeat in range(self.__RepeatTransmit):
            for c in CodeWord:
                if c=='0':
                    self.__transmit(1,5)
                    self.__transmit(1,5)
                elif c=='F':
                    self.__transmit(1,5)
                    self.__transmit(4,2)
                elif c=='1':
                    self.__transmit(4,2)
                    self.__transmit(4,2)
            self.__transmit(1,62) # sync
    
    def SendRawTimings(self, timings):        
        self.enableTransmit()
        for i in range(0, len(timings)/2):
            t1 = timings[i]
            t2 = timings[i+1]            
            self.__transmitRaw(t1, t2)
        self.disableTransmit()
        wiringpi.delayMicroseconds(250000)
        
    def SwitchAcPlug(self, plug, state):        
        self.enableTransmit()
        pstring = ''
        for i in range(1, 9):
            l = 'F'
            if i == plug: l = '0'
            pstring += l
            
        print("=======================================================================")
        print('sending 0FF%s%i' % (pstring, state))
        self.__sendAcPlug('0FF%s%i' % (pstring, state))
        self.disableTransmit()
        
    def __init__(self, PulseLength=350, RepeatTransmit=2, ReceiveTolerance=70, Protocol=None, TXPIN=0, RXPIN=2):
        # self.RCSWITCH_MAX_CHANGES = 280 # 67
        if wiringpi.wiringPiSetup() == -1: raise 'Problem initializing wiring pi'    
            
        self.__ReceivedValue = None
        
        self.setProtocol(Protocol, PulseLength)
        self.setRepeatTransmit(RepeatTransmit)
        self.setReceiveTolerance(ReceiveTolerance)
        
        self.__TransmitterPin = -1
        self.__ReceiverInterrupt = -1
        
        self.__TXPIN = TXPIN
        self.__RXPIN = RXPIN
        
        
        if TXPIN != None:
            self.__TransmitterPin = TXPIN
        if RXPIN != None:
            self.__ReceiverInterrupt = RXPIN
            
            
            
if __name__ == '__main__':
    s = pyRCSwitch(RepeatTransmit=4,TXPIN=0,RXPIN=2)
    try:
        s.enableReceive()
        print('receive enabled')

        #s.SwitchAcPlug(1, 0)
        #s.SwitchAcPlug(1, 1)
        #s.SwitchAcPlug(2, 0)
        #s.SwitchAcPlug(2, 1)
        #s.SwitchAcPlug(2, 1)
            
    
        
        #timings = [10620, 1780, 1200, 240, 320, 300, 1260, 260, 300, 200, 1360, 240, 1360, 240, 340, 180, 1400, 240, 300, 260, 1300, 240, 340, 200, 340, 200, 1360, 240, 1360, 240, 360, 240, 1320, 240, 320, 240, 320, 240, 1360, 260, 280, 240, 1380, 260, 1360, 200, 360, 200, 320, 200, 1380, 260, 1360, 180, 340, 240, 1360, 240, 300, 340, 1220, 240, 360, 200, 1360, 240, 300, 240, 1360, 260, 300, 240, 1360, 220, 300, 240, 320, 240, 1360, 260, 300, 240, 1380, 180, 1360, 240, 300, 240, 360, 200, 1380, 240, 380, 120, 1400, 200, 300, 260, 1360, 260, 1340, 260, 300, 260, 280, 260, 1380, 220, 300, 240, 1340, 260, 300, 260, 1320, 260, 300, 240, 1320, 260, 300, 240, 1360, 260, 1340, 200, 340, 200, 300, 240, 1340, 260]
        #timings = [10620, 1140, 1880, 240, 320, 240, 1340, 240, 320, 260, 1320, 280, 1320, 220, 320, 320, 1240, 240, 380, 180, 1380, 240, 280, 240, 320, 220, 1400, 220, 1320, 240, 320, 220, 1400, 200, 320, 240, 280, 240, 1360, 220, 340, 220, 1380, 240, 1320, 220, 340, 240, 280, 320, 1280, 280, 1340, 240, 280, 280, 1320, 220, 320, 240, 1320, 240, 400, 180, 1320, 240, 340, 220, 1380, 300, 200, 240, 1380, 200, 340, 240, 280, 280, 1340, 240, 280, 220, 1360, 240, 1360, 220, 340, 220, 280, 240, 1420, 180, 340, 260, 1300, 240, 520, 120, 1260, 240, 1400, 180, 340, 240, 340, 220, 1400, 260, 240, 240, 1360, 240, 1340, 240, 280, 240, 340, 240, 1360, 240, 280, 240, 1360, 240, 1380, 260, 280, 240, 300, 220, 1420, 180]
        timings = [10650, 14400, 150, 100, 1300, 200, 1400, 250, 300, 200, 1350, 200, 250, 250, 250, 250, 1350, 200, 250, 200, 1350, 300, 1350, 200, 250, 250, 300, 200, 1350, 250, 1300, 250, 250, 250, 1350, 200, 300, 300, 1250, 250, 300, 200, 1350, 200, 350, 200, 1350, 200, 350, 200, 1350, 250, 300, 200, 350, 200, 1350, 200, 350, 200, 1350, 200, 1350, 200, 300, 300, 200, 350, 1250, 200, 350, 200, 1300, 200, 300, 300, 1250, 250, 1300, 250, 300, 300, 200, 250, 1300, 200, 350, 200, 1350, 200, 350, 150, 1400, 200, 300, 200, 1350, 200, 350, 200, 1350, 200, 1350, 200, 300, 300, 200, 250, 1350, 250]
        
        
        stime = wiringpi.micros()
        
        #if True:
        if False:
            print('start sending')    
            for j in range(4):
                for i in range(4):        
                    s.SendRawTimings(timings)
                time.sleep(0.25)
                print('sent')
          
         
        if s.available():
            value = s.getReceivedValue()        
            if value == 0: print("Unknown encoding\n")
            else: print("Received %i\n" % s.getReceivedValue())       
            s.resetAvailable();

         
         
        stime = wiringpi.micros()
        print('sleeping...')
        time.sleep(3)
        print('done')
    except Exception as e:
        pass
    finally:     
        s.disableReceive()
    
    