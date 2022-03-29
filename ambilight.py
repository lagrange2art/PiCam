""" first test with led strip. https://docs.circuitpython.org/projects/neopixel/en/latest/ Test for led strip with 60 led. Chose a particular led and pick r,g,b values to light up the specific led. \n ctrl-c to exit program and turn off led strip \n"""


import neopixel

import numpy as np
import time
from picamera import PiCamera
import RPi.GPIO as GPIO
import board

from matplotlib import pyplot as plt

length = 220  # actually there is last LED missing but work with symmetric pic 
pixels = neopixel.NeoPixel(board.D18, length, brightness=0.5, auto_write=False)

cam = PiCamera()               # initialize camera
h = 128#64#1024                     # pixels in x-dir
cam_res = (int(h),int(0.5*h)) # keeping the natural 3/4 resolution
# we need to round to the nearest 16th and 32nd (requirement for picamera)
cam_res = (int(16*np.floor(cam_res[1]/16)),int(32*np.floor(cam_res[0]/32)))

cam.resolution = (cam_res[1], cam_res[0])
cam.framerate = 90
time.sleep(2) #let the camera settle
cam.iso = 1#10#100
cam.shutter_speed = cam.exposure_speed
cam.exposure_mode = 'off'
gain_set = cam.awb_gains
cam.awb_mode = 'off'
cam.awb_gains = gain_set


def main():
    data = np.empty((cam_res[0], cam_res[1],3),dtype=np.uint8) # x,y and rgb
    led_height = 39
    led_width = 71
    offset = 35

    tr = 35
    #br = 74
    #bl = 145
    #tl = 184

    while True:
        try:
            
            cam.capture(data, 'rgb', use_video_port=True)
            #plt.imshow(data)
            #plt.show()
            for i in range(led_width):
                # top row leds
                start = np.int(np.floor(i*cam_res[1]/led_width))   # pixel start for i-th led
                stop = np.int(np.ceil((i+1)*cam_res[1]/led_width))
                rgb = np.mean(data[0, start:stop], axis=0)
                
                pixels[(i-offset - 1)%length] = rgb.astype(int)
            
            for i in range(led_height):
                # right column leds
                start = np.int(np.floor(i*cam_res[0]/led_height))   # pixel start for i-th led
                stop = np.int(np.ceil((i+1)*cam_res[0]/led_height))
                rgb = np.mean(data[start:stop, -1], axis=0)
                
                led_ind = (i-offset - 1 + led_width)%length               
                pixels[led_ind] = rgb.astype(int)
            
            for i in range(led_width):
                # bottom row leds
                start = np.int(np.floor(i*cam_res[1]/led_width))   # pixel start for i-th led
                stop = np.int(np.ceil((i+1)*cam_res[1]/led_width))
                rgb = np.mean(data[:,::-1,:][-1, start:stop], axis=0)
                
                led_ind = (i-offset - 1 + led_width + led_height)%length               
                pixels[led_ind] = rgb.astype(int) 
                
            for i in range(led_height):
                # left column leds
                start = np.int(np.floor(i*cam_res[0]/led_height))   # pixel start for i-th led
                stop = np.int(np.ceil((i+1)*cam_res[0]/led_height))
                rgb = np.mean(data[::-1,:,:][start:stop, 0], axis=0)
                
                led_ind = (i-offset - 1 + led_width + led_height + led_width)%length               
                pixels[led_ind] = rgb.astype(int)
                
            
            pixels.show()
           
           
        except KeyboardInterrupt:
            pixels.fill((0,0,0))
            pixels.show()
            return 0

if __name__ == '__main__':
        print(__doc__)
        main()
#main()
