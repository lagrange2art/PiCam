from matplotlib import pyplot as plt
from matplotlib.widgets import Slider, Button
import numpy as np
import time
from picamera import PiCamera
import RPi.GPIO as GPIO


class Camera(object):
	def __init__(self, cam_res, pins):
		self.cam_res = cam_res
		
		self.cam = self.cam_setup()       # initialize camera
		self.pwmRed, self.pwmGreen, self.pwmBlue = self.led_setup(pins)
		self.data = 255*np.ones((self.cam_res[0],self.cam_res[1],3),dtype=np.uint8) # x,y and rgb 
		
		self.fig = plt.figure()
		plt.subplot(121)
		self.pic = plt.imshow(self.data[::-1,::-1])
		  
		photoaxis = plt.axes([0.5, 0.025, 0.15, 0.04])         # button to take photo
		self.photobutton = Button(photoaxis, 'take pic', color='lightgoldenrodyellow', hovercolor='0.975')
		self.photobutton.on_clicked(self.video)
		
		rgbaxis = plt.axes([0.3, 0.025, 0.15, 0.04])         # button to reset value
		self.rgbbutton = Button(rgbaxis, 'rgb detect', color='lightgoldenrodyellow', hovercolor='0.975')
		self.rgbbutton.on_clicked(self.rgb_detect)
		
		releasebutton = plt.axes([0.7, 0.025, 0.15, 0.04])         # button to reset value
		self.release = Button(releasebutton, 'Release GPIO', color='red', hovercolor='0.975')
		self.release.on_clicked(self.destroy)
		
		plt.show()
	
	
	def cam_setup(self, resolution=1024):
		cam = PiCamera()               # initialize camera
		
		cam.resolution = (self.cam_res[1],self.cam_res[0])
		cam.framerate = 30
		time.sleep(2) #let the camera settle
		cam.iso = 100
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
	
	
	def video(self, event):
		plt.subplot(122)
		diff = plt.imshow(self.data)
		
		old = self.data.copy()
		
		self.cam.capture(self.data,'rgb')    # take picture to RGB
		
		print('diff %s ' % np.sum(np.abs(old - self.data)))
		print('mean data %s, std data %s ' % (np.mean(self.data), np.std(self.data))) 
		diff.set_data((self.data - np.mean(self.data)).astype(int))#np.abs(old - self.data))

		self.pic.set_data(self.data[::-1,::-1])
		self.fig.canvas.draw()
		self.fig.canvas.flush_events()

		
	def rgb_detect(self, event):
		noise = np.empty((self.cam_res[0],self.cam_res[1],3),dtype=np.uint8)
		input('rgb detect \n press enter to capture background noise (remove colors) ')
		self.cam.capture(noise, 'rgb')        
		noise = noise-np.mean(noise)    # background 'noise'
		
		self.pic.set_data(np.abs(noise[::-1,::-1]).astype(int))
		self.fig.canvas.draw()
		self.fig.canvas.flush_events()

		input("press enter to capture image")
		self.cam.capture(self.data, 'rgb')
		mean_rgb = np.mean(self.data - noise, axis=(0,1)) - np.mean(self.data)

		self.pic.set_data(np.abs((self.data - noise)[::-1,::-1]).astype(int))
		self.fig.canvas.draw()
		self.fig.canvas.flush_events()

		print('rgb %s ' % mean_rgb)
		text_rgb = np.array(['RED', 'GREEN', 'BLUE'])
		print('\n Color is %s  !!' % (text_rgb)[np.argmax(mean_rgb)])
		
		data_rgb_mean = np.mean(self.data, axis=(0,1))
		print('r,g,b %s' % data_rgb_mean)
		self.setColor(*data_rgb_mean) 

	def destroy(self, event):
		print('cleanup')
		self.pwmRed.stop()
		self.pwmGreen.stop()
		self.pwmBlue.stop()
		GPIO.cleanup()                     # Release all GPIO



def main():
	h = 64#1024                     # pixels in x-dir
	pins = [11, 12, 13]         # define the pins for R:11,G:12,B:13 

	cam_res = (int(h),int(0.75*h)) # keeping the natural 3/4 resolution
	# we need to round to the nearest 16th and 32nd (requirement for picamera)
	cam_res = (int(16*np.floor(cam_res[1]/16)),int(32*np.floor(cam_res[0]/32)))
    
	Camera(cam_res, pins)

if __name__ == '__main__':
    main()
