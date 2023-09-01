import tkinter as tk
from tkinter import ttk
import threading
from threading import Thread
from tkinter import filedialog
from simple_pyspin import Camera,list_cameras
from PIL import Image
import os
import cv2
import sys
import pandas as pd
from os import listdir
import glob
import numpy as np
import math
import time
import csv
from datetime import datetime
from tkinter import messagebox
import gc
###################################################################################
# Threads
def threading():
    t=Thread(target=stop_stream)
    t.start()

def threading1():
    t1=Thread(target=start_stream)
    t1.start()


def crop_thread():
    t4=Thread(target=Stream_camera)
    t4.start()

def StopCam2():
    t2=Thread(target=Stop_stream_camera)
    t2.start()

def record_start():
    t3=Thread(target=record_sync)
    t3.start()

def cam1thread(im_ar):
    t5=Thread(target=Cam1write,args=(im_ar,))
    t5.start()

def cam2thread(im_ar):
    t6=Thread(target=Cam2write,args=(im_ar,))
    t6.start()

def cam3thread(im_ar):
    t7=Thread(target=Cam3write,args=(im_ar,))
    t7.start()


def write_video():
    global ncam
    t8=Thread(target=write_video1)
    t8.start()
    if ncam>1:
        t9=Thread(target=write_video2)
        t9.start()
    if ncam>2:
        t10=Thread(target=write_video3)
        t10.start()

def abort_thread():
    t4=Thread(target=abort_record)
    t4.start()

###################################################################################

def Cam1write(im_ar):
    global opdir1
    global running_flag1
    running_flag1=1
    output_dir=opdir1
    n=int(len(im_ar))
    height,width=im_ar[0].shape
    size = (width,height)
    count=1 

    item=str('behavcam_')+str(count-1)+str('.avi')


    if os.path.exists(os.path.join(output_dir, item)):
        flag_name_check=0
        while flag_name_check==0:
            count=count+1
            item=str('behavcam_')+str(count-1)+str('.avi')
            if not os.path.exists(os.path.join(output_dir, item)):
                flag_name_check=1


    item=str('behavcam_')+str(count-1)+str('.avi') 
    count=count+1
    
    out = cv2.VideoWriter(os.path.join(output_dir, item), cv2.VideoWriter_fourcc(*'MJPG'), 30, size, False)

    for i in range(n):
        out.write(im_ar[i])
    out.release()
    running_flag1=0


def Cam2write(im_ar):
    global opdir2
    global running_flag2
    running_flag2=1
    output_dir=opdir2
    n=int(len(im_ar))
    height,width=im_ar[0].shape
    size = (width,height)
    count=1 

    item=str('behavcam_')+str(count-1)+str('.avi')


    if os.path.exists(os.path.join(output_dir, item)):
        flag_name_check=0
        while flag_name_check==0:
            count=count+1
            item=str('behavcam_')+str(count-1)+str('.avi')
            if not os.path.exists(os.path.join(output_dir, item)):
                flag_name_check=1


    item=str('behavcam_')+str(count-1)+str('.avi') 
    count=count+1
    
    out = cv2.VideoWriter(os.path.join(output_dir, item), cv2.VideoWriter_fourcc(*'MJPG'), 30, size, False)

    for i in range(n):
        out.write(im_ar[i])
    out.release()
    running_flag2=0

def Cam3write(im_ar):
    global opdir3
    global running_flag3
    running_flag3=1
    output_dir=opdir3
    n=int(len(im_ar))
    height,width=im_ar[0].shape
    size = (width,height)
    count=1 

    item=str('behavcam_')+str(count-1)+str('.avi')


    if os.path.exists(os.path.join(output_dir, item)):
        flag_name_check=0
        while flag_name_check==0:
            count=count+1
            item=str('behavcam_')+str(count-1)+str('.avi')
            if not os.path.exists(os.path.join(output_dir, item)):
                flag_name_check=1


    item=str('behavcam_')+str(count-1)+str('.avi') 
    count=count+1
    
    out = cv2.VideoWriter(os.path.join(output_dir, item), cv2.VideoWriter_fourcc(*'MJPG'), 30, size, False)

    for i in range(n):
        out.write(im_ar[i])
    out.release()
    running_flag3=0

###################################################################################

# Camera Select Options
options = [
    "Camera 1",
    "Camera 2",
    "Camera 3"
]

fps_options = [15,30,45,60]



def get_length(val):
  return val[1]

def connect():
    global ncam 
    global cama
    global crops
    global gains
    global exposures
    global cam_serial

    cama=[]
    
    ncam=len(list_cameras())
    camb=[[]*2]*ncam

    for i in range(ncam):
        cam_temp=Camera(i)
        cam_temp.init()
        serial=cam_temp.get_info('DeviceSerialNumber')['value']
        camb[i]=[i,int(serial)]
        cam_temp.Width = cam_temp.get_info('Width')['max']
        cam_temp.Height = cam_temp.get_info('Height')['max']
        cam_temp.OffsetX = cam_temp.get_info('OffsetX')['min']
        cam_temp.OffsetY = cam_temp.get_info('OffsetY')['min']
        cam_temp.close()

    camb.sort(key=get_length)
    
    cam_serial = [t[0] for t in camb]

    update_label=str(str("Number of cameras=")+str(ncam))
    camera_deets.config(text=update_label)
    for n in range(ncam):
        cama.append([])
    crops=[[]*4]*ncam   
    gains=[[]*1]*ncam
    exposures=[[]*1]*ncam

    for i in range(ncam):
        crops[i]=[0,0,0,0]
        gains[i]=[0]
        exposures[i]=[0]

    for i in range(ncam):
        cama[i]=Camera(int(i))
        cam=cama[int(i)]
        cam.init()
        width = cam.get_info('Width')['max']
        height = cam.get_info('Height')['max']
        xcrop = cam.get_info('OffsetX')['min']
        ycrop = cam.get_info('OffsetY')['min']
        crops[i]=[xcrop,width,ycrop,height]
        gains[i]=[50]
        exposures[i]=[1000]
        cam.close()


# Camera Select Function

def select_camera():
    global cam_idx
    global camera_name
    global cam_serial
    global crops
    global gains
    global exposures
    selected = choose.get()
    cropx_entry.delete(0, tk.END)
    cropy_entry.delete(0, tk.END)
    cropwidth_entry.delete(0, tk.END)
    cropheight_entry.delete(0, tk.END)
    # fps_entry.delete(0, tk.END)
    time_entry.delete(0,tk.END)
    Gain_entry.delete(0,tk.END)
    Gain_entry.insert(0,50)
    Exposure_entry.delete(0,tk.END)
    Exposure_entry.insert(0,1000)
    if selected == options[0]:
        cam_idx=cam_serial[0]
        [xcrop,width,ycrop,height]=crops[cam_idx]
        [gain]=gains[cam_idx]
        [exp]=exposures[cam_idx]
        cam_temp=Camera(int(cam_idx))
        cam_temp.init()
        serial=cam_temp.get_info('DeviceSerialNumber')['value']
        update_label=str(str("Serial Number:\n ")+str(serial))
        camera_serial.config(text=update_label)
        camera_name='Camera '+ str(serial)
        cropx_entry.delete(0, tk.END)
        cropy_entry.delete(0, tk.END)
        cropwidth_entry.delete(0, tk.END)
        cropheight_entry.delete(0, tk.END)
        cropx_entry.insert(0,xcrop)
        cropy_entry.insert(0,ycrop)
        cropwidth_entry.insert(0,width)
        cropheight_entry.insert(0,height)
        Gain_entry.delete(0,tk.END)
        Gain_entry.insert(0,gain)
        Exposure_entry.delete(0,tk.END)
        Exposure_entry.insert(0,exp)         
        cam_temp.close()
        
    if selected == options[1]:
        cam_idx=cam_serial[1]
        [xcrop,width,ycrop,height]=crops[cam_idx]
        [gain]=gains[cam_idx]
        [exp]=exposures[cam_idx]
        cam_temp=Camera(int(cam_idx))
        cam_temp.init()
        serial=cam_temp.get_info('DeviceSerialNumber')['value']
        update_label=str(str("Serial Number:\n ")+str(serial))
        camera_serial.config(text=update_label)
        camera_name='Camera '+ str(serial)
        cropx_entry.delete(0, tk.END)
        cropy_entry.delete(0, tk.END)
        cropwidth_entry.delete(0, tk.END)
        cropheight_entry.delete(0, tk.END)
        cropx_entry.insert(0,xcrop)
        cropy_entry.insert(0,ycrop)
        cropwidth_entry.insert(0,width)
        cropheight_entry.insert(0,height)
        Gain_entry.delete(0,tk.END)
        Gain_entry.insert(0,gain)
        Exposure_entry.delete(0,tk.END)
        Exposure_entry.insert(0,exp)  
        cam_temp.close()

    if selected == options[2]:
        cam_idx=cam_serial[2]
        [xcrop,width,ycrop,height]=crops[cam_idx]
        [gain]=gains[cam_idx]
        [exp]=exposures[cam_idx]
        cam_temp=Camera(int(cam_idx))
        cam_temp.init()
        serial=cam_temp.get_info('DeviceSerialNumber')['value']
        update_label=str(str("Serial Number:\n ")+str(serial))
        camera_serial.config(text=update_label)
        camera_name='Camera '+ str(serial)
        cropx_entry.delete(0, tk.END)
        cropy_entry.delete(0, tk.END)
        cropwidth_entry.delete(0, tk.END)
        cropheight_entry.delete(0, tk.END)
        cropx_entry.insert(0,xcrop)
        cropy_entry.insert(0,ycrop)
        cropwidth_entry.insert(0,width)
        cropheight_entry.insert(0,height)
        Gain_entry.delete(0,tk.END)
        Gain_entry.insert(0,gain)
        Exposure_entry.delete(0,tk.END)
        Exposure_entry.insert(0,exp)  
        cam_temp.close()
        

def Stream_camera():
    global flag_stop
    flag_stop = 0
    global cam_idx
    global camera_name
    global cama
    global crops
    global gains
    global exposures

    stream_camerabtn.config(state="disabled")

    selected = choose.get()
    if selected == options[0]:
        cam_idx=cam_serial[0]
    if selected == options[1]:
        cam_idx=cam_serial[1]
    if selected == options[2]:
        cam_idx=cam_serial[2]
    
    cama[cam_idx]=Camera(int(cam_idx))
    cam=cama[int(cam_idx)]
    
    cam.init()
    
    cam.GainAuto = 'Off'
    gain=int(Gain_entry.get())
    gain_min=int(cam.get_info('Gain')['min'])
    gain_max=int(cam.get_info('Gain')['max'])
    gain=gain*(gain_max-gain_min)/100
    gain=gain_min+gain
    
    

    
    cv2.namedWindow(camera_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(camera_name, 850, 500)
    
    if len(cropx_entry.get()) == 0:
            xcrop=cam.get_info('OffsetX')['min']
    else:
        xcrop=int(cropx_entry.get())
        temp=xcrop/4
        temp=math.floor(temp)
        xcrop=temp*4

    if xcrop<cam.get_info('OffsetX')['min']:
        xcrop=cam.get_info('OffsetX')['min']
    if xcrop>cam.get_info('OffsetX')['max']:
        xcrop=cam.get_info('OffsetX')['max']

    if len(cropy_entry.get()) == 0:
        ycrop=cam.get_info('OffsetY')['min']
    else:
        ycrop=int(cropy_entry.get())
        temp=ycrop/4
        temp=math.floor(temp)
        ycrop=temp*4

    if ycrop<cam.get_info('OffsetY')['min']:
        ycrop=cam.get_info('OffsetY')['min']
    if ycrop>cam.get_info('OffsetY')['max']:
        ycrop=cam.get_info('OffsetY')['max']


    if len(cropwidth_entry.get()) == 0:
        width=cam.get_info('Width')['max']
    else:
        width=int(cropwidth_entry.get())
        temp=width/32
        temp=math.floor(temp)
        width=temp*32

    if width<cam.get_info('Width')['min']:
        width=cam.get_info('Width')['min']
    if width>cam.get_info('Width')['max']:
        width=cam.get_info('Width')['max']

    if len(cropheight_entry.get()) == 0:
        height=cam.get_info('Height')['max']
    else:
        height=int(cropheight_entry.get())
        temp=height/4
        temp=math.floor(temp)
        height=temp*4
    
    if height<cam.get_info('Height')['min']:
        height=cam.get_info('Height')['min']
    if height>cam.get_info('Height')['max']:
        height=cam.get_info('Height')['max']
    
    crops[cam_idx]=[xcrop,width,ycrop,height]
    
    cam.ExposureAuto = 'Off'
    if len(Exposure_entry.get())>0:
        exp=int(Exposure_entry.get())
        if exp>cam.get_info('ExposureTime')['max']:
            exp=cam.get_info('ExposureTime')['max']
        elif exp<cam.get_info('ExposureTime')['min']:
            exp=cam.get_info('ExposureTime')['min']
        else:
            cam.ExposureTime = exp
    else: 
         cam.ExposureTime=1000


    try:
        cam.AcquisitionFrameRateAuto = 'Off'
        cam.AcquisitionFrameRateEnabled = True
    except:
        cam.AcquisitionFrameRateEnable = True
    cam.AcquisitionFrameRate = 30

    cam.Width = crops[cam_idx][1]
    cam.Height = crops[cam_idx][3]
    cam.OffsetX = crops[cam_idx][0]
    cam.OffsetY = crops[cam_idx][2]
    cam.Gain = int(gain)
    cam.start()

    update_label=str(str("Frame Size and Location:\n X=")+str(xcrop)+str(", Y= ")+str(ycrop)+str("\n Height= ")+str(height)+str(", Width= ")+str(width))
    frame_size.config(text=update_label)

    prev_gain=gain
    prev_exposure=exp

    serial=cam.get_info('DeviceSerialNumber')['value']
    update_label=str(str("Serial Number:\n ")+str(serial))
    camera_serial.config(text=update_label)


    while True:
        if len(Gain_entry.get())>0:
            gain=int(Gain_entry.get())
            gain=gain*(gain_max-gain_min)/100
            gain=gain_min+gain

        if gain!=prev_gain:
            prev_gain=gain
            cam.stop()
            cam.Gain=int(gain)
            cam.start()

        
        if len(Exposure_entry.get())>0:
            exp=int(Exposure_entry.get())
            
            
        if exp!=prev_exposure and len(Exposure_entry.get())>0:
            if exp>cam.get_info('ExposureTime')['max']:
                exp=1000
            if exp<cam.get_info('ExposureTime')['min']:
                exp=100
            prev_exposure=exp
            cam.stop()
            cam.ExposureTime=int(exp)
            cam.start()
       


        if len(cropx_entry.get()) > 0:
            new_x_crop=int(cropx_entry.get())
            temp=new_x_crop/4
            temp=math.floor(temp)
            new_x_crop=temp*4

        if new_x_crop!=xcrop and len(cropx_entry.get()) > 0:
            xcrop=new_x_crop
            if xcrop<cam.get_info('OffsetX')['min']:
                xcrop=cam.get_info('OffsetX')['min']
            if xcrop>cam.get_info('OffsetX')['max']:
                xcrop=cam.get_info('OffsetX')['max']

            cam.stop()
            cam.OffsetX=xcrop
            if (xcrop+width)>cam.get_info('Width')['max']:
                diff=(xcrop+width)-cam.get_info('Width')['max']
                width_adj=width-diff
                temp=width_adj/32
                temp=math.floor(temp)
                width_adj=temp*32
                cam.Width=width_adj

            cam.start()

        if len(cropy_entry.get()) > 0:
            new_y_crop=int(cropy_entry.get())
            temp=new_y_crop/4
            temp=math.floor(temp)
            new_y_crop=temp*4

        if new_y_crop!=ycrop and len(cropy_entry.get()) > 0:
            ycrop=new_y_crop
            if ycrop<cam.get_info('OffsetY')['min']:
                ycrop=cam.get_info('OffsetY')['min']
            if ycrop>cam.get_info('OffsetY')['max']:
                ycrop=cam.get_info('OffsetY')['max']
            cam.stop()
            cam.OffsetY=ycrop
            if (ycrop+height)>cam.get_info('Height')['max']:
                diff=(ycrop+height)-cam.get_info('Height')['max']
                height_adj=height-diff
                temp=height_adj/2
                temp=math.floor(temp)
                height_adj=temp*2
                cam.Height=height_adj


            cam.start()


        if len(cropwidth_entry.get()) > 0:
            new_width=int(cropwidth_entry.get())
            temp=new_width/32
            temp=math.floor(temp)
            new_width=temp*32

        if new_width!=width and len(cropwidth_entry.get()) > 0:
            width=new_width
            if width<cam.get_info('Width')['min']:
                width=cam.get_info('Width')['min']
            if width>cam.get_info('Width')['max']:
                width=cam.get_info('Width')['max']
            cam.stop()
            cam.Width=width
            cam.start()

        if len(cropheight_entry.get()) > 0:
            new_height=int(cropheight_entry.get())
            temp=new_height/4
            temp=math.floor(temp)
            new_height=temp*4

        if new_height!=height and len(cropheight_entry.get()) > 0:
            height=new_height
            if height<cam.get_info('Height')['min']:
                height=cam.get_info('Height')['min']
            if height>cam.get_info('Height')['max']:
                height=cam.get_info('Height')['max']
            cam.stop()
            cam.Height=height
            cam.start()


        imgs_temp = cam.get_array()
        cv2.imshow(camera_name,imgs_temp)
        cv2.waitKey(5)
        if flag_stop==1:
            break

    
    cam.stop()
    gain=int(Gain_entry.get())
    crops[cam_idx]=[xcrop,width,ycrop,height]
    gains[cam_idx]=[gain]
    exposures[cam_idx]=[exp]
    cam.close()
    del imgs_temp
    cv2.destroyAllWindows()
    flag_stop=0
    stream_camerabtn.config(state="normal")

def Stop_stream_camera():
    global flag_stop
    flag_stop=1




def reset_camera():
    global ncam 
    global cama
    global crops
    global gains
    global exposures
    global cam_serial


    crop_thread()
    time.sleep(1)
    StopCam2()

    selected = choose.get()
    if selected == options[0]:
        cam_idx=cam_serial[0]
    if selected == options[1]:
        cam_idx=cam_serial[1]
    if selected == options[2]:
        cam_idx=cam_serial[2]
    
    cama[cam_idx]=Camera(int(cam_idx))
    cam=cama[int(cam_idx)]
    
    cam.init()
    width = cam.get_info('Width')['max']
    height = cam.get_info('Height')['max']
    xcrop = cam.get_info('OffsetX')['min']
    ycrop = cam.get_info('OffsetY')['min']
    crops[cam_idx]=[xcrop,width,ycrop,height]
    gains[cam_idx]=[50]
    exposures[cam_idx]=[1000]
    cam.close()
    gain=50
    exp=1000
    cropx_entry.delete(0, tk.END)
    cropy_entry.delete(0, tk.END)
    cropwidth_entry.delete(0, tk.END)
    cropheight_entry.delete(0, tk.END)
    cropx_entry.insert(0,xcrop)
    cropy_entry.insert(0,ycrop)
    cropwidth_entry.insert(0,width)
    cropheight_entry.insert(0,height)
    Gain_entry.delete(0,tk.END)
    Gain_entry.insert(0,gain)
    Exposure_entry.delete(0,tk.END)
    Exposure_entry.insert(0,exp)  

###################################################################################


def start_stream():
    global flag_stop
    global cam1
    global cam2
    global cam3
    global ncam
    global cam
    global fps
    global cama
    global crops
    global cam_serial
    global gains
    global exposures
    global cam_name1, cam_name2, cam_name3
    global opdir1, opdir2, opdir3
    global imgs1,imgs2,imgs3
    global running_flag1, running_flag2, running_flag3

    flag_stop=0
    
    STREAMbtn.config(state="disabled")
    RECORDbtn.config(state="normal")


    fps = int(fps_choose.get())

    for n in range(ncam): # Initialize Camera
        
        if n==0:
            n_temp=cam_serial[0]
            cam1=Camera(int(n_temp))
            cam1.init()

            cam1.GainAuto = 'Off'

            gain=gains[n_temp][0]
            exp=exposures[n_temp][0]
            gain=int(gain)
            gain_min=int(cam1.get_info('Gain')['min'])
            gain_max=int(cam1.get_info('Gain')['max'])
            gain=gain*(gain_max-gain_min)/100
            gain=gain_min+gain
            cam1.Gain=gain

            cam1.Width = crops[n_temp][1]
            cam1.Height = crops[n_temp][3]
            cam1.OffsetX = crops[n_temp][0]
            cam1.OffsetY = crops[n_temp][2]
            serial=cam1.get_info('DeviceSerialNumber')['value']
            size = (cam1.Width,cam1.Height)

            # update_label=str(str("Frame Size and Location: X=")+str(xcrop)+str(", Y= ")+str(ycrop)+str(", Height= ")+str(cam.Height)+str(", Width= ")+str(cam.Width))
            # frame_size.config(text=update_label)

            # To change the frame rate, we need to enable manual control
            try:
                cam1.AcquisitionFrameRateAuto = 'Off'
                cam1.AcquisitionFrameRateEnabled = True
            except:
                cam1.AcquisitionFrameRateEnable = True
            #cam1.AcquisitionFrameRate = cam1.get_info('AcquisitionFrameRate')['max']
            cam1.AcquisitionFrameRate=fps

            cam1.ExposureAuto = 'Off'
            cam1.ExposureTime = exp 

            cam1.start()


            cam_name1=str("Camera ")+str(serial)
            cv2.namedWindow(cam_name1, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(cam_name1, 510, 300)

        if n==1:
            n_temp=cam_serial[1]
            cam2=Camera(int(n_temp))
            cam2.init()

            cam2.GainAuto = 'Off'
            gain=gains[n_temp][0]
            exp=exposures[n_temp][0]
            gain=int(gain)
            gain_min=int(cam2.get_info('Gain')['min'])
            gain_max=int(cam2.get_info('Gain')['max'])
            gain=gain*(gain_max-gain_min)/100
            gain=gain_min+gain
            cam2.Gain=gain

            cam2.Width = crops[n_temp][1]
            cam2.Height = crops[n_temp][3]
            cam2.OffsetX = crops[n_temp][0]
            cam2.OffsetY = crops[n_temp][2]
            serial=cam2.get_info('DeviceSerialNumber')['value']
            size = (cam2.Width,cam2.Height)

            # update_label=str(str("Frame Size and Location: X=")+str(xcrop)+str(", Y= ")+str(ycrop)+str(", Height= ")+str(cam.Height)+str(", Width= ")+str(cam.Width))
            # frame_size.config(text=update_label)

            # To change the frame rate, we need to enable manual control
            try:
                cam2.AcquisitionFrameRateAuto = 'Off'
                cam2.AcquisitionFrameRateEnabled = True
            except:
                cam2.AcquisitionFrameRateEnable = True
            #cam2.AcquisitionFrameRate = cam2.get_info('AcquisitionFrameRate')['max']
            cam2.AcquisitionFrameRate=fps


            cam2.ExposureAuto = 'Off'
            cam2.ExposureTime = exp

            cam2.start()

            cam_name2=str("Camera ")+str(serial)
            cv2.namedWindow(cam_name2, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(cam_name2, 510, 300)
    

        if n==2:
            n_temp=cam_serial[2]
            cam3=Camera(int(n_temp))
            cam3.init()

            cam3.GainAuto = 'Off'
            gain=gains[n_temp][0]
            exp=exposures[n_temp][0]
            gain=int(gain)
            gain_min=int(cam3.get_info('Gain')['min'])
            gain_max=int(cam3.get_info('Gain')['max'])
            gain=gain*(gain_max-gain_min)/100
            gain=gain_min+gain
            cam3.Gain=gain

            cam3.Width = crops[n_temp][1]
            cam3.Height = crops[n_temp][3]
            cam3.OffsetX = crops[n_temp][0]
            cam3.OffsetY = crops[n_temp][2]
            serial=cam3.get_info('DeviceSerialNumber')['value']
            size = (cam3.Width,cam3.Height)

            # update_label=str(str("Frame Size and Location: X=")+str(xcrop)+str(", Y= ")+str(ycrop)+str(", Height= ")+str(cam.Height)+str(", Width= ")+str(cam.Width))
            # frame_size.config(text=update_label)

            # To change the frame rate, we need to enable manual control
            try:
                cam3.AcquisitionFrameRateAuto = 'Off'
                cam3.AcquisitionFrameRateEnabled = True
            except:
                cam3.AcquisitionFrameRateEnable = True
            #cam3.AcquisitionFrameRate = cam3.get_info('AcquisitionFrameRate')['max']
            cam3.AcquisitionFrameRate=fps


            cam3.ExposureAuto = 'Off'
            cam3.ExposureTime = exp

            cam3.start()

            cam_name3=str("Camera ")+str(serial)
            cv2.namedWindow(cam_name3, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(cam_name3, 510, 300)
    
    global imgs_con
    global record_flag
    record_flag=0

    while True:
        imc1 = cam1.get_array()
        cv2.imshow(cam_name1,imc1)
        if ncam>1:
            imc2 = cam2.get_array()
            cv2.imshow(cam_name2,imc2)
        if ncam>2:
            imc3 = cam3.get_array()
            cv2.imshow(cam_name3,imc3)
        cv2.waitKey(1)
        if flag_stop==1:
            break

    if record_flag==0:
        STREAMbtn.config(state="normal")
        RECORDbtn.config(state="disabled")

    if record_flag==1:
        running_flag1=0 
        running_flag2=0 
        running_flag3=0

        flag_stop=1

        create_folder()

        arr1 = [[0]*2]*1
        if ncam>1:
            arr2=[[0]*2]*1
        if ncam>2:
            arr3=[[0]*2]*1
        
        fps = int(fps_choose.get())
        
        t_total=int(time_entry.get())

        imgs1=[]
        imgs2=[]
        imgs3=[]

        record_status.config(bg="black", fg="red",text="Recording")
        
        
        framecount=0
        framecount2=0
        framecount3=0
        n=0 

        t=1000/fps

        cam1.start()
        if ncam>1:
            cam2.start()
        if ncam>2:
            cam3.start()


        prev_time=0
        time_start = time.time()
        
        if ncam==1:
            while time.time()<(time_start+t_total) and record_flag==1:
                interval=1000*(time.time()-prev_time)
                if interval>t:
                    prev_time=time.time()
                    framecount+=1
                    n+=1
                    imc1 = cam1.get_array()
                    newrow = [int(n), math.floor((time.time() - time_start)*1000) ]
                    arr1 = np.vstack([arr1, newrow])
                    imgs1.append(imc1)
                    if (framecount%50)==0:
                        time_taken=1000*(time.time()-time_start)
                        t=(t*framecount*1000)/(fps*time_taken)
                    if ((framecount)%1000)==0:
                        if running_flag1==0:
                            im_t=imgs1[0:999]
                            cam1thread(im_t)
                            imgs1[0:999]=[]
                            gc.collect()

        if ncam==2:
            while time.time()<(time_start+t_total) and record_flag==1:
                interval=1000*(time.time()-prev_time)
                if interval>t:
                    prev_time=time.time()
                    framecount+=1
                    framecount2+=1
                    n+=1
                    imc1 = cam1.get_array()
                    newrow = [int(n), math.floor((time.time() - time_start)*1000) ]
                    arr1 = np.vstack([arr1, newrow])

                    imc2 = cam2.get_array()
                    newrow = [int(n), math.floor((time.time() - time_start)*1000) ]
                    arr2 = np.vstack([arr2, newrow])

                    imgs1.append(imc1)
                    imgs2.append(imc2)

                    if (framecount%50)==0:
                        time_taken=1000*(time.time()-time_start)
                        t=(t*framecount*1000)/(fps*time_taken)
                    if ((framecount)%1000)==0:
                        if running_flag1==0:
                            im_t=imgs1[0:999]
                            cam1thread(im_t)
                            imgs1[0:999]=[]
                            gc.collect()
                    if ((framecount2)%1000)==0:
                        if running_flag2==0:
                            im_t=imgs2[0:999]
                            cam2thread(im_t)
                            imgs2[0:999]=[]
                            gc.collect()


        if ncam==3:
            while time.time()<(time_start+t_total) and record_flag==1:
                interval=1000*(time.time()-prev_time)
                if interval>t:
                    prev_time=time.time()
                    framecount+=1
                    framecount2+=1
                    framecount3+=1
                    n+=1
                    imc1 = cam1.get_array()
                    newrow = [int(n), math.floor((time.time() - time_start)*1000) ]
                    arr1 = np.vstack([arr1, newrow])

                    imc2 = cam2.get_array()
                    newrow = [int(n), math.floor((time.time() - time_start)*1000) ]
                    arr2 = np.vstack([arr2, newrow])

                    imc3 = cam3.get_array()
                    newrow = [int(n), math.floor((time.time() - time_start)*1000) ]
                    arr3 = np.vstack([arr3, newrow])

                    imgs1.append(imc1)
                    imgs2.append(imc2)
                    imgs3.append(imc3)

                    if (framecount%50)==0:
                        time_taken=1000*(time.time()-time_start)
                        t=(t*n*1000)/(fps*time_taken)
                    if ((framecount)%1000)==0:
                        if running_flag1==0:
                            im_t=imgs1[0:999]
                            cam1thread(im_t)
                            imgs1[0:999]=[]
                            gc.collect()
                    if ((framecount2)%1000)==0:
                        if running_flag2==0:
                            im_t=imgs2[0:999]
                            cam2thread(im_t)
                            imgs2[0:999]=[]
                            gc.collect()
                    if ((framecount3)%1000)==0:
                        if running_flag3==0:
                            im_t=imgs3[0:999]
                            cam3thread(im_t)
                            imgs3[0:999]=[]
                            gc.collect()

        
        if record_flag==1:
            record_status.config(bg="black", fg="yellow",text="Saving")

            write_video()

            
            while True:
                if running_flag1==0 and running_flag2==0 and running_flag3==0:
                    break



            csv_timestamp(opdir1,arr1)
            if ncam>1:
                csv_timestamp(opdir2,arr2)
            if ncam>2:
                csv_timestamp(opdir3,arr3)

        

        cam1.stop()
        if ncam>1:
            cam2.stop()
        if ncam>2:
            cam3.stop()

       
        record_status.config(bg="black", fg="white",text="Not Recording")
        cv2.destroyAllWindows()
        flag_stop=0
        record_flag=0
        del imgs1
        del imgs2
        del imgs3
        gc.collect()

        pause()
        reset()

        STREAMbtn.config(state="normal")
        RECORDbtn.config(state="disabled")

    if record_flag==0:   
        cam1.stop()
        if ncam>1:
            cam2.stop()
        if ncam>2:
            cam3.stop()


        cv2.destroyAllWindows()
        flag_stop=0

def stop_stream():
    global flag_stop
    global ncam, cam1, cam2, cam3

    flag_stop=1

    
def abort_record():
    global record_flag
    record_flag=0

###################################################################################
def folder_name(camera_folder,desktop,dt_string):
    file_name = "/" + file_name_entry.get()
    if len(file_name_entry.get())>0:
        while True:
            if os.path.exists(file_name):
                output_dir = desktop+camera_folder
                output_dir = output_dir.replace(os.sep,'/')
                output_dir = output_dir+dt_string
            else:
                output_dir = desktop + camera_folder
                output_dir = output_dir.replace(os.sep,'/')
                output_dir = output_dir + file_name
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                break
    else:
        output_dir = desktop+camera_folder
        output_dir = output_dir.replace(os.sep,'/')
        output_dir = output_dir+dt_string

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return output_dir


def create_folder():
    global ncam, cam1, cam2, cam3
    global opdir1, opdir2, opdir3


    now = datetime.now()
    dt_string = now.strftime("%Y_%m_%d %H_%M")
    desktop=os.path.join((os.environ['USERPROFILE']),'Desktop/FLIR_Recording')
    file_name = "/" + file_name_entry.get()

    serial=cam1.get_info('DeviceSerialNumber')['value']
    camera_folder='/'+'Camera '+str(serial)+'/'

    opdir1=folder_name(camera_folder,desktop,dt_string)

    if ncam>1:
        serial=cam2.get_info('DeviceSerialNumber')['value']
        camera_folder='/'+'Camera '+str(serial)+'/'

        opdir2=folder_name(camera_folder,desktop,dt_string)

    if ncam>2:
        serial=cam3.get_info('DeviceSerialNumber')['value']
        camera_folder='/'+'Camera '+str(serial)+'/'

        opdir3=folder_name(camera_folder,desktop,dt_string)

def csv_timestamp(output_dir,arr):
    file = '/' + 'timestamp' + '.csv'
    csv_file = output_dir + file

    with open(csv_file, 'w', newline = '') as timestamp:
        csv_writer = csv.writer(timestamp)  
        timestamp_file_header = ["Frame", "Time(ms)"]
        csv_writer.writerow(timestamp_file_header)
        csv_writer.writerows(arr)  

    timestamp.close()

def write_video1():
    global imgs1

    frames_left=len(imgs1)
    iterations1=math.floor(frames_left/1000)

    for j in range(iterations1):
        im_t=imgs1[0:999]
        cam1thread(im_t)
        previous_time = time.time()
        while True:
            if time.time()-previous_time>20:
                break
        imgs1[0:999]=[]
    
    frames_left=len(imgs1)
    if frames_left>10:
        cam1thread(imgs1)

def write_video2():
    global imgs2

    frames_left=len(imgs2)
    iterations2=math.floor(frames_left/1000)

    for j in range(iterations2):
        im_t=imgs2[0:999]
        cam2thread(im_t)
        previous_time = time.time()
        while True:
            if time.time()-previous_time>20:
                break
        imgs2[0:999]=[]
    
    frames_left=len(imgs2)
    if frames_left>10:
        cam2thread(imgs2)


def write_video3():
    global imgs3

    frames_left=len(imgs3)
    iterations3=math.floor(frames_left/1000)

    for j in range(iterations3):
        im_t=imgs3[0:999]
        cam3thread(im_t)
        previous_time = time.time()
        while True:
            if time.time()-previous_time>20:
                break
        imgs3[0:999]=[]
    
    frames_left=len(imgs3)
    if frames_left>10:
        cam3thread(imgs3)

def record_sync():
    global flag_stop
    global record_flag
    record_flag=1
    flag_stop=1

###################################################################################

global running
running = False


def start():
    global running
    global time_start_timer
    time_start_timer=time.time()
    if not running:
        update()
        running = True

def pause():
    global running
    global update_time
    if running:
        stopwatch_label.after_cancel(update_time)
        running = False

def reset():
    global running
    global update_time
    if running:
        stopwatch_label.after_cancel(update_time)
        running = False
    
    stopwatch_label.config(text='00:00')

def update():
 
    global time_start_timer

    t=math.floor((time.time()-time_start_timer))

    
    
    sec=t%60
    minit=math.floor(t/60)
    minutes_string = f'{minit}' if minit > 9 else f'0{minit}'
    seconds_string = f'{sec}' if sec > 9 else f'0{sec}'
    stopwatch_label.config(text=minutes_string + ':' + seconds_string)
    global update_time
    update_time = stopwatch_label.after(500, update)




###################################################################################

win = tk.Tk()
choose = tk.StringVar()
fps_choose = tk.IntVar()
choose.set( "Camera 1" )
fps_choose.set(30)
win.minsize(325,300)

win.resizable(True,True)

# initialize window with title & minimum size
win.title("REVEALS")
tabControl = ttk.Notebook(win)

tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)

s=ttk.Style()
s.theme_use('classic')
s.configure('TNotebook.Tab', background="gray")
s.map("TNotebook", background= [("selected", "white")])
  
tabControl.add(tab1, text ='Camera Setup')
tabControl.add(tab2, text ='Recording')
tabControl.pack(expand = 1, fill ="both")

mycolor='#e0dcdc'

STOPbtn1 = tk.Button(tab1, bg="red", fg="white",bd=4, width=10,text="Stop Stream", command=StopCam2)
STOPbtn1.grid(column=2, row=3)

STOPbtn2 = tk.Button(tab2,  bg="red", fg="white",bd=4, width=10, text="Stop Stream", command=threading)
STOPbtn2.grid(column=2, row=1)

STREAMbtn = tk.Button(tab2,  bg="green",fg="white",bd=4, width=10, text="Stream", command=threading1)
STREAMbtn.grid(column=1, row=1,pady=10)

RECORDbtn = tk.Button(tab2, bd=4, width=10, text="Record", command=lambda:[record_start(),start()],state="disabled")
RECORDbtn.grid(column=1, row=5, pady=10)

CONNECTbtn=tk.Button(tab1,bd=4, width=10, text="Connect", command=connect)
CONNECTbtn.grid(column=1, row=1,pady=10)

record_status=tk.Label(tab2,bg="black",fg="white",pady=10,text="Not recording")
record_status.grid(column=1,row=6)

time_label = tk.Label(tab2, bg=mycolor,text="Recording Time(s)")
time_label.grid(column=1, row=3, pady=10)

time_entry = tk.Entry(tab2, width=5)
time_entry.grid(column=1, row=4)

fps_label = tk.Label(tab2, bg=mycolor,text="FPS")
fps_label.grid(column=2, row=3)

fps_menu = tk.OptionMenu(tab2, fps_choose, *fps_options)
fps_menu.grid(column=2,row=4)

# fps_entry = tk.Entry(tab2, width=5)
# fps_entry.grid(column=2, row=3)

stopwatch_label = tk.Label(tab2,text='00:00:00', font=('Arial', 12))
stopwatch_label.grid(column=3, row=5)

stoptimerbtn = tk.Button(tab2, bd=4, width=10, text="Stop Timer", command=pause)
stoptimerbtn.grid(column=3, row=6)

resetbtn = tk.Button(tab2, bd=4, width=10, text="Reset Timer", command=reset)
resetbtn.grid(column=3, row=7)

abort_btn=tk.Button(tab2, bg="red",bd=4, width=10, text="ABORT", command=abort_thread)
abort_btn.grid(column=3, row=8,pady=30)

#Cropping portion


Gain_label = tk.Label(tab1, bg=mycolor,text="Gain (%)")
Gain_label.grid(column=1, row=4)

Gain_entry = tk.Entry(tab1, width=5)
Gain_entry.grid(column=2, row=4)

Exposure_label = tk.Label(tab1, bg=mycolor,text="Exposure (micro sec)")
Exposure_label.grid(column=1, row=5)

Exposure_entry = tk.Entry(tab1, width=5)
Exposure_entry.grid(column=2, row=5)

cropx_label = tk.Label(tab1, bg=mycolor,text="X Crop")
cropx_label.grid(column=1, row=7)

cropx_entry = tk.Entry(tab1, width=5)
cropx_entry.grid(column=1, row=8)


cropy_label = tk.Label(tab1, bg=mycolor,text="Y Crop")
cropy_label.grid(column=2, row=7)

cropy_entry = tk.Entry(tab1, width=5)
cropy_entry.grid(column=2, row=8)

cropwidth_label = tk.Label(tab1, bg=mycolor,text="Width")
cropwidth_label.grid(column=1, row=9)

cropwidth_entry = tk.Entry(tab1, width=5)
cropwidth_entry.grid(column=1, row=10)

cropheight_label = tk.Label(tab1,bg=mycolor, text="Height")
cropheight_label.grid(column=2, row=9)

cropheight_entry = tk.Entry(tab1, width=5)
cropheight_entry.grid(column=2, row=10)

frame_size=tk.Label(tab1,bg=mycolor,pady=10,text="Frame Size and Location:\n X=0, Y=0,\n Height=768, Width=1024")
frame_size.grid(column=1,row=11,pady=10)

camera_serial=tk.Label(tab1,bg=mycolor,pady=10,text="Serial Number:\n ")
camera_serial.grid(column=2,row=11,pady=10)

camera_deets=tk.Label(tab1,pady=10,bg=mycolor,text="Number of cameras=0")
camera_deets.grid(column=2,row=1)


# Camera Selection Menu
menu = tk.OptionMenu(tab1, choose, *options)
menu.grid(column=1,row=2,pady=10)

select_button = tk.Button(tab1,  bd=4, width=12, text='Select Camera', command=select_camera)
select_button.grid(column=2, row=2)

stream_camerabtn=tk.Button(tab1, bg="green",fg="white", bd=4, width=12, text='Stream Camera', command=crop_thread)
stream_camerabtn.grid(column=1, row=3,pady=10)

# File Name
file_name_label = tk.Label(tab2, text="Folder Name", bg=mycolor)
file_name_label.grid(column=2, row=2)

file_name_entry=tk.Entry(tab2, width=20)
file_name_entry.grid(column=3, row=2)

mycolor='#e0dcdc'
crop_label=tk.Label(tab1,bg=mycolor, text="Crop")
crop_label.grid(column=1,row=6,pady=10)

reset_camerabtn=tk.Button(tab1, bd=4, width=20, text='Reset Camera (press twice)', command=reset_camera)
reset_camerabtn.grid(column=2, row=6)


global flag_stop
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
       
       cv2.waitKey(1)
       cv2.destroyAllWindows()
       cv2.waitKey(1)
       win.destroy()

win.protocol("WM_DELETE_WINDOW", on_closing)

win.mainloop()
