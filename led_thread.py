import time 
import threading
from socket import *
from common_func import *
import signal
from sock_thread import D_TIME_SESSION




b_table = ('Dark','Bright')


class DummyDeviceThread(threading.Thread):
	def __init__(self,ID,name,function, *args):
		threading.Thread.__init__(self)
		self.ID = ID
		self.name = name
		self.function = function
		self.input_tuple = tuple(value for _, value in enumerate(args))
		
		self.stop_flag = threading.Event()
		self.stop_flag.set()
		self.input_tuple = self.input_tuple + (self.stop_flag,)

	def run(self):
		print_dumDevInfo("starting " + self.name)
		#LedJarThreadLock.acquire()
		self.function(*self.input_tuple)
		#LedJarThreadLock.release()
		print_dumDevInfo( "ending" + self.name)




class LedJarTimer:
	kill_evt = 0
	def __init__(self,name,delay,fuction,*args):
		self.name = name
		#if name  
		self.delay = delay
		self.fuction = fuction
		self.args = tuple(value for _, value in enumerate(args))
		self.thread = threading.Timer(self.delay, self.handle_function)

		self.CHECK_TIME = 0
		self.SESIION_TERMINATE = False


	def handle_function(self):
		self.fuction(*self.args)
		self.thread = threading.Timer(self.delay, self.handle_function)
		self.thread.start()
		if self.kill_evt == 1:
			self.thread.cancel()


	def start(self):
		print_timerinfo ('[%s]timer start !'%self.name)
		self.thread.start()

	def cancel(self):
		print_timerinfo ('[%s]timer stop !'%self.name)
		self.kill_evt = 1
		self.thread.cancel()

	def isAlive(self):
		val = self.thread.isAlive()
		print_timerinfo ('[%s]timer status %d !'% (self.name, val))
		return val

### LEDJAR normal def function ###

def popRoomStateFromList(_device_info, _list_light,_c_light_state):
	if len(_list_light) != 0:
		print 'size of list ', len(_list_light)
		_data = _list_light.pop()
		tmp_str = lambda x:b_table[x]
		Strings = ('room light state was changed !! to %s' % tmp_str(_data[1]))
		print Strings

		_last_room_light = _data[1]
		return _last_room_light
	return 0xff
 


def checkTimeSection(t_start, t_end):
	t_clock = int(time.strftime('%H'))
	if t_clock == 0:
		t_clock = 24

	if t_start == t_end:
		print 'impossible'
		return False

	if t_start > t_end:
		if t_start <= t_clock < 24:
			return True
		elif int(time.strftime('%H')) < t_end:
			return True
		else:
			return False

	else:
		if t_start <= int(time.strftime('%H')) < t_end:
			return True
		else:
			return False

def checkTwoTimeSection(ts1,te1,ts2,te2):
	if checkTimeSection(ts1,te1) or checkTimeSection(ts2,te2):
		return True
	else:
		return False

	

###################### fuction line ######################

if __name__ == "__main__":

	def printer(para, para2):
		print ('fuck you man [%s],%d - %d'% (time.ctime(),para,para2))

	def thread_printer(para, para2, t_event):
		i= 0
		while t_event.is_set():
			if i == 5:
				exit()
			else:
				print ('fuck you man [%s],%d - %d'% (time.ctime(),para,para2))
				#time.sleep(5)


	def printer2():
		print 'ddd'

	def test(a,b):
		print a+b

	def looper(func, **kwargs):
		print kwargs
		for _, value in kwargs.iteritems():
			print 'value ', value
		func(*tuple(value for _, value in kwargs.iteritems()))

	def looper2(func, *args):
		for value in enumerate(args):
			print value
		input_tuple = tuple(value for _, value in enumerate(args))
		func(*input_tuple)
	test_list = [0]
	def _lists(_list):
		_list[0] = 1

	#ledjar timer example
	"""
	timer = 0
	i =0 
	try:
		timer.isAlive()
	except:
		print 'error'
	timer = LedJarTimer('test', 1,printer,3,4)
	timer2 = LedJarTimer('test3',2 ,printer,3,4)
	timer.start()
	timer2.start()

	while True:
		i += 1
		timer.isAlive()
		if i == 5:
			timer.cancel()

		time.sleep(5)
	"""
	#ledjarthread example
	#stop_flag = threading.Event()
	#stop_flag.set()

	thread1 = DummyDeviceThread(1,'test',thread_printer,4,3)
	thread2 = DummyDeviceThread(2,'test3',thread_printer,6,37)
	thread1.start()
	thread2.start()
	#signal.pause()

	try:
		while True:
			signal.pause()
	except (KeyboardInterrupt, SystemExit):
		thread1.stop_flag.clear()
		thread2.stop_flag.clear()
		thread1.join()
		thread2.join()

		print "exit"
		#exit()
