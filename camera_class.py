# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 13:25:40 2024

@author: jdemas
"""

from simple_pyspin import Camera,list_cameras
import os
from datetime import datetime
import math

class cam:
    
    def __init__(self):
        cams = list_cameras() #list all FLIR cameras connected to the computer
        ncams = len(cams) 

        self.img_array=[[] for _ in range(ncams)] #records grabbed frames

        self.camera_names=['Camera 1']*ncams #Records assigned camera names
        self.video_path='desktop' #placeholder for video path untill set by the GUI
        self.experiment_name='experiment' #place holder for animal name untill set by the GUI

        self.ncams = ncams #Number of connected cameras

        self.cam = [0]*ncams #array for camera object
        
        #Create arrays for storing maximum and minimum values for each camera
        self.widthMx = [0]*ncams
        self.widthMn = [0]*ncams
        
        self.heightMx = [0]*ncams
        self.heightMn = [0]*ncams
        
        self.xcropMx = [0]*ncams
        self.xcropMn = [0]*ncams
        
        self.ycropMx = [0]*ncams
        self.ycropMn = [0]*ncams
        
        self.gainMx = [0]*ncams
        self.gainMn = [0]*ncams
        
        self.expMx = [0]*ncams
        self.expMn = [0]*ncams
        
        self.serial = [0]*ncams #Camera serial number array
   
    
    def initialize(self): #This function initiliases each camera, and sets default value of its frames to maximum possible. It also sets gain and exposure value to half maximum
        
        for i in range(self.ncams):
            self.cam[i] = Camera(i) #Assign a camera object to each index of the camera array
            self.cam[i].init() #initialize cameras

            #Set all starting parameters to default max and minimum values
            
            self.widthMx[i] = self.cam[i].get_info('Width')['max']
            self.widthMn[i] = self.cam[i].get_info('Width')['min']
            
            self.heightMx[i] = self.cam[i].get_info('Height')['max']
            self.heightMn[i] = self.cam[i].get_info('Height')['min']
            
            self.xcropMx[i] = self.cam[i].get_info('OffsetX')['max']
            self.xcropMn[i] = self.cam[i].get_info('OffsetX')['min']
            
            self.ycropMx[i] = self.cam[i].get_info('OffsetY')['max']
            self.ycropMn[i] = self.cam[i].get_info('OffsetY')['min']
            
            self.cam[i].GainAuto = 'Off'   
            self.gainMx[i] = self.cam[i].get_info('Gain')['max']
            self.gainMn[i] = self.cam[i].get_info('Gain')['min']
            
            self.cam[i].ExposureAuto = 'Off'
            self.expMx[i] = self.cam[i].get_info('ExposureTime')['max']
            self.expMn[i] = self.cam[i].get_info('ExposureTime')['min']
            
            try:
                self.cam[i].AcquisitionFrameRateAuto = 'Off'
                self.cam[i].AcquisitionFrameRateEnabled = True
            except:
                self.cam[i].AcquisitionFrameRateEnable = True

            self.cam[i].OffsetX=self.cam[i].get_info('OffsetX')['min']
            self.cam[i].OffsetY=self.cam[i].get_info('OffsetY')['min']
            self.cam[i].Height=self.cam[i].get_info('Height')['max']
            self.cam[i].Width=self.cam[i].get_info('Width')['max']
            if (int(self.cam[i].get_info('ExposureTime')['max'])/2)<5000:
                self.cam[i].ExposureTime=int(self.cam[i].get_info('ExposureTime')['max'])/2
            else:
                self.cam[i].ExposureTime=5000
            self.cam[i].Gain=int(self.cam[i].get_info('Gain')['max'])/2
            
            self.serial[i] = self.cam[i].get_info('DeviceSerialNumber')['value']
            
    def close(self): #This function closes any active camera
        for i in range(self.ncams):
            self.cam[i].close()
            
 

    def set_running_flag(self,camIdx,val): #This function keeps a track of if a cmaera is reading actively
        self.running_flag[camIdx]=val

    def set_writing_flag(self,camIdx,val): #This function keeps a track of if a camera is writing actively
        self.writing_flag[camIdx]=val

    def setGain(self,camIdx,val): #This function sets the gain value for a camera in the cam array at index camIdx to user input value
        
        val=val*(int(self.gainMx[camIdx])-int(self.gainMn[camIdx]))/100 #take in user input value and convert it to from percentage to real value then set it
        val=int(self.gainMn[camIdx])+val

        #This part will make sure input values dont exceed limits
        if val>self.gainMx[camIdx]:
            val = self.gainMx[camIdx]
        elif val<self.gainMn[camIdx]:
            val = self.gainMn[camIdx]
        
        self.cam[camIdx].Gain = int(val) #assign the new gain value
        
    def setExp(self,camIdx,val): #This function sets the exposure value for a camera in the cam array at index camIdx to user input value
        
         #This part will make sure input values dont exceed limit
        if val>self.expMx[camIdx]:
            self.cam[camIdx].ExposureTime = self.expMx[camIdx]
        elif val<self.expMn[camIdx]:
            self.cam[camIdx].ExposureTime = self.expMn[camIdx]
        else:
            try:
                self.cam[camIdx].ExposureTime = int(val) #assign the new exposure value
            except:
                pass
        
    def setframeRate(self,camIdx,val):  #This function sets the framerate for a camera in the cam array at index camIdx to user input value
        self.cam[camIdx].AcquisitionFrameRate = val
        
    def setFrameSize(self,camIdx,cropVec):  #This function sets the framesize for a camera in the cam array at index camIdx to user input value

        self.cam[camIdx].Height=self.cam[camIdx].get_info('Height')['max']
        self.cam[camIdx].Width=self.cam[camIdx].get_info('Width')['max']

        #Then input vector cropVec is in the order [x-offset, width, y-offset, height]

        #each of the following portions of the code will examine input values to make sure they are in range. In cases of x and y offset, the input values must be in multiples of 
        #min allowed value for FLIR cameras, which this function will naturally handle

        width = self.widthMn[camIdx]*(math.floor(cropVec[1]/self.widthMn[camIdx]))
        if width<self.widthMn[camIdx]:
            width=self.widthMn[camIdx]
        elif width>self.widthMx[camIdx]:
            width=self.widthMx[camIdx]

        height = self.heightMn[camIdx]*(math.floor(cropVec[3]/self.heightMn[camIdx]))
        if height<self.heightMn[camIdx]:
            height=self.heightMn[camIdx]
        elif height>self.heightMx[camIdx]:
            height=self.heightMx[camIdx]

        offsetx = self.widthMn[camIdx]*(math.floor(cropVec[0]/self.widthMn[camIdx]))
        if offsetx<self.xcropMn[camIdx]:
            offsetx=self.xcropMn[camIdx]
        elif (offsetx+width)>self.widthMx[camIdx]:
            offsetx=self.widthMx[camIdx]-width

        offsety = self.heightMn[camIdx]*(math.floor(cropVec[2]/self.heightMn[camIdx]))
        if offsety<self.ycropMn[camIdx]:
            offsety=self.ycropMn[camIdx]
        elif (offsety+height)>self.heightMx[camIdx]:
            offsety=self.heightMx[camIdx]-height


        width = self.widthMn[camIdx]*(math.floor(width/self.widthMn[camIdx]))
        height = self.heightMn[camIdx]*(math.floor(height/self.heightMn[camIdx]))
        offsetx = self.widthMn[camIdx]*(math.floor(offsetx/self.widthMn[camIdx]))
        offsety = self.heightMn[camIdx]*(math.floor(offsety/self.heightMn[camIdx]))

        #set new values for frame region
        self.cam[camIdx].Width = width
        self.cam[camIdx].Height = height
        self.cam[camIdx].OffsetX= offsetx
        self.cam[camIdx].OffsetY= offsety



    def get_OffsetX(self,camIdx): #this function will return set offset x
        temp=self.cam[camIdx]
        return temp.OffsetX


    def get_OffsetY(self,camIdx): #this function will return set offset y
        temp=self.cam[camIdx]
        return temp.OffsetY


    def get_Height(self,camIdx): #this function will return set height
        temp=self.cam[camIdx]
        return temp.Height

    def get_Width(self,camIdx): #this function will return set width
        temp=self.cam[camIdx]
        return temp.Width
        
    def get_Gain(self,camIdx): #this function will return set gain in terms of percentage
        temp=self.cam[camIdx]
        val=temp.Gain
        val=100*(val-int(self.gainMn[camIdx]))/(int(self.gainMx[camIdx])-int(self.gainMn[camIdx]))        
        return math.floor(val)

    def get_Exposure(self,camIdx): #this function will return set exposure time
        temp=self.cam[camIdx]
        return math.floor(temp.ExposureTime) 

    def start(self,camIdx): #this function will start the camera
        self.cam[camIdx].start()
        
    def stop(self,camIdx): #this function will stop the camera
        self.cam[camIdx].stop()

    def getFrame(self,camIdx): #this function will instruct the camera to acquire a frame and store it in the array im

        im = self.cam[camIdx].get_array()

        return im
            
