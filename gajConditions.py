import time, urllib2, xmltodict, MySQLdb, datetime

weatherUrl =    r'http://wxdata.weather.com/wxdata/weather/local'
locationCode =  r'/FRNC0526:1:FR'

# db connection parameters
mySQLhost = '192.168.30.100'
mySQLuser = 'pi'
mySQLpasswd = 'ET4bAwC6'
mySQLdb = 'pi'

OwnerMac = '9C:04:EB:22:98:16'
presenceTimeout = 300 # seconds


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
    
    def CurrentTime(self):
        now = time.strftime("%I:%M %p")
        return self.DecodeTimeString(now)
    
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
        now = self.CurrentTime()
        if (sunR <= now and now < sunS):
            isDayTime = True
        print(time.strftime('%H:%M', sunR), time.strftime('%H:%M', sunS), time.strftime('%H:%M', now))
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
            print conso_data[0][0], nbSecsSinceLastConn

            return nbSecsSinceLastConn < presenceTimeout
            
        except Exception as e:
            print(e)
            return False
         
            
        
        
        
        
        
        
        