
""" from: https://makersportal.com/blog/2019/4/21/image-processing-using-raspberry-pi-and-python"""

from picamera import PiCamera
import numpy as np
import matplotlib.pyplot as plt
import time

def main(resolution=1024):
	h = resolution                    # pixels in x-dir
	cam_res = (int(h),int(0.75*h)) # keeping the natural 3/4 resolution
	# we need to round to the nearest 16th and 32nd (requirement for picamera)
	cam_res = (int(16*np.floor(cam_res[1]/16)),int(32*np.floor(cam_res[0]/32)))
	cam = PiCamera()               # initialize camera
	cam.resolution = (cam_res[1],cam_res[0])
	data = np.empty((cam_res[0],cam_res[1],3),dtype=np.uint8) # x,y and rgb 
	
	r_proj = np.ones((cam_res[0],cam_res[1],3), dtype=np.uint8) 
	r_proj[:,:,1:] = 0            # only r-values nonzero
	
	g_proj = np.ones((cam_res[0],cam_res[1],3), dtype=np.uint8)
	g_proj[:,:,0] = 0
	g_proj[:,:,2] = 0
	
	b_proj = np.ones((cam_res[0],cam_res[1],3), dtype=np.uint8)
	b_proj[:,:,:-1] = 0
	
	while True:
		try:
			cam.capture(data,'rgb')    # capture RGB image
			data = np.flip(data,0)     # flip y-axis
			data = np.flip(data,1)     # flip x-axis
			plt.subplot(241)
			plt.imshow(data) # plot image
			plt.subplot(242)
			plt.imshow(data*r_proj)
			plt.subplot(243)
			plt.imshow(data*g_proj)
			plt.subplot(244)
			plt.imshow(data*b_proj)
			plt.subplot(246)
			mean = np.mean(data, axis=(0,1), dtype=int)   # take mean rgb over x-y plane
			plt.title('mean rgb %s' % mean) 
			plt.imshow(np.array([[mean]]))

			
			# clear data to save memory and prevent overloading of CPU
			data = np.empty((cam_res[0],cam_res[1],3),dtype=np.uint8)
			plt.show() # show the image
			# press enter when ready to take another photo
			#input("Click to save a different plot")
			time.sleep(2)
		# pressing CTRL+C exits the loop
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
    main(resolution=256)
	
