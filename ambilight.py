""" Ambilight: Light led strip accroding to TV screen. 
Record TV-screen with raspberry pi camera. Find rgb-values of boundary 
and light up led strip with this rgb values. To this end attach led strip 
on the back of the TV. For a good result make sure that the boundary of 
the camera capture is aligned with the screens boundary. 
Connect ledstrip to raspberry pi GPIO 18

Copyright: Tobias Becker
""" 
import neopixel
import numpy as np
import time
from picamera import PiCamera
import RPi.GPIO as GPIO
import board


def cam_setup():
    """ setup instance of PiCamera. Fix resolution, framerate, iso, ...
    :return cam: camera instance
    """
    cam = PiCamera()              # initialize camera
    h = 127#64#1024               # pixels in x-dir
    cam_res = (int(h),int(0.5*h)) # keeping the natural 3/4 resolution
    # we need to round to the nearest 16th and 32nd (requirement for picamera)
    cam_res = (int(16*np.floor(cam_res[1]/16)),int(32*np.floor(cam_res[0]/32)))

    cam.resolution = (cam_res[1], cam_res[0])
    cam.framerate = 60
    time.sleep(2)                #let the camera settle
    cam.iso = 400                # light sensitivity recommend 100...800 

    cam.shutter_speed = cam.exposure_speed

    cam.exposure_mode = 'off'
    gain_set = cam.awb_gains
    cam.awb_mode = 'off'
    cam.awb_gains = gain_set
    
    return cam

def Ambilight(cam, pixels, led_width, led_height, offset=0):
    """
    capture video via picamera and store rgb values to array with given resolution. For a fast capture use video port. 
    Then loop over the top row, right, bottom and left of the ambilight led strip one after another. To find rgb value 
    for each led make some average that fits to the number of leds in horizontal and vertical direction.
    :param cam: PiCamera object
    :param pixels: instance of neopixel to controll led strip
    :param led_width: number of leds in x-direction
    :param led_height: number of leds in y-direction
    :offset: strip starts in top row, but in the middle with offset leds before it
    """
    cam_res = np.array(str(cam.resolution).split('x')).astype(int)  # retrieve resolution from PiCamera object
    # capture image to memory 
    data = np.empty((cam_res[0], cam_res[1],3),dtype=np.uint8) # y,x and rgb
    print('start...')
    length = 2*(led_width + led_height)
    while True:
        try:
            cam.capture(data, 'rgb', use_video_port=True)
            for i in range(led_width):
                # top row leds
                start = np.int(np.floor(i*cam_res[1]/led_width))   # pixel start for i-th led
                stop = np.int(np.ceil((i+1)*cam_res[1]/led_width))
                rgb = np.mean(data[0, start:stop], axis=0)
                
                led_ind = (i-offset - 1)%length
                pixels[led_ind] = rgb.astype(int)

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
            
def main():
    """ specify number of leds, create PiCamera/neopixel instances and run Ambilight()"""    
    led_width = 71    # number of leds in x-direction
    led_height = 39   # number of leds in y-direction
    offset = 35       # strip starts in top row, but in the middle with offset leds before it

  
    # connect Neopixel to GPIO 18 pin 
    pixels = neopixel.NeoPixel(board.D18, 2*led_width + 2*led_height,brightness=0.4, auto_write=False)
    cam = cam_setup()
    
    Ambilight(cam, pixels, led_width, led_height, offset)

if __name__ == '__main__':
        print(__doc__)
        main()

