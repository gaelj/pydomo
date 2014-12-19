import time, urllib2, xmltodict, MySQLdb, datetime
from gajResources import *


class DayTime():
    def __init__(self):
        self.__prevRunDate = None
        self.__data = None

    def GetXmlFromUrl(self, url):
        file = urllib2.urlopen(weatherUrl + locationCode) 
        self.__data = file.read()
        file.close()
        self.__data = xmltodict.parse(self.__data)
        assert self.__data != None
    
    def GetTodaySunTimes(self):
        newSunTimesRetrievalDate = time.strftime("%d/%m/%Y")
        if newSunTimesRetrievalDate != self.__prevRunDate:
            print('from web')
            self.GetXmlFromUrl(weatherUrl)
            self.__prevRunDate = newSunTimesRetrievalDate
        else:
            print('from memory')
    
    def DecodeTimeString(self, timeString): # returns a time tuple
        return time.strptime(timeString,"%I:%M %p") # u'8:14 AM'
    
    def CurrentTime(self, dt):
        dt = dt.strftime("%I:%M %p")
        return self.DecodeTimeString(dt)
    
    #<weather ver="2.0">
    #    <loc id="FRNC0526">
    #        <sunr>8:14 AM</sunr>
    #        <suns>4:50 PM</suns>
    def DecodeData(self):
        return (self.DecodeTimeString(self.__data['weather']['loc']['sunr']), \
                self.DecodeTimeString(self.__data['weather']['loc']['suns']))
    
    def IsDayTimeNow(self):
        self.GetTodaySunTimes()
        sunR, sunS = self.DecodeData()
        isDayTime = False
        now = datetime.datetime.now()
        nowPlus = self.CurrentTime(now + datetime.timedelta(minutes = 20))
        nowMinus = self.CurrentTime(now - datetime.timedelta(minutes = 20))
        nowExact = self.CurrentTime(now)
        if sunR <= nowPlus and nowMinus < sunS:
            isDayTime = True
        print(time.strftime('%H:%M', sunR), time.strftime('%H:%M', sunS), time.strftime('%H:%M', nowExact))
        return isDayTime


class Owner():
    def __init__(self):
        pass
        
    def IsHome(self):
        try:    
            con = MySQLdb.connect(host=mySQLhost, user=mySQLuser, passwd=mySQLpasswd, db=mySQLdb)
    
            with con: 
                cur = con.cursor()
                cur.execute("select datetime_last as dtl from pi.probereq where mac = '%s' order by datetime_last desc limit 0, 1" % OwnerMac)
                conso_data = cur.fetchall()
            
            con.close() 
            
            # 2014-12-05 18:18:02
            nbSecsSinceLastConn = (datetime.datetime.now() - conso_data[0][0]).seconds
            print 'Ishome (nb seconds since last frame):', conso_data[0][0], nbSecsSinceLastConn

            return nbSecsSinceLastConn < presenceTimeout
            
        except Exception as e:
            print(e)
            return False
         
            
        
        
        
        
        
        
        