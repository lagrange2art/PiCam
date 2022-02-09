import numpy as np
import time
from picamera import PiCamera
import RPi.GPIO as GPIO


class LEDctrl(object):
	def __init__(self, cam_res, pins):
		self.cam_res = cam_res
		
		self.cam = self.cam_setup()       # initialize camera
		self.pwmRed, self.pwmGreen, self.pwmBlue = self.led_setup(pins)
		self.data = np.empty((self.cam_res[0],self.cam_res[1],3),dtype=np.uint8) # x,y and rgb 
		
	
	def cam_setup(self):
		cam = PiCamera()               # initialize camera
		
		cam.resolution = (self.cam_res[1],self.cam_res[0])
		cam.framerate = 60
		time.sleep(2) #let the camera settle
		cam.iso = 1#10#100
		cam.shutter_speed = cam.exposure_speed
		cam.exposure_mode = 'off'
		gain_set = cam.awb_gains
		cam.awb_mode = 'off'
		cam.awb_gains = gain_set
		
		return cam
		
	def led_setup(self, pins):
		freq = 100
		
		GPIO.setmode(GPIO.BOARD)       # use PHYSICAL GPIO Numbering
		GPIO.setup(pins, GPIO.OUT)     # set RGBLED pins to OUTPUT mode
		GPIO.output(pins, GPIO.HIGH)   # make RGBLED pins output HIGH level
		pwmRed = GPIO.PWM(pins[0], freq)      # set PWM Frequence to 2kHz
		pwmGreen = GPIO.PWM(pins[1], freq)  # set PWM Frequence to 2kHz
		pwmBlue = GPIO.PWM(pins[2], freq)    # set PWM Frequence to 2kHz
		pwmRed.start(100)      # set initial Duty Cycle to 0
		pwmGreen.start(100)
		pwmBlue.start(100)
		
		return pwmRed, pwmGreen, pwmBlue
	
	
	def setColor(self,r_val,g_val,b_val):      # change duty cycle for three pins to r_val,g_val,b_val
		""" param: rgb values 0 ... 255, find corresponding, duty cycle"""
		r_dc = 100 - (np.mean(self.data[:,:,0])/255)*100
		g_dc = 100 - (np.mean(self.data[:,:,1])/255)*100
		b_dc = 100 - (np.mean(self.data[:,:,2])/255)*100
		
		self.pwmRed.ChangeDutyCycle(r_dc)     # change pwmRed duty cycle to r_val
		self.pwmGreen.ChangeDutyCycle(g_dc)   
		self.pwmBlue.ChangeDutyCycle(b_dc)
	
	
	def calibrate(self):
		cycles = 10
		input('calibrate to RED ')
		cal_red = np.zeros(3)
		for i in range(cycles):
			self.cam.capture(self.data, 'rgb')
			cal_red += 1/cycles * np.mean(self.data, axis=(0,1))
		print('RED calibrate %s' % cal_red)
		
		input('calibrate to GREEN ')
		cal_green = np.zeros(3)
		for i in range(cycles):
			self.cam.capture(self.data, 'rgb')
			cal_green += 1/cycles * np.mean(self.data, axis=(0,1))
		print('GREEN calibrate %s' % cal_green)
		
		input('calibrate to BLUE ')
		cal_blue = np.zeros(3)
		for i in range(cycles):
			self.cam.capture(self.data, 'rgb')
			cal_blue += 1/cycles * np.mean(self.data, axis=(0,1))
		print('BLUE calibrate %s' % cal_blue)
			
	
	
	def rgb_detect(self):
		
		while True:
			try:
				self.cam.capture(self.data, 'rgb', use_video_port=True)
				mean_rgb = np.mean(self.data, axis=(0,1)) 

				self.setColor(*mean_rgb) 
			except KeyboardInterrupt:
				self.destroy()
				break

	def destroy(self):
		print('cleanup')
		self.pwmRed.stop()
		self.pwmGreen.stop()
		self.pwmBlue.stop()
		GPIO.cleanup()                     # Release all GPIO



def main():
	h = 128#64#1024                     # pixels in x-dir
	pins = [11, 12, 13]         # define the pins for R:11,G:12,B:13 

	cam_res = (int(h),int(0.75*h)) # keeping the natural 3/4 resolution
	# we need to round to the nearest 16th and 32nd (requirement for picamera)
	cam_res = (int(16*np.floor(cam_res[1]/16)),int(32*np.floor(cam_res[0]/32)))
    
	led = LEDctrl(cam_res, pins)
	led.rgb_detect()
	#led.calibrate()
	
if __name__ == '__main__':
    main()
