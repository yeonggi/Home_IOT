from socket import *
from select import select
import threading
from threading import Thread, Lock
import Queue
from socket_func import *
from common_func import *
from led_thread import *
import signal
from IrData import *


connection_list = []
Device_Info = {}



HOST = ''
PORT = 9898
RX_BUFSIZE = 1024
TX_BUFSIZE = 1024
ADDR = (HOST, PORT)
SESSION_RESET_TIME=0

D_TIME_SESSION = 30

sock_m = Lock()
ir = IrDataProc();

def send_thread():
	while True:
		sock_m.acquire()	
		try:
			_socket, data = sock_q.get_nowait()
			#print str(index)+ " " + data
			#socket = connection_list[index]
			if type(_socket) == str:
				if data.find('[IOT_dat/command]') >= 0:
					_socket = findSockByDeviceName(Device_Info, '[[Master]]')
					data = data[len('[IOT_dat/command]'):]
				elif data.find('[IOT_dat/weather]') >= 0:
					_socket = findSockByDeviceName(Device_Info,_socket)
					data = data[len('[IOT_dat/weather]'):]
					print_mqttinfo('MQTT SEND')
			try:
				_socket.send(data)
			except:
				print_info ('sock send error ')
				disconnect_sock(_socket,Device_Info,connection_list)
		except Queue.Empty:
			pass
		sock_m.release()

#need mutex

def recv_thread():

	while connection_list:
		
		try:
			rd_sock, wr_sock, error_sock = select(connection_list, [], [], 10)
			for sock in rd_sock:
				if sock == connection_list[0]:
					sock_m.acquire()

					clnt_sock, addr_info = serv_sock.accept()
					connection_list.append(clnt_sock)
					
					addDeviceInfo(Device_Info,clnt_sock,'',addr_info[0])

					sock_m.release()
				else:
					sock_m.acquire()
					try:
						data = sock.recv(RX_BUFSIZE)

					except Exception as e:
						print_info('sock recv error ')
						disconnect_sock(sock,Device_Info,connection_list)
						data = 0
						pass
						
					if data:
						
						if checkCommandOrString(data):
							print_CmdOrString(str(printCommand(data)))
							result = checkRecvSessionRSP(Device_Info[sock][0],data)
							if checkSessionMsg(Device_Info,sock,data):
								#need to develope not use for LedJar
								data = data.strip()
								reset_time = getDataFromAscii(data[1:len(data)])
								_str = 'Session time will be set [%x]' % reset_time
								print_sessionifo(_str)

							elif result:
								if result == True:
									print_sessionifo("Success to get 0xe102(session check) from arduino")
								elif result == 0xff:
									print_sessionifo("Disconnect Device [%s] by Device" % Device_Info[sock][0])
									disconnect_sock(sock,Device_Info,connection_list)

							elif forceDisconnect(Device_Info, sock, data, connection_list):
								print_sessionifo("Force Disconnect Success ")
							elif getTouchDataFromDevice(data):
								pass

						else:
							if data.find('mqtt') >= 0:
								MQTT_publish(data)

							if data.find('help') >= 0:
								send_queue(sock,  PrintCommand())
							if forceDisconnectByString(Device_Info, sock, data, connection_list):
								print_sessionifo("Force Disconnect Success BY MASTER ")

							led_mode = ir.Print_IrData(data)
							if 0<led_mode < 9:
								if led_mode < 5:
									send_sock = findSockByDeviceName(Device_Info, '[[Nano]]')
									send_queue(send_sock,'\xe5%c' % chr(led_mode))
								MQTT_publish('[IR]'+str(led_mode))
							elif led_mode == 0xf:
								send_sock = findSockByDeviceName(Device_Info, '[[Nano]]')
								send_queue(send_sock,'\xe5\x00')
							
							dev = 'Nano'
							print_CmdOrString(data)
							getDeviceInfoForMaster(connection_list,Device_Info,sock,data)
							if getDeviceNameFromString(Device_Info,sock,data,connection_list) != 0xff:
								pass
							elif dev in data:
								num = getLightDataFromMaster(data,dev)
								if num != False:
									send_sock = findSockByDeviceName(Device_Info, '[['+dev+']]')
									send_queue(send_sock,'\xe5%c' % chr(num))
							else:
								pass
								#send_queue(sock, data)

					else:
						disconnect_sock(sock,Device_Info,connection_list)
					sock_m.release()
		except KeyboardInterrupt:
		# smooth close
			serv_sock.close()
			sys.exit()
	


if __name__=="__main__":

	serv_sock = socket(AF_INET, SOCK_STREAM)
	sock_opt = 1;
	serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, sock_opt);
	serv_sock.bind(ADDR)
	serv_sock.listen(10)
	connection_list.append(serv_sock)

	#sock_thread
	threading._start_new_thread(recv_thread,())
	threading._start_new_thread(send_thread,())

	#Device_Thread
	touch_sensor = DummyDeviceThread(1,'Touch',scanTouched,Device_Info)
	light_sensor = DummyDeviceThread(2,'Light',scanLightState,Device_Info)
	mqtt_service = DummyDeviceThread(3,'MQTT',MQTT_subscribe)
	touch_sensor.start()
	light_sensor.start()
	mqtt_service.start()
	
	#thread kill 
	try:
		while True:
			signal.pause()
	except (KeyboardInterrupt, SystemExit):
		touch_sensor.stop_flag.clear()
		light_sensor.stop_flag.clear()
		mqtt_service.stop_flag.clear()
		touch_sensor.join()
		light_sensor.join()
		mqtt_service.join()

