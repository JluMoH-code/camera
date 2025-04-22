import cv2
import time

from CameraCommandManager import CameraCommandManager
from ThreadedCamera import ThreadedCamera

commandManager = CameraCommandManager()

current_pitch = 0
current_yaw = 0
step = 10

cap = ThreadedCamera("rtsp://192.168.144.25:8554/main.264").start()
print("Ожидание первого кадра...")
time.sleep(1) 

commandManager.base_command("auto-centering")

while True:
	img = cap.read()
	
	img = cv2.resize(img, (1280, 720))
	cv2.imshow("Main", img)
	
	key = cv2.waitKey(1)
	
	if key == ord("l"):
		commandManager.base_command("lock-mode")
	elif key == ord("f"):
		commandManager.base_command("fpv-mode")
	elif key == ord("o"):
		commandManager.base_command("follow-mode")
  
	elif key == ord("w"):
		current_pitch -= step
		commandManager.rotate(current_yaw * 10, current_pitch * 10)
		if current_pitch <= -90:
			current_pitch = -90
		
	elif key == ord("s"):
		current_pitch += step
		commandManager.rotate(current_yaw * 10, current_pitch * 10)
		if current_pitch >= 25:
			current_pitch = 25
			
	elif key == ord("a"):
		current_yaw += step
		commandManager.rotate(current_yaw * 10, current_pitch * 10)
		if current_yaw >= 135:
			current_yaw = 135
		
	elif key == ord("d"):
		current_yaw -= step
		commandManager.rotate(current_yaw * 10, current_pitch * 10)
		if current_yaw <= -135:
			current_yaw = -135
   
	elif key == ord("g"):
		response = commandManager.base_command("attitude-data")
		print(response)
  
	elif key == ord("c"):
		commandManager.base_command("auto-centering")
  
	elif key == ord("z"):
		response = commandManager.base_command("zoom-1")
		print(response)
  
	elif key == ord("x"):
		response = commandManager.base_command("zoom--1")
		print(response)
			
	elif key == ord("p"):
		response = commandManager.base_command("take-picture")
		print(response)
			
	elif key == ord("q"):
		break