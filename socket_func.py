from common_func import *
import Queue
from threading import Thread, Lock
from led_thread import *
from sock_thread import connection_list, Device_Info
from touch_sensor import *
from light_sensor import *
import paho.mqtt.client as mqtt


sock_q = Queue.Queue()
S_timer = {}

#sock function 
#---------------------------------------------------------------------------------------------
def disconnect_sock(_sock, _device_info, _connection_list):
	global S_timer
	try:
		device_name = _device_info[_sock][0]
		print_info(' %s will be deleted'% device_name)
		del _device_info[_sock]
	except Exception as e:
		print_info('No Clinet Device name exist ')	
	
	try:
		_connection_list.remove(_sock)
		_sock.close()
	except Exception as e:
		print_info('No Socket info in Connection list ')
		return
	#kill Thread
	
	deleteTimerDic(S_timer, device_name)

	_str = ('%s was disconnected !' % device_name)
	print_info(_str) 

def forceDisconnect(_Device_info ,_sock, _data,_connection_list):
	if len(_data) == 2 and ord(_data[0]) == 0xe2 and _Device_info[_sock][0]:
		index = ord(_data[1])
		if index > 0 and index <= len(_Device_info):
			dis_sock = _Device_info.keys()[index - 1]
			if _Device_info.values()[index - 1][0] != '[[Master]]':
				disconnect_sock(dis_sock, _Device_info, _connection_list)
				return True
			else:
				send_queue(_sock,'Can not disconnect server sock and Master Clinet !!!!!')
				return False

		else:
			send_queue(_sock,'index should be 1 ~ %d' % len(_Device_info))
			return False
	return False

def forceDisconnectByString(_Device_info ,_sock, _data,_connection_list):
	if _data.find('Del')==0 and _Device_info[_sock][0]:
		index_list=0
		index =0
		try:
			index_list = _data.split()
			try:
				index = int(index_list[1])
			except:
				pass
		except:
			pass
		if index > 0 and index <= len(_Device_info):
			dis_sock = _Device_info.keys()[index - 1]
			if _Device_info.values()[index - 1][0] != '[[Master]]':
				disconnect_sock(dis_sock, _Device_info, _connection_list)
				return True
			else:
				send_queue(_sock,'Can not disconnect server sock and Master Clinet !!!!!')
				return False

		else:
			send_queue(_sock,'index should be 1 ~ %d' % len(_Device_info))
			return False
	return False

def addDeviceInfo(_device_info,sock,device_name, host_ip):
	_device_info[sock] = [device_name, host_ip]
	print_info("Device info added ")


# GetDeviceName 
def getDeviceNameFromString(_Device_info ,_sock, _data,_connection_list):
	global S_timer
	global D_TIME_SESSION
	if _data[0:2] == '[[' and ']]' in _data:
		chtmp = _data.find(']]')
		if chtmp != -1:
			device_name = _data[:chtmp+2] 
			if len(device_name) == len(_data):
				if _Device_info[_sock][0] == '':
					#check there are another device name
					dis_sock = findSockByDeviceName(_Device_info,_data[:chtmp+2])
					if dis_sock != False:
						disconnect_sock(dis_sock,_Device_info,_connection_list)
					
					_Device_info[_sock][0] = _data[:chtmp+2]

					#Session timer start 
					if _Device_info[_sock][0] == '[[Nano]]' or _Device_info[_sock][0] == '[[NMCU]]':
						S_timer[_Device_info[_sock][0]] = LedJarTimer('Session_check',D_TIME_SESSION,sendSessionMsg,_sock,_Device_info,_connection_list)
						S_timer[_Device_info[_sock][0]].CHECK_TIME = time.time()
						S_timer[_Device_info[_sock][0]].start()

					string = ('%s New DEVICE Connected ' %  _Device_info[_sock][0])
					print_info(string)
				else:
					#send_queue(_sock, _data)
					disconnect_sock(_sock,_Device_info,connection_list)

					string = ('%s Duplicate Device Disconnect' %  _Device_info[_sock][0])
					print_info(string)

		else:
			print_info('data format was wrong')
			
		return 0xff

	else:
		return 0xff




def getDeviceInfoForMaster(_connection_list,_device_info,_sock,_data):
	if _data[0:1] == 'P' and _device_info[_sock][0] == '[[Master]]':
		_str = print_deviceinfo(_device_info)
		#_str += print_connectionList(_connection_list)
		_str += print_LedJarTimerinfo(S_timer)
		#_str += print_lightinfo(Device_Info,static_light,s_light_para,last_room_light,time_state)
		send_queue(_sock,_str)
		#_sock.send(_str)
		return _str
	return False

def send_queue(_sock, data):
	try:
		#index = connection_list.index(sock)
		dataTosend = [_sock,data]
		try:
			sock_q.put(dataTosend)
		except Queue.Full:
			print_info("QUEUE FULL!!!")
	except:
		print_info("sock find error !!")
#---------------------------------------------------------------------------------------------


#session code
#---------------------------------------------------------------------------------------------
#timer
def sendSessionMsg(_sock,_Device_info, _connection_list):
	#global Device_Info, connection_list
	global S_timer
	try:
		_time = time.time() - S_timer[_Device_info[_sock][0]].CHECK_TIME
		if _time > S_timer[_Device_info[_sock][0]].delay*2 :
			
			print_sessionifo('No answer Session timer Terminate !')
			disconnect_sock(_sock,_Device_info,_connection_list)
			return

		send_queue(_sock,'\xe1\x01')
		_str = 'Send Session MSG, Time Past from Geting RSP = %d' % _time
		print_sessionifo(_str)
	except Exception as e:
		print_sessionifo('Session msg send error')
		return

def checkSessionMsg(_device_info,_sock,_data):
	if _device_info[_sock][0]:
		dat = _data.strip()
		if len(dat) == 4 and ord(dat[0]) == 0xe0:
			return True
		else:
			return False
	return False

def checkRecvSessionRSP(_device_name,_data):
	global S_timer
	if _device_name:
		dat = _data.strip()
		if len(dat) == 2 and ord(dat[0]) == 0xe1:
			if ord(dat[1]) == 0x02:
				S_timer[_device_name].CHECK_TIME = time.time()
				return True
			elif ord(dat[1]) == 0xff:
				return 0xFF
			else:
				return False
	
	return False	
#---------------------------------------------------------------------------------------------

#Touch_code 
#---------------------------------------------------------------------------------------------
def scanTouched(_device_info, t_event):
	start_time = 0
	Touch1 = TouchSensor()
	while t_event.is_set():
		click_count = 0
		t_val = Touch1.touch_time()
		click_count = Touch1.multi_click(t_val)
		if click_count > 0: 
			for key, values in _device_info.iteritems():
				if values[0] == '[[Master]]' or values[0] == '[[Nano]]':
					start_time = time.time()
					if click_count == 0xf:
						print_dumDevInfo('%ssend light off by touch' % values[0])
						send_queue(key,'\xe5\x00')
						start_time = 0
					else:
						_str = '%sClick count = %d' % (values[0],click_count)
						print_dumDevInfo(_str)
						send_queue(key,'\xe5%c' % chr(click_count))
		if start_time > 0 and (time.time() - start_time) > 10:
			for key, values in _device_info.iteritems():
				if values[0] == '[[Master]]' or values[0] == '[[Nano]]':
					send_queue(key,'\xe5\x00')
			start_time = 0

def getTouchDataFromDevice(_data):
	dat = _data.strip()
	if len(dat) == 4 and ord(dat[0]) == 0xe4:
		if ord(dat[1]) == 0x01: # if data from nano (ledjar)
			print_dumDevInfo('Nano Touch %d' % getDataFromAscii(dat[2:4]))
			return True
		else:
			return False
	return False

def getLightDataFromMaster(_data, dev):
	
	dat = _data.strip()
	try:
		num = int(_data[len(dev):len(_data)])
		return num
	except Exception as e:
		return False
	

		
#---------------------------------------------------------------------------------------------

#Light_code
#---------------------------------------------------------------------------------------------


m_timer_flag = 0
#send 
def sendLightDataToDevice(_device_info,light_state,led_command,*args):
	d_name = list()
	d_sock = list()
	l_string = ('Bright -> Dark', 'Dark -> Bright')
	for _, _d_name in enumerate(args):
			d_name.append(_d_name)

	for key, values in _device_info.iteritems():
		if values[0] in d_name:
			sockForSend = key
			if values[0] == '[[Master]]':
				print 'send master'
				_str = l_string[light_state]
				send_queue(sockForSend,_str)
				print_staticLightInfo('Data was sent to %s '% values[0])
			else:
				_str = '\xe3\x02'
				d_sock.append(sockForSend)
				send_queue(sockForSend,_str)
				print_staticLightInfo('Data was sent to %s '% values[0])

			#return True, values[0]
	if len(d_sock) > 0:
		return d_sock
	else:
		return False

# Scan Light State and send command to device if room get Bright to dark 
def scanLightState(_device_info ,t_event):
	isChange = 0
	value = 0
	static_light = 0
	light_dat_list = list()
	global m_timer_flag
	l_string = ('Bright -> Dark', 'Dark -> Bright')
	light = LightSensor()
	tenmin_timer = LedJarTimer('ten_min_timer',600,tenMinTimer,)
	tenmin_timer.start()
	S_timer['ten_min_timer'] = tenmin_timer

	while t_event.is_set():

		isChange, value = light.checkDarkBrightChange(static_light)
		if m_timer_flag == 1:
			if len(light_dat_list) == 6:
				mean = int(sum(light_dat_list)/len(light_dat_list))
				light_dat_list = list()
				print_staticLightInfo('mean is %s' % mean)

			light_dat_list.append(value)
			m_timer_flag = 0


		if isChange != 0:
			print_dumDevInfo( 'Light State Was Changed [%s]' % l_string[isChange[1]] )
			#listLightChange.append(isChange_list)
			if isChange[1] == 0:
				print_dumDevInfo('Detect Dark!! Send Command to Device')
				sock_lists = sendLightDataToDevice(_device_info,isChange[1],2,'[[Nano]]','[[Master]]')
				MQTT_publish('mqtt_get_weather')
				if sock_lists:
					if S_timer.has_key('offCMDTimer') == False:
						offCMDTimer = LedJarTimer('light_off_command_timer',10, offCommandTimer,sock_lists,'offCMDTimer')
						offCMDTimer.start()
						S_timer['offCMDTimer'] = offCMDTimer

		time.sleep(0.05)
	tenmin_timer.cancel()

#timer
def tenMinTimer():
	global m_timer_flag
	m_timer_flag = 1

def offCommandTimer(_sock,_timer_name):
	for i in _sock:
		send_queue(i,'\xe5\x00')

	deleteTimerDic(S_timer,_timer_name)


#---------------------------------------------------------------------------------------------

#mqtt_code
#---------------------------------------------------------------------------------------------

def on_connect(client, userdata, flags, rc):
		print ("Connencted with result code "+str(rc))
		client.subscribe("IOT_dat/weather")
		client.subscribe("IOT_dat/command")

def on_message(client,userdata, msg):
	print_mqttinfo(msg.topic+" : "+str(msg.payload))
	msgs = 0
	if msg.topic == 'IOT_dat/weather':
		msgs = MakeMsgToSendPISA(msg.payload)
	else:
		msgs = msg.payload
	send_queue('[[NMCU]]','['+msg.topic+']'+msgs)

def MQTT_subscribe(t_event):
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
	client.connect("127.0.0.1", 1883)
	client.loop_start()

def MQTT_publish( pub_str):
	mqttc = mqtt.Client()
	mqttc.connect("127.0.0.1", 1883)
	mqttc.publish("IOT_dat/command", pub_str)
	mqttc.loop(2)

def MakeMsgToSendPISA(msgs):
	msg_list = msgs.split(';')
	return_list = list()
	try:
		wheather_main = msg_list[0].split(':')[1]
		if wheather_main.find('Cloud') != -1:
			return_list.append('Cloud')
		elif wheather_main.find('Rain')!= -1:
			return_list.append('Rain')
		elif wheather_main.find('Snow') != -1:
			return_list.append('Snow')
		else:
			return_list.append('Clear')
	except:
		print_mqttinfo('msg error !!')

	temp = msg_list[1].split(':')[1]
	return_list.append(temp)

	comp = msg_list[2].split(':')[1]
	return_list.append(comp)

	tmp_str = '/'.join(return_list)
	tmp_str = '<'+tmp_str+'>'
	print tmp_str

	return tmp_str
#---------------------------------------------------------------------------------------------
