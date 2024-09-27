
#from custom camera class import the cam module
from camera_class import cam

#import all requirements for GUI building
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from ttkthemes import ThemedTk
import sv_ttk
from tkinter import messagebox

#threading for concurrent processes
import threading
from threading import Thread

#multiprocessing for recording
from multiprocessing import Pool,Process

#import image module
from PIL import Image,ImageTk

#import opencv for video handling and writing
import cv2

#import other system requirements
import os
import re
import sys
import pandas as pd
from os import listdir
import glob
import numpy as np
import math
import time
import csv
from datetime import datetime
import logging
###################################################################################

########SETUP TAB FUNCTIONS########


global camObj #global object to handle all connected cameras
global cam_flags #global object to record state of cameras

#Initiliaze the global camObj
camObj = cam();
camObj.initialize()

#set all default values for flags and options to fill in camera drop down menu
cam_flags=1 
options=[]
options.append('Camera 1')

if camObj.ncams>0:
	options=[]

for i in range (int(camObj.ncams)):
	string_temp="Camera " + str(i+1)
	options.append(string_temp)
	

def camera_find(): #This function triggers on pressing connect button. It handles changing entries in GUI as well as assigning states to other buttons.
	global camObj
	camera_number_label.configure(text=f'Number of cameras={int(camObj.ncams)}') #update camera label

	delete_entries() #clear all GUi entries for camera parameter values
	cidx=0
	#set all camera parameter values in teh GUI to values of camera 1 to correspond to the initial dropdown
	XCrop_entry.insert(0,str(camObj.get_OffsetX(cidx)))
	YCrop_entry.insert(0,str(camObj.get_OffsetY(cidx)))
	HeightCrop_entry.insert(0,str(camObj.get_Height(cidx)))
	WidthCrop_entry.insert(0,str(camObj.get_Width(cidx)))
	Gain_entry.insert(0,str(camObj.get_Gain(cidx)))
	Exposure_entry.insert(0,str(camObj.get_Exposure(cidx)))
	CurrentCrop_label2.configure(text=f'X={camObj.get_OffsetX(cidx)},Y={camObj.get_OffsetY(cidx)}\nHeight={camObj.get_Height(cidx)},Width={camObj.get_Width(cidx)}')

	RESETbtn.configure(state='normal') #allow reset button to be used
	setupSTREAMbtn.configure(state='normal') #allow stream button to be used on setup tab




def delete_entries():  #clear all GUi entries for camera parameter values
	XCrop_entry.delete(0,tk.END)
	YCrop_entry.delete(0,tk.END)
	HeightCrop_entry.delete(0,tk.END)
	WidthCrop_entry.delete(0,tk.END)
	Gain_entry.delete(0,tk.END)
	Exposure_entry.delete(0,tk.END)
	

def update_crop_entries(event): #change all GUI entries for camera parameter values on selecting a different camera from drop down
	global camObj
	selected = choose_camera.get() #determine which camera is selected in the dropdown

	cidx=selected.replace('Camera ','')
	cidx=int(cidx)-1
	
	delete_entries() #clear all entries

	XCrop_entry.insert(0,str(camObj.get_OffsetX(cidx)))
	YCrop_entry.insert(0,str(camObj.get_OffsetY(cidx)))
	HeightCrop_entry.insert(0,str(camObj.get_Height(cidx)))
	WidthCrop_entry.insert(0,str(camObj.get_Width(cidx)))
	Gain_entry.insert(0,str(camObj.get_Gain(cidx)))
	Exposure_entry.insert(0,str(camObj.get_Exposure(cidx)))

	CurrentCrop_label2.configure(text=f'X={camObj.get_OffsetX(cidx)},Y={camObj.get_OffsetY(cidx)}\nHeight={camObj.get_Height(cidx)},Width={camObj.get_Width(cidx)}') #configure the current crop label to reflect new values


def cameras_reset():
	global camObj
	
	camObj.close()

	camObj=cam()
	camObj.initialize()
	messagebox.showinfo('Notice','Cameras have been reset')

def check_changes(cidx): #This function checks if any of the camera parameter GUI entry values have changed and then assigns them accordingly to the camera
	global camObj

	crop_current=[int(camObj.get_OffsetX(cidx)),int(camObj.get_Width(cidx)),int(camObj.get_OffsetY(cidx)),int(camObj.get_Height(cidx))] #get the cameras current set values

	#get the new values from GUI
	x_new=int(XCrop_entry.get())
	y_new=int(YCrop_entry.get())
	width_new=int(WidthCrop_entry.get())
	height_new=int(HeightCrop_entry.get())

	#check if new values are valid and different from current set values and then assigns them to the camera

	#the crop vector sent to the camera class function is in the form [x-offset, width, y-offset, height]

	if x_new>=0 and x_new != crop_current[0]:
		crop_current[0]=x_new
		camObj.setFrameSize(cidx,crop_current)
	if y_new>=0 and y_new != crop_current[2]:
		crop_current[2]=y_new
		camObj.setFrameSize(cidx,crop_current)
	if width_new>=0 and width_new != crop_current[1]:
		crop_current[1]=width_new
		camObj.setFrameSize(cidx,crop_current)
	if height_new>=0 and height_new != crop_current[3]:
		crop_current[3]=height_new
		camObj.setFrameSize(cidx,crop_current)

	CurrentCrop_label2.configure(text=f'X={crop_current[0]},Y={crop_current[2]}\nHeight={crop_current[3]},Width={crop_current[1]}')

	gain_current=int(camObj.get_Gain(cidx))
	exp_current=int(camObj.get_Exposure(cidx))

	gain_new=float(Gain_entry.get())
	exp_new=float(Exposure_entry.get())


	if gain_new>=0 and gain_new != gain_current:
		camObj.setGain(cidx,gain_new)

	if exp_new>=0 and exp_new != exp_current:
		camObj.setExp(cidx,exp_new)
	

def setup_stream(cidx): #this function starts a stream in a new window for the selected camera from the drop down menu when pressed. cidx points to the camera being streamed
	global camObj
	global cam_flags
	
	cam_name='Camera '+str(cidx) #Assign camera name (based on camera index)

	check_current=[int(XCrop_entry.get()),int(WidthCrop_entry.get()),int(YCrop_entry.get()),int(HeightCrop_entry.get()),int(Gain_entry.get()),int(Exposure_entry.get())] #check current entries in GUI camera parameters

	if any(x<0 for x in check_current):
		messagebox.showerror('Error','One of the parameters entered is invalid\nPlease correct and try again')
		return

	check_fields=[len(XCrop_entry.get()),len(WidthCrop_entry.get()),len(YCrop_entry.get()),len(HeightCrop_entry.get()),len(Gain_entry.get()),len(Exposure_entry.get())] #check lengths of all entries in GUI camera parameters


	if any(x<=0 for x in check_fields):
		messagebox.showerror('Error','One of the parameters entered is invalid\nPlease correct and try again')
		return

	check_changes(cidx) #evaluate changes and assign if needed

	camObj.start(cidx) #start camera


	#open a new window for displaying the input from current camera
	cv2.namedWindow(cam_name, cv2.WINDOW_NORMAL)
	cv2.resizeWindow(cam_name, 510, 300)

	#start a loop that keeps the camera streaming until forcefully stopped using stop stream or closing the window, or until 5 min pass
	t_start=time.time()
	while time.time()<(t_start+300):
		imc1 = camObj.getFrame(cidx) #get frame from camera
		cv2.imshow(cam_name,imc1) #show frame in the new window
		cv2.waitKey(1)


		#if any changes are made to the GUI camera parameters entries, stop the camera, assign changes, start the camera again

		crop_current=[int(camObj.get_OffsetX(cidx)),int(camObj.get_Width(cidx)),int(camObj.get_OffsetY(cidx)),int(camObj.get_Height(cidx)),int(camObj.get_Gain(cidx)),int(camObj.get_Exposure(cidx))]
		check_current=[float(XCrop_entry.get()),float(WidthCrop_entry.get()),float(YCrop_entry.get()),float(HeightCrop_entry.get()),float(Gain_entry.get()),float(Exposure_entry.get())]

		if crop_current != check_current:
			camObj.stop(cidx)
			check_changes(cidx)
			camObj.start(cidx)

		if cv2.getWindowProperty(cam_name,cv2.WND_PROP_VISIBLE) <1: #check that window hasnt been closed
			break
		if cam_flags==0: #check that stop stream hasnt been pressed
			break

	setupSTREAMbtn.configure(state='normal') #make the stream button usable again

	try:
		cv2.destroyAllWindows() #close the camera stream windows if open
	except:
		pass

	camObj.stop(cidx) #stop camera recording
	

def stop_setup_stream(): #this function stops the current streaming camera on the setup tab
	global cam_flags
	if cam_flags==0:
		messagebox.showerror('Error','Stream is not active')
	cam_flags=0



def stream_thread(): #this is the thread that starts the camera stream in setup tab. It calls the setup_stream function.
	global CamObj
	global cam_flags
	cam_flags=1

	#recognise which camera has been selected in dropdown to decide what index to pass to the setup_stream function
	selected = choose_camera.get() 
	for i in range (int(camObj.ncams)):
		string_temp="Camera " + str(i+1)
		if (string_temp==selected):
			index=i	

	#disable start stream button to avoid accidental presses
	setupSTREAMbtn.configure(state='disabled')
	setupSTOP_STREAMbtn.configure(state='normal')

	t=threading.Thread(target=setup_stream,args=(index,)) #start the thread
	t.start()

def stop_stream_thread(): #thread to use stop_setup_stream function
	global CamObj

	t_stop=threading.Thread(target=stop_setup_stream)
	t_stop.start()	

###################################################################################

########VIDEO ACQUISITION TAB FUNCTIONS########

def select_folder(): #this function sets the directory for saving videos when using Browse button
	global camObj
	folder_selected = filedialog.askdirectory()
	if folder_selected:
		camObj.video_path=folder_selected
		Folder_display_path.configure(text=folder_selected) #update label to show path of recording



def select_experiment(event): #this function sets folder name for the instance inside the save location on detecting an input in entry box
	global camObj
	if (len(Experiment_name_entry.get())>0):
		valid_folder_pattern = r'^[a-zA-Z0-9_\-\s\.]+$'
		if not re.match(valid_folder_pattern, str(Experiment_name_entry.get())):
   			messagebox.showerror('Error','Invalid folder name\nPlease try again')
   			return False
		else:
			camObj.experiment_name=str(Experiment_name_entry.get())
			return True



def set_path(cam_name,vpath,ename): #this function handles creation of the folders for recording
	global camObj
	now = datetime.now() #get date and time
	dt_string = now.strftime("%Y_%m_%d %H_%M_%S") #make a string for YY_MM_DD_HH_MM
	desktop=os.path.join((os.environ['USERPROFILE']),'Desktop/FLIR_Recording') #get path to desktop
	if vpath!='desktop': #check if user provided any input for folder location
		desktop=vpath
	output_dir = desktop+'/'+cam_name+'/'
	output_dir = output_dir.replace(os.sep,'/')

	

	if str(ename)!='experiment': #check if user provided any input for animal name
		exp_name=str(ename)

		if not os.path.exists((output_dir+exp_name)):
			output_dir=output_dir+exp_name			
		else:
			output_dir = output_dir+dt_string #if folder name already exists, make a folder name with current date and time
	else:
		output_dir = output_dir+dt_string #if no user input was provided, make a folder name with current date and time


		
	if not os.path.exists(output_dir):
	    os.makedirs(output_dir)
	return output_dir

def csv_timestamp(output_dir,arr): #this function creates the csv for saving timestamp. The inputs are the folder path and the array of timestamps
	file = '/' + 'timestamp' + '.csv'
	csv_file = output_dir + file

	with open(csv_file, 'w', newline = '') as timestamp:
	    csv_writer = csv.writer(timestamp)  
	    timestamp_file_header = ["Frame", "Time(ms)"]
	    csv_writer.writerow(timestamp_file_header)
	    csv_writer.writerows(arr)  

	timestamp.close()

def record_frame_buttons_activate(): #change acqusition tab button state to active
	Recording_status.configure(text='Not Recording',font="Helevtica 11 underline")
	Browse_button.configure(state='normal')
	recordSTREAMbtn.configure(state='normal')
	RECORD_btn.configure(state='normal')

def record_frame_buttons_deactivate():  #change acqusition tab button state to inactive
	Browse_button.configure(state='disabled')
	recordSTREAMbtn.configure(state='disabled')
	RECORD_btn.configure(state='disabled')
	Recording_status.configure(text='Recording',font="Helevtica 16 bold")


def pooled_record(): #This function starts a multiprocessing pools for all cameras to record video on pressing the record button

	global camObj
	logging.basicConfig(level=logging.DEBUG)

	record_frame_buttons_deactivate() #deactivate buttons to avoid accidental presses
	root.update_idletasks()

	
	
	time_start=time.time() #start time

	items=[] #array to pass all required parameters to the worker function record_sep
	vpath=camObj.video_path
	ename=camObj.experiment_name

	#check all entries for validity, and pass through only if all are valid. Otherwise reactivate all buttons and exit the function

	if len(Recording_time_entry.get())>0:
		t_total=int(Recording_time_entry.get()) #set total time of recording
	else:
		messagebox.showerror('Error','Invalid Recording Time')
		record_frame_buttons_activate()
		return
	if t_total<=0:
		messagebox.showerror('Error','Invalid Recording Time')
		record_frame_buttons_activate()
		return

	if len(FPS_entry.get())>0:
		fps=int(FPS_entry.get())
	else:
		messagebox.showerror('Error','Invalid FPS')
		record_frame_buttons_activate()
		return
	if (fps<15) or (fps>120):
		messagebox.showerror('Error','Please enter FPS between 15-120')
		record_frame_buttons_activate()
		return

	if len(FPV_entry.get())>0:
		frame_bin=int(FPV_entry.get())
	else:
		messagebox.showerror('Error','Invalid FPV')
		record_frame_buttons_activate()
		return
	if frame_bin<=0:
		messagebox.showerror('Error','Invalid FPV')
		record_frame_buttons_activate()
		return
	
	
	
	for i in range (int(camObj.ncams)): #asssign input parameters to worker functions
		crop_current=[int(camObj.get_OffsetX(i)),int(camObj.get_Width(i)),int(camObj.get_OffsetY(i)),int(camObj.get_Height(i)),int(camObj.get_Gain(i)),int(camObj.get_Exposure(i))]
		items.append((int(i),time_start,t_total,fps,frame_bin,vpath,ename,crop_current))


	with Pool() as pool: #start pool
		_=pool.starmap_async(record_sep, items)
		pool.close()
		pool.join()

	try:	
		cv2.destroyAllWindows() #close camera windows if any
	except:
		pass

	record_frame_buttons_activate() #activate all buttons again for next round of recording


def record_sep(cidx,t_start,tt,fps,frame_bin,video_path,exp_name,crop_para): #worker function for recording from each camera
	global camObj
	

	cam_name='Camera '+str(cidx) #camera name based on cidx (camera index)

	output_path=set_path(cam_name,video_path,exp_name) #set output path

	#set all user decided camera parameters
	
	camObj.setFrameSize(cidx,crop_para[0:4])

	camObj.setGain(cidx,crop_para[4])
	
	camObj.setExp(cidx,crop_para[5])
	
	camObj.start(cidx)
	
	
	count=1 #start a count for number of videos in each folder

	item=str('behavcam_')+str(count-1)+str('.mp4') #name the first video behavcam_0.mp4


	if os.path.exists(os.path.join(output_path, item)):
		flag_name_check=0 #this will change when a video name doesnt exist in the output folder
		while flag_name_check==0:
			count=count+1
			item=str('behavcam_')+str(count-1)+str('.mp4')
			if not os.path.exists(os.path.join(output_path, item)):
				flag_name_check=1
	item=str('behavcam_')+str(count-1)+str('.mp4')
	video_name=os.path.join(output_path, item) #set the video output
	count=count+1

	fourcc = cv2.VideoWriter_fourcc(*'mp4v') #initialise the video writer and set the format
	prev_time=0 #track time
	
	t=1000/fps #set interval between frames based on fps
	frames=0 #frame counter 
	
	ts_array = [[0]*2]*1 # initialise the time stamp array


	cv2.namedWindow(cam_name, cv2.WINDOW_NORMAL) #open a window to display the camera stream
	cv2.resizeWindow(cam_name, 510, 300)
	t_start=time.time() #starting time after all intialization is done
	while time.time()<(t_start+tt): #monitor duration of recording. tt is total time in seconds from user input
		interval=1000*(time.time()-prev_time) #interval since last check of this loop in milliseconds
		if interval>t: #if interval passes the time for correct frame rate
			prev_time=time.time() #record time of frame intake
			frames=frames+1 #increase frame counter
			
			imc1 = camObj.getFrame(cidx) #get frame from camera
			newrow = [int(frames), math.floor((time.time() - t_start)*1000) ] 	#uncomment this to save timestamps as relative from beginning of recording

			#newrow = [int(frames), datetime.now().timestamp()] 				#uncomment this to save timestamps in real time instead of from beginning of recording

			ts_array = np.vstack([ts_array, newrow]) #update the timestamp array
			try:
				out.write(imc1) #write the frame to video if its open
			except:
				#open video if its not already open
				height,width=imc1.shape
				size = (width,height)
				out = cv2.VideoWriter(video_name,fourcc, 30, size, False)
				out.write(imc1)

			if (frames%frame_bin)==0:
				
				#once number of frame reached frames per video as input by user, close the video and create the next one
				out.release()
				item=str('behavcam_')+str(count-1)+str('.mp4')
				video_name=os.path.join(output_path, item) 
				count=count+1
				out = cv2.VideoWriter(video_name,fourcc, 30, size, False)

			
			cv2.imshow(cam_name,imc1) #display the frame
			cv2.waitKey(1)
			if (frames%50)==0: #every 50 frames, see if the recording is lagging or leading according to desired fps, and adjust the interval between frames to compensate for that iteratively		
				time_taken=1000*(time.time()-t_start)
				t=(t*frames*1000)/(fps*time_taken)
			if cv2.getWindowProperty(cam_name,cv2.WND_PROP_VISIBLE) <1: #if window is force closed, break the loop
				break
	camObj.stop(cidx) #stop the camera

	csv_timestamp(output_path,ts_array) #output the timestamp
	
	out.release()	#release the video object


def pooled_stream(): #This function starts a multiprocessing pools for all cameras to stream video from all cameras on pressing the stream camera button in the acquisition tab
	global camObj

	t_total=int(Recording_time_entry.get()) #set total time of recording
	Browse_button.configure(state='disabled')
	RECORD_btn.configure(state='disabled')
	recordSTREAMbtn.configure(state='disabled')
	root.update_idletasks()

	
	time_start=time.time()



	items=[]
	vpath=camObj.video_path
	ename=camObj.experiment_name

	
	# if (selected=="All"):
	for i in range (int(camObj.ncams)):
		crop_current=[int(camObj.get_OffsetX(i)),int(camObj.get_Width(i)),int(camObj.get_OffsetY(i)),int(camObj.get_Height(i)),int(camObj.get_Gain(i)),int(camObj.get_Exposure(i))]
		items.append((int(i),time_start,t_total,vpath,ename,crop_current))


	with Pool() as pool:
		_=pool.starmap_async(stream_sep, items)
		pool.close()
		pool.join()

	try:	
		cv2.destroyAllWindows()
	except:
		pass

	Browse_button.configure(state='normal')
	RECORD_btn.configure(state='normal')
	recordSTREAMbtn.configure(state='normal')


def stream_sep(cidx,t_start,tt,video_path,exp_name,crop_para):  #worker function for streaming all cameras together
	global camObj

	camObj.setFrameSize(cidx,crop_para[0:4])


	camObj.setGain(cidx,crop_para[4])
	
	camObj.setExp(cidx,crop_para[5])
	
	camObj.start(cidx)
	

	camObj.start(cidx)

	cam_name='Camera '+str(cidx)
	cv2.namedWindow(cam_name, cv2.WINDOW_NORMAL)
	cv2.resizeWindow(cam_name, 510, 300)

	while time.time()<(t_start+300):
		imc1 = camObj.getFrame(cidx)
		cv2.imshow(cam_name,imc1)
		cv2.waitKey(1)

		if cv2.getWindowProperty(cam_name,cv2.WND_PROP_VISIBLE) <1:
			break
		
	camObj.stop(cidx)

	
##########################################################################################

########SPLASH SCREEN AT LOADING########

if __name__ == '__main__':
	splash_window = tk.Tk()
	splash_window.title("REVEALS 2.0")
	splash_window.geometry("250x250")
	splash_window.configure(bg="white")

	# Load the image
	image = Image.open("splash_screen.jpg") 
	image = image.resize((200, 200)) 
	photo = ImageTk.PhotoImage(image)

	# Create a label to display the image
	image_label = tk.Label(splash_window, image=photo)
	image_label.pack()

	# Create a label for the text
	text_label = tk.Label(splash_window, text="Initializing REVEALS..", font=("Arial", 12))
	text_label.pack()


	splash_window.update()
	time.sleep(5)  # Wait for 5 seconds
	splash_window.destroy()


##########################################################################################

########BASE GUI FRAME ASSIGNMENT########

#root = ThemedTk(theme="adapta")
root=tk.Tk()
sv_ttk.use_dark_theme()
root.resizable(True, True) 
#root.configure(background='grey')
root.title('REVEALS 2.0')

# s = ttk.Style(root)
# s.configure('.', font=18)

Main_frame=ttk.Frame(root,relief='solid')
Main_frame.grid(row=0, column=0, sticky="nsew")

tabControl = ttk.Notebook(Main_frame) 
#tabControl.bind("<<NotebookTabChanged>>", adjust_window_size)
tab1 = ttk.Frame(tabControl) 
tab2 = ttk.Frame(tabControl) 


root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

tabControl.add(tab1, text ='Camera Setup') 
tabControl.add(tab2, text ='Video Acqusition') 
tabControl.pack(expand = 1, fill ="both") 

connect_Frame=ttk.Frame(tab1,relief='sunken')
connect_Frame.grid(row=0,sticky='nsew',padx=10,pady=10)

setup_Frame=ttk.Frame(tab1,relief='sunken')
setup_Frame.grid(row=1,sticky='nsew',padx=10,pady=10)

recording_details_Frame=ttk.Frame(tab2,relief='sunken')
recording_details_Frame.grid(row=0,sticky='nsew',padx=10,pady=10)

recording_Frame=ttk.Frame(tab2,relief='sunken')
recording_Frame.grid(row=1,sticky='nsew',padx=10,pady=10)

##########################################################################################

########SETUP TAB FRAME 1 GUI ARRANGEMENT########

connect_frame_label=ttk.Label(connect_Frame,text="Camera connection\nand reset:",font="Helvetica 14 underline")
connect_frame_label.grid(column=0,row=0,sticky='w',pady=10,padx=10)

CONNECTbtn=ttk.Button(connect_Frame,width=10, text="Connect",command=camera_find)
CONNECTbtn.grid(column=0, row=1,sticky='w',pady=10,padx=10)

camera_number_label=ttk.Label(connect_Frame,text="Number of cameras=0")
camera_number_label.grid(column=0,row=2,sticky='w',pady=10,padx=10)


RESETbtn=ttk.Button(connect_Frame, width=10, text="Reset",command=cameras_reset,state='disabled')
RESETbtn.grid(column=0, row=3,sticky='w',pady=10,padx=10)


##########################################################################################

########SETUP TAB FRAME 2 GUI ARRANGEMENT########

setup_frame_label=ttk.Label(setup_Frame,text="Camera\nparameters:",font="Helvetica 14 underline")
setup_frame_label.grid(column=0,row=0,sticky='w',pady=10,padx=10)


camera_select_label=ttk.Label(setup_Frame,text="Select camera:")
camera_select_label.grid(column=0,row=1,sticky='w',pady=10,padx=10)

choose_camera = tk.StringVar()
#choose_camera.set( "All" )

menu_camera = ttk.OptionMenu(setup_Frame, choose_camera,options[0], *options,command=update_crop_entries)
menu_camera.grid(column=1, row=1,sticky='w',padx=10,pady=10)

gs=ttk.Style(root)
gs.configure('TButton',background='green')

setupSTREAMbtn=ttk.Button(setup_Frame,width=10,text="Stream\nCamera",command=stream_thread,state='disabled')
setupSTREAMbtn.grid(column=0, row=3,sticky='w',pady=10,padx=10)

setupSTOP_STREAMbtn=ttk.Button(setup_Frame,width=10,text="Stop\nStream",command=stop_stream_thread,state='disabled')
setupSTOP_STREAMbtn.grid(column=1, row=3,sticky='w',pady=10,padx=10)

Gain_label=ttk.Label(setup_Frame,text="Gain(%)")
Gain_label.grid(column=0,row=4,sticky='w',pady=10,padx='10')	

Gain_entry=ttk.Entry(setup_Frame,width=7)
Gain_entry.grid(column=1,row=4,sticky='w',pady=10,padx='10')

Exposure_label=ttk.Label(setup_Frame,text="Exposure(micro sec)")
Exposure_label.grid(column=0,row=5,sticky='w',pady=10,padx='10')	

Exposure_entry=ttk.Entry(setup_Frame,width=9)
Exposure_entry.grid(column=1,row=5,sticky='w',pady=10,padx='10')

Crop_label=ttk.Label(setup_Frame,text="Crop parameters:",font="Helvetica 11 underline")
Crop_label.grid(column=0,row=6,sticky='w',pady=10,padx=10)

XCrop_label=ttk.Label(setup_Frame,text="X-offset")
XCrop_label.grid(column=0,row=7,sticky='w',pady=10,padx='10')	

xcrop = tk.StringVar()

XCrop_entry=ttk.Entry(setup_Frame,width=5,textvariable=xcrop)
XCrop_entry.grid(column=1,row=7,sticky='w',pady=10,padx='10')
XCrop_entry.insert(0,'0')

YCrop_label=ttk.Label(setup_Frame,text="Y-offset")
YCrop_label.grid(column=2,row=7,sticky='w',pady=10,padx='10')	

ycrop = tk.StringVar()

YCrop_entry=ttk.Entry(setup_Frame,width=5,textvariable=ycrop)
YCrop_entry.grid(column=3,row=7,sticky='w',pady=10,padx='10')
YCrop_entry.insert(0,'0')

HeightCrop_label=ttk.Label(setup_Frame,text="Height")
HeightCrop_label.grid(column=0,row=8,sticky='w',pady=10,padx='10')	

htcrop = tk.StringVar()

HeightCrop_entry=ttk.Entry(setup_Frame,width=5,textvariable=htcrop)
HeightCrop_entry.grid(column=1,row=8,sticky='w',pady=10,padx='10')
HeightCrop_entry.insert(0,'0')

WidthCrop_label=ttk.Label(setup_Frame,text="Width")
WidthCrop_label.grid(column=2,row=8,sticky='w',pady=10,padx='10')

wtcrop = tk.StringVar()	

WidthCrop_entry=ttk.Entry(setup_Frame,width=5,textvariable=wtcrop)
WidthCrop_entry.grid(column=3,row=8,sticky='w',pady=10,padx='10')
WidthCrop_entry.insert(0,'0')

CurrentCrop_label=ttk.Label(setup_Frame,text="Current set crop:",font="Helvetica 11 underline")
CurrentCrop_label.grid(column=0,row=9,sticky='w',pady=10,padx='10')

CurrentCrop_label2=ttk.Label(setup_Frame,text="X=0,Y=0\nHeight=0,Width=0")
CurrentCrop_label2.grid(column=0,row=10,sticky='w',pady=10,padx='10')


##########################################################################################

########ACQUISITION TAB FRAME 1 GUI ARRANGEMENT########

frame1=ttk.Frame(recording_details_Frame)
frame1.grid(row=0,sticky='nsew',padx=10)

recording_details_frame_label=ttk.Label(frame1,text="Recording Details",font="Helvetica 14 underline")
recording_details_frame_label.grid(column=0,row=0,sticky='w',pady=10,padx=10)

Folder_display=ttk.Label(frame1,text='Destination:',font='Helvetica 11 underline')
Folder_display.grid(column=0,row=1,sticky='w',padx=10,pady=10)

Folder_display_path=ttk.Label(frame1,text='Desktop/FLIR Recordings/')
Folder_display_path.grid(column=0,row=2,sticky='w',padx=10,pady=10)

Browse_button=ttk.Button(frame1,text='Browse',width=10,command=select_folder)
Browse_button.grid(column=0,row=3,sticky='w',padx=10,pady=10)

frame2=ttk.Frame(recording_details_Frame)
frame2.grid(row=1,sticky='nsew',padx=10)

Experiment_name_label=ttk.Label(frame2, text='Animal Name:')
Experiment_name_label.grid(column=0,row=0,sticky='w',padx=10,pady=10)

Experiment_name_entry=ttk.Entry(frame2,width=10)
Experiment_name_entry.grid(column=1,row=0,sticky='w',padx=10,pady=10)
Experiment_name_entry.bind('<Return>', select_experiment)
Experiment_name_entry.bind('<FocusOut>', select_experiment)

Recording_time_label=ttk.Label(frame2, text='Recording Time(s)')
Recording_time_label.grid(column=0,row=1,sticky='w',padx=10,pady=10)

Recording_time_entry=ttk.Entry(frame2,width=10)
Recording_time_entry.grid(column=1,row=1,sticky='w',padx=10,pady=10)
Recording_time_entry.insert(0,"300")

FPS_label=ttk.Label(frame2, text='Frames per second(fps)')
FPS_label.grid(column=2,row=1,sticky='w',padx=10,pady=10)

FPS_entry=ttk.Entry(frame2,width=5)
FPS_entry.grid(column=3,row=1,sticky='w',padx=10,pady=10)
FPS_entry.insert(0,"30")

FPV_label=ttk.Label(frame2, text='Frames per video(fpv)')
FPV_label.grid(column=2,row=2,sticky='w',padx=10,pady=10)

FPV_entry=ttk.Entry(frame2,width=5)
FPV_entry.grid(column=3,row=2,sticky='w',padx=10,pady=10)
FPV_entry.insert(0,"1000")

##########################################################################################

########ACQUISITION TAB FRAME 1 GUI ARRANGEMENT########

recording_frame_label=ttk.Label(recording_Frame,text="Recording\nControls",font="Helvetica 14 underline")
recording_frame_label.grid(column=0,row=0,sticky='w',pady=10,padx=10)

recordSTREAMbtn=ttk.Button(recording_Frame,width=10,text="Stream\nCamera",command=pooled_stream)
recordSTREAMbtn.grid(column=0, row=1,sticky='w',pady=10,padx=10)

#recordSTOP_STREAMbtn=ttk.Button(recording_Frame,width=10,text="Stop\nStream")
#recordSTOP_STREAMbtn.grid(column=1, row=1,sticky='w',pady=10,padx=10)

RECORD_btn=ttk.Button(recording_Frame,width=10,text="Record",command=pooled_record)
RECORD_btn.grid(column=0, row=2,sticky='w',pady=10,padx=10)

# ABORT_btn=ttk.Button(recording_Frame,width=10,text="Abort")
# ABORT_btn.grid(column=0, row=3,sticky='w',pady=10,padx=10)

Recording_status=ttk.Label(recording_Frame,text='Not Recording',font="Helevtica 11 underline")
Recording_status.grid(column=1,row=2,sticky='w',pady=10,padx=10)

##########################################################################################

#Start the GUI loop

if __name__ == '__main__':
	root.mainloop()
