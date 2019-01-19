"""
Use OpenCV contours for finding the line.  
   
"""

import numpy as np
import cv2 as cv

def get_position(cap):

	ret, frame = cap.read()

	imgray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
	blur = cv.GaussianBlur(imgray,(9,9),0)
	ret, thresh = cv.threshold(blur, 170, 255, 0)

	thresh = cv.erode(thresh, None, iterations=2)
	thresh = cv.dilate(thresh, None, iterations=2)

	# thresh = cv.adaptiveThreshold(blur,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY,11,2)
	contours, hierarchy = cv.findContours(thresh,cv.RETR_LIST , cv.CHAIN_APPROX_SIMPLE)

	cnts = sorted(contours, key = cv.contourArea, reverse = True)[:5] # get largest five contour area
 
	if (len(cnts)<1): 
		return float('nan')

	# find the contour which are closest to the lower edge of the frame
	distances = [c[c[:, :, 1].argmax()][0][1] for c in cnts]
	c = cnts[np.argmax(distances)]

	cv.drawContours(frame, cnts, -1, (0,255,0), 3)

	epsilon = 0.02*cv.arcLength(c,True)
	approx = cv.approxPolyDP(c,epsilon,True)
	cv.drawContours(frame,[approx],0,(0,0,255),2)
	moments = cv.moments(approx) 
	m00 = moments['m00']
	m01 = moments['m01']
	m10 = moments['m10']

	if (m00==0): 
		return float('nan')

	print('centroid ',m10/m00,m01/m00)

	# line
	# rows,cols = frame.shape[:2]
	# [vx,vy,x,y] = cv.fitLine(c, cv.DIST_L2,0,0.01,0.01)
	# lefty = int((-x*vy/vx) + y)
	# righty = int(((cols-x)*vy/vx)+y)
	# cv.line(frame,(cols-1,righty),(0,lefty),(0,255,0),2)

	# rect = cv.minAreaRect(c)
	# box = cv.boxPoints(rect)
	# box = np.int0(box)
	# print(cv.contourArea(c)) # ,box[0,1],box[1,1],box[2,1],box[3,1])


	# show the images
	cv.imshow("frame",frame)
	cv.imshow("thresh",thresh)

	return m10/m00-250

if __name__ == '__main__': 
	cap = cv.VideoCapture(0)
	while(True): 
		x = get_position(cap) 	
		print('current position ',x)
		cv.waitKey(1)


