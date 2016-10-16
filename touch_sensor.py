import Adafruit_BBIO.GPIO as GPIO
import time
import subLibFuc



class TouchSensor():
	def __init__(self):
		GPIO.setup("P9_12", GPIO.IN)
		self.old_val = 0
		self.val = 0
		self.start_time = 0
		self.end_time = 0

		self.c_start_time =0 
		self.c_ending_time =0 
		self.click_count =0 

	def checkTouched(self):
		_val = 0xff
		self.val = GPIO.input("P9_12")
		if(self.old_val != self.val):	
			if self.val:
				#print "HIGH"
				_val = 1
			else:
				#print "LOW"
				_val = 0

		self.old_val = self.val
		return _val		

	def touch_time(self):
		return_val = 0
		touched = self.checkTouched()
		if touched == 1 and self.start_time == 0:
			print 'touched'
			self.start_time = time.time()
		elif self.start_time > 0 and not touched:
			print 'releasd'
			self.end_time = time.time()
			return_val = self.end_time - self.start_time
			self.end_time = 0
			self.start_time = 0
			return return_val
		return 0

	def multi_click(self, _time):
		return_val = 0
		TOUCH_TIME = 0.4
		if 0 < _time < TOUCH_TIME:
			self.click_count += 1
			if self.c_start_time == 0:
				self.c_start_time = time.time()

			self.c_ending_time = TOUCH_TIME*self.click_count
#		elif _time > 0: 
#			return_val = self.click_count
#			self.c_start_time = 0
#			self.c_ending_time =0
#			self.click_count = 0
		elif TOUCH_TIME <= _time:
			return_val = 0xf
		
		elif self.c_start_time > 0 and time.time() - self.c_start_time > self.c_ending_time:
			return_val = self.click_count
			self.c_start_time = 0
			self.c_ending_time =0
			self.click_count = 0

		return return_val


		#GPIO.cleanup()



if __name__ == "__main__":
	T = TouchSensor()
	touch = 0
#	while True:
		#touch = T.checkTouched()
		#if touch != 0xff:
		#	print touch
	while True:
		touched_time = T.touch_time()
		if  touched_time > 0:
			print touched_time
		click_count = T.multi_click(touched_time)
		if click_count > 0:
			print click_count



