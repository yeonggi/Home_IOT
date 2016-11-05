# -*- coding: utf-8 -*-
import json, requests
import time
import datetime
import paho.mqtt.client as mqtt
import sys
sys.path.insert(0, '/root/Home_IOT/DataBase')
import DB_Process
from mqtt_thread import *
import Queue
sys.path.insert(0, '/root/Home_IOT')
from common_func import *


#c4ca3e7f12ae57ad1fca3d82f066d33b API Key
#http://api.openweathermap.org/data/2.5/weather?id=1846898&APPID={API Key}
#http://api.openweathermap.org/data/2.5/forecast?id=1846898&APPID=c4ca3e7f12ae57ad1fca3d82f066d33b
#id 1846898 anyang, id 1845457 Jeonju, id 1835847 Seoul
#City list 파일을 참조해서 얻어올 데이터로 쓰는것도 좋을 것 같음
#temp unit 켈빈, 절대온도
#아침에 데이터 필요 불꺼질때 내일 아침 기온 정보 대로 불이 켜져야함
#날씨 찾는거 잘못짬 ..... dt unix to date 로 해야함 ...datetime.datetime.fromtimestamp(1474351200).strftime('%Y-%m-%d %H:%M:%S') 이거 이용
data_queue = Queue.Queue()
url_current_weather = 'http://api.openweathermap.org/data/2.5/weather'
url_current_forecast = 'http://api.openweathermap.org/data/2.5/forecast'
CURRENT = 10
FORCAST = 11
params = dict(
    id=1846898, #KR anyang
    APPID='c4ca3e7f12ae57ad1fca3d82f066d33b'
)
weather_main_list = ["Thunderstorm","Drizzle","Rain","Snow","Atmosphere","Clear","Clouds","Extreme","Additional","Haze"]
LIGHT_ON_TIME = ["13:57", "21:00"]
SAVE_REQ_TIME = ['00:00', '08:00', '16:00']
fixed_alarm_time = "09 00 00"
cond_flag = False
cond_flag_old = False
start_up = True
dis_times = 0
time_delta = 0
db_file_name = '/root/Home_IOT/DB/Wheather.db'
db_table_name = 'wheather_info'

def compareTemp(w_db, date_to_compare, current_temp):
    # type: (object, object, object) -> object
    date, time = date_to_compare.split()
    date = date.split('-')
    time = time.split(':')


    if int(time[0])%3 > 0:
        now = datetime.datetime.now()
        min_time = now.replace(hour = 3*(int(time[0])/3), minute=0,second = 0)
        if 3*(int(time[0])/3) + 3 == 24:
            max_time = now.replace(day=now.day+1,hour=0, minute=0, second=0)
        else:
            max_time = now.replace(hour = 3*(int(time[0])/3) + 3, minute= 0, second=0)
        cur_time = now.replace(hour = int(time[0]), minute= int(time[1]), second=int(time[2]))
        if (cur_time - min_time > max_time - cur_time) == True:
            cmp_time = max_time
        else:
            cmp_time= min_time
    else:
        cmp_time = datetime.datetime(year= int(date[0]), month= int(date[1]), day= int(date[2]), hour =int(time[0]), minute= 0, second=0)

    yesterday = cmp_time - datetime.timedelta(days=-1)
    date_str = yesterday.strftime('%Y-%m-%d %H:%M:%S')

    print date_str

    try:
        temp = w_db.DBSelectOneByKey(db_file_name, db_table_name, 'DATE',date_str)
        if len(temp) > 1:
            print_info('-------------------------DB has 2 data -----------------------------')
        elif len(temp) < 1:
            return 0xff

        print temp
        temp = temp[0][3]
        if temp < current_temp:
            return 1
        else:
            return 0
    except:
        return 0xff




def SaveWeatherInFo(urls, file_name, table_name, db_class):
    resp = requests.get(url=urls, params=params)
    data_dic = json.loads(resp.text)

    query_list = []
    data_list = data_dic['list']
    print_Info('-----------------DB SAVE !!!-------------')
    for val_dic in data_list:
        wheather_date = datetime.datetime.fromtimestamp(val_dic['dt']).strftime('%Y-%m-%d %H:%M:%S')
        temp = val_dic['main']['temp'] - 273.15
        wheather= val_dic['weather'][0]['main']
        query_list.append((str(wheather_date), str(wheather) ,round(temp,2)))

    db_class.DBInsertMany(file_name,table_name,'Date',query_list)

    if db_class.DB_count == 50:
        db_class.DBDeleteRange(file_name, table_name, 'ID', 1, 20)

def RequestWeatherInFo(urls,dis_date,dis_time, *args):
    resp = requests.get(url=urls, params=params)
    data_dic = json.loads(resp.text)
    print_all_str = json.dumps(data_dic, sort_keys=True, indent=4)
    #print print_all_str
    data_list=0

    today = datetime.date.today()
    com_day = today + datetime.timedelta(days=dis_date)

    for key, value in data_dic.iteritems():
        if key == 'list':
            data_list = data_dic['list']
            for i in range(len(data_list)):
                rsp_day = data_list[i]['dt']
                rsp_day = datetime.datetime.fromtimestamp(rsp_day).strftime('%Y-%m-%d %H:%M:%S')
                rsp_day = rsp_day.split()
                strs = "%d 00 00" % dis_time
                alarm_time = time.strptime(strs, "%H %M %S")

                if (str(rsp_day[0]) == str(com_day)) and (str(rsp_day[1]) == time.strftime('%H:%M:%S',alarm_time)):
                    data_dic = data_list[i]
                    break

    return_data = dict()
    return_data['DATE'] = str(com_day)
    try:
        return_data['TIME'] = str(rsp_day[1])
    except:
        return_data['TIME'] = time.strftime('%H:%M:%S',time.localtime())
    for i in range(len(args)):
        if type(args[i]) == list:
            if args[i][0] == 'weather':
                try:
                    return_data['WT'] = data_dic[args[i][0]][0][args[i][1]]
                except:
                    pass
            else:
                try:
                    return_data['TEMP'] = data_dic[args[i][0]][args[i][1]] - 273.15
                except:
                    pass

    print_Info( 'Date to get weather : '+ return_data['DATE'] +'  ' + return_data['TIME'])
    print "Data to return: "+ str(return_data)
    return return_data

print time.localtime()

mqttc = mqtt.Client()
mqttc.connect("127.0.0.1",1883)



def on_connect(client, userdata, flags, rc):
    print ("Connencted with result code " + str(rc))
    client.subscribe("IOT_dat/command")

def on_message(client, userdata, msg):
    print msg.topic + " : " + str(msg.payload)
    data_queue.put_nowait(msg.payload)

def MQTT_subscribe(t_event):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("127.0.0.1", 1883)
    client.loop_start()

def MQTT_publish( msg_topic, pub_str):
	mqttc = mqtt.Client()
	mqttc.connect("127.0.0.1", 1883)
    #"IOT_dat/command"
	mqttc.publish(msg_topic, pub_str)
	mqttc.loop(2)

def decode_string(data_str,light_on_time):
    global dis_times
    global time_delta
    if data_str.strip()== 'mqtt_get_weather':
        print_Info('Req from Master Or Light ')
        cur_time = time.localtime()
        if cur_time.tm_hour < 9:
            time_delta = 0
        return FORCAST

    elif data_str.find('mqtt_set_time') >=0:
        index = data_str.find(':')
        data_str = data_str[(index+1):].strip()
        print_Info( 'mqtt_set_time '+ str(data_str))
        if data_str.find(':') > 0:
            light_on_time.append(data_str)
            return 2

    elif data_str.find('mqtt_del_time') >=0:
        index = data_str.find(':')
        data_str = data_str[(index+1):].strip()
        print_Info('mqtt_del_time ' + str(data_str))
        try:
            light_on_time.remove(data_str)
            return 2
        except:
            print '[%s]Remove Fail' % data_str
            return 0xff

    elif data_str.strip()== 'mqtt_get_timeinfo':
        MQTT_publish("IOT_dat/command",str(light_on_time))
        return 3

    elif data_str.strip()== 'mqtt_get_forcast':
        print_Info('Req from Master or Light')
        dis_times = 9
        return 11

    elif data_str.find('[IR]') >=0:
        print_Info('Req from IR ')
        ir_code = data_str[data_str.find('[IR]') + len('[IR]')]
        return_dat = 0
        dis_times = 0
        try:
            ir_code = int(ir_code)
            if ir_code == 7:
                return_dat = CURRENT
            elif ir_code == 8:
                return_dat = FORCAST
            elif ir_code == 9:
                return_dat = 12
            else:
                return_dat = 0
        except:
            pass

        return return_dat


    else:
        return 0

mqtt_command = DummyDeviceThread(1, 'MQTT_COMMAND', MQTT_subscribe)
mqtt_command.start()




DB_wheather = DB_Process.DBProc()
arg = ('Date text', 'Wheather text', 'Temp real')
DB_wheather.DBCreate(db_file_name, db_table_name, arg)

SaveWeatherInFo(url_current_forecast,db_file_name,db_table_name,DB_wheather)

alarm_1 = ClockThread(1, '07:30:00',SaveWeatherInFo,url_current_forecast, db_file_name,db_table_name,DB_wheather)
alarm_1.start()

while True:
    get_request_time = 9
    decode_res = 0
    time_delta = 1
    try:
        try:
            data_str = data_queue.get_nowait()
            decode_res = decode_string(data_str, LIGHT_ON_TIME)
            if 10<= decode_res <= 12:
                start_up = True
        except:
            pass

        j=0
        time_st = time.localtime()
        for i in range(len(LIGHT_ON_TIME)):
            input_time = LIGHT_ON_TIME[i].split(':')
            if time_st.tm_hour == int(input_time[0]) and time_st.tm_min == int(input_time[1]):
                j += 1
                cond_flag = True

        if j == 0:
            cond_flag = False

        if (cond_flag == True) and (cond_flag_old == False) or start_up == True:
            '''
            ## TIMER module
            print_Info( str(LIGHT_ON_TIME))
            if (0 < time.localtime().tm_hour <= 18) and (get_request_time == 0xff):
                print_Info( 'Weather Current')
                data = RequestWeatherInFo(url_current_weather,0 ,0,['main','temp'],['weather','main'])
            '''
            print_info('decode_res = %d ' % decode_res)
            if decode_res == CURRENT:
                print_Info( 'Weather Current ')
                data = RequestWeatherInFo(url_current_weather,0 ,0,['main','temp'],['weather','main'])
            elif decode_res == 12:
                SaveWeatherInFo(url_current_forecast,db_file_name,db_table_name,DB_wheather)
            else:
                print_Info( 'Weather Forcast')
                data = RequestWeatherInFo(url_current_forecast,time_delta ,get_request_time,['main','temp'],['weather','main'])
            try:
                com_val = compareTemp(DB_wheather, data['DATE'] + ' ' + data['TIME'], data['TEMP'])
                print_Info('Weather main: ' + data['WT']+'  temperature : ' + str(data['TEMP']) + 'compare temp  = ' + str(com_val))

                string_to_send = str()
                string_to_send += 'WT:%s;' %  data['WT']
                string_to_send += 'TEMP:%.2f;' % data['TEMP']
                string_to_send += 'COMP:%d' % com_val
                MQTT_publish("IOT_dat/weather", string_to_send)
            except:
                print_info('Error Occured ')
            start_up = False
        cond_flag_old = cond_flag
    except KeyboardInterrupt:
        mqtt_command.stop_flag.clear()
        mqtt_command.join()
        sys.exit()




