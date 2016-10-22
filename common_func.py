# Common function 
# print function 
import time
import os
import sys

#print function 
#---------------------------------------------------------------------------------------------

def writeDataToFile(f_name,str_to_write):
        for i in os.listdir(os.getcwd()):
                if i == 'log':
                        break
                else:
                        os.system('mkdir log')
                        break

        file_name_path = os.path.join(os.getcwd(),'log',f_name)
        try:
                f = open(file_name_path, 'r+')
        except IOError as e:
                print file_name_path, '  Created '
                f=open(file_name_path,'w+')

        f.read()
        pos = f.tell()
        f.seek(pos)
        string = ('[INFO][%s]  ' % time.ctime() + str_to_write + '\n')
        f.write(string)
        f.close()

def print_time(threadName, delay):
        count = 5
        while count:
                time.sleep(delay)
                print threadName, ' time : ',time.strftime('%H:%M:%S')
                count -= 1

def print_info(strings):
        strs = time.strftime('[%H:%M:%S]')  + str(strings)
        print strs
        writeDataToFile('log.txt',strs)


def print_mqttinfo(strings):
        strs = time.strftime('[%H:%M:%S]') + str(strings)
        print strs
        writeDataToFile('weatherofmqtt.txt', strs)

def print_sessionifo(strings):
        strs = time.strftime('[%H:%M:%S]')  + str(strings)
        print strs
        writeDataToFile('sessionlog.txt',strs)  

def print_timerinfo(strings):
        strs = time.strftime('[%H:%M:%S]')  + str(strings)
        print strs
        writeDataToFile('timerlog.txt',strs)
        
def print_IRinfo(strings):
	strs = time.strftime('[%H:%M:%S]')  + str(strings)
        print strs
        writeDataToFile('IR.txt',strs)

def print_dumDevInfo(strings):
        strs = time.strftime('[%H:%M:%S]')  + str(strings)
        print strs
        writeDataToFile('dumDevice.txt',strs)  

def print_staticLightInfo(strings):
        print strings
        writeDataToFile('lightstatic.txt',strings)  


def print_CmdOrString(strings):
        print strings
        writeDataToFile('CmdOrString.txt',strings)  

def print_deviceinfo(d_name):
        val_list = list()
        i = 1
        strtmp = '\n' + '-'*8 + 'Conn_info' + '-'*8 + '\n'
        for key, value in d_name.iteritems():
                strtmp += str(i) + '. ' + ',  '.join(value) + '\n'
                i += 1
        print strtmp
        return strtmp



def print_connectionList(_connection_list):
        val_list = list()
        i = 1
        strtmp = '\n' + '-'*8 + 'conn_list' + '-'*8 + '\n'
        for i in range(len(_connection_list)):
                strtmp += str(i+1) +'. ' + str(_connection_list[i]) + '\n'
        print strtmp
        return strtmp

def print_LedJarTimerinfo(_timer):
        i = 1
        strtmp = '\n' + '-'*8 + 'timer_info' + '-'*8 + '\n'
        for key in _timer.keys():
                strtmp += str(i) + '. '+str(key) + ': ' + _timer[key].name + '\n'
                i += 1
        print strtmp
        return strtmp

def print_lightinfo(_DI,_sl,_slp,_lrl, _ts):

        strtmp = '\n' + '-'*8 + 'light_info' + '-'*8 + '\n'
        strtmp += 'Static Light Val(1h)                 : %d \n' % _sl
        strtmp += 'Moment Light Val                     : %d \n' % _slp
        _state = ['Dark','Bright']
        
        device_exist = 0
        for key, values in _DI.iteritems():
                if values[0] == '[[Nano]]':
                        device_exist = 1
        
        if device_exist == 1:
                operate = 1
        else:
                operate = 0
                
        _state = ['NO','YES']
        strtmp += 'LedJar Operation?            : %s \n' % _state[operate]
        return strtmp


def JSONtoFile(f_name, str_to_write):
        try:
                f = open(f_name, 'r+')
        except IOError as e:
                print f_name, '  Created '
                f = open(f_name, 'w+')

        f.read()
        pos = f.tell()
        f.seek(pos)

        f.write(str_to_write)
        f.close()


def WheatherLOG(f_name, str_to_write, date_str):
        try:
                f = open(f_name, 'r+')
        except IOError as e:
                print f_name, '  Created '
                f = open(f_name, 'w+')

        data = f.read()
        if data.find(date_str) != -1:
                f.close()
                return
        pos = f.tell()
        f.seek(pos)

        f.write(str_to_write)
        f.close()


def print_Info(strings):
        strs = time.strftime('[%H:%M:%S]') + str(strings)
        print strs
        writeDataToFile('mqtt_log.txt', strs)
#---------------------------------------------------------------------------------------------

#String Procession function 
#---------------------------------------------------------------------------------------------

def checkCommandOrString(_data):
        if ord(_data[0]) >= 0xe0:
                # control data
                return True
        else:
                # Normal String
                return False


def getDataFromAscii(_data):
        return_dat = 0x0
        for i in range(0, len(_data)):
                return_dat = (return_dat << 8) | ord(_data[i])
        return return_dat        

# retun inverse list
# return hex code list 
def makeIntToAscii(_int):
        return_dat = []
        while _int != 0:
                return_dat.append(_int & 0xff)
                _int = _int >> 8
        return return_dat

def printCommand(data):
        length = len(data)
        lists = list()
        for i in range(length):
                lists.append(data[i])
        return lists
#---------------------------------------------------------------------------------------------
#check specific device 
#---------------------------------------------------------------------------------------------
def findSockByDeviceName(_Device_info, _d_name):
        for i in _Device_info.keys():
                if _Device_info[i][0] == _d_name:
                        return i

        return False

#---------------------------------------------------------------------------------------------


def deleteTimerDic(_S_timer,timer_name):
        if _S_timer.has_key(timer_name):
                _timer = _S_timer.pop(timer_name)
                if _timer.isAlive():
                        _timer.cancel()
        else:
                print_info('no timer')



# help Command
# ---------------------------------------------------------------------------------------------
def PrintCommand():
        strtmp = '\n' + '-' * 8 + 'PRINT_COMMAND' + '-' * 8 + '\n'
        strtmp += 'mqtt_get_timeinfo : ' + 'print time info of get weather' +'\n'
        strtmp += 'mqtt_get_weather : ' + "request weather info to server " + '\n'
        strtmp += 'mqtt_set_time = HH:MM' + '\n'
        strtmp += 'mqtt_del_time' + '\n'
        strtmp += 'mqtt_get_forcast :' + 'get weather forcaste ' + '\n'
        strtmp += '\n' + '-' * 8 + 'PRINT_COMMAND' + '-' * 8 + '\n'
        return strtmp




# ---------------------------------------------------------------------------------------------

if __name__ == "__main__":
        print 'HI'
        print_info('fuck you man')