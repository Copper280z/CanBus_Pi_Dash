# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 19:58:52 2021

@author: rocke
"""

"""
Getting this working on the Pi was harder than expected.
created venv for this project
compiled Pillow from source with all options enabled - not sure how much of that was required
also needed to install pygame SDL dependencies and in the future would suggest installing all build dependencies - sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libfreetype6-dev python3-setuptools python3-dev python3 libportmidi-dev
https://www.pygame.org/wiki/CompileUbuntu?parent=

Calibrating the touchscreen also sucked. Current (2021) raspbian uses libinput consequently the best way to calibrate teh screen is to clone and build https://github.com/kreijack/xlibinput_calibrator, then add
Section "InputClass"
        Identifier      "calibration"
        MatchProduct    "WaveShare WS170120"
        MatchDriver     "libinput"
        Option "CalibrationMatrix" "1.103964 -0.001097 -0.052464 -0.007270 1.18$
EndSection

/usr/share/X11/xorg.conf.d/40-libinput.conf

"""
# Import and initialize the pygame library

import pygame
import numpy as np
import glob
import os
from PIL import Image
from sprites import DoubleGauge, SingleGauge,Group
import time
import threading
import queue
import MS_can_def
import can

def Spacing(res,shape,sz):
    res_x,res_y = res
    n_x,n_y = shape
    
    x,y = np.meshgrid(np.arange(n_x),np.arange(n_y))
    x=x+1
    y=y+1
    x_pix=np.asarray(x*((res_x-(n_x*sz))/(n_x+1))+((2*x-1)*sz/2),dtype=np.uint16)
    y_pix=np.asarray(y*((res_y-(n_y*sz))/(n_y+1))+((2*y-1)*sz/2),dtype=np.uint16)

    coords = np.array((x_pix.ravel(),y_pix.ravel())).T
    return coords

def get_can_data():
    print('started CAN Bus thread')
    cur_thread = threading.current_thread()
    cur_thread.run=True
    while cur_thread.run:
        msg = reader.get_message()
        if not data_queue.full():
            if msg is not None:
                data_queue.put_nowait(msg)
                
        else:
            with data_queue.mutex:
                data_queue.queue.clear()
                
            data_queue.put_nowait(msg)
            

    

can_interface = 'can0'
bus = can.interface.Bus(can_interface, bustype='socketcan')
reader = can.BufferedReader()
listeners = [reader]
notifier = can.Notifier(bus, listeners)

data_queue = queue.Queue(maxsize=10)
can_thread = threading.Thread(target = get_can_data)
can_thread.start()

pygame.init()

# Set up the drawing window

res_x,res_y = 800,480

screen =pygame.display.set_mode([res_x, res_y],pygame.DOUBLEBUF|pygame.HWSURFACE|pygame.FULLSCREEN|pygame.SCALED)#pygame.display.set_mode([res_x, res_y])

gauge_names = ['RPM','MAP','TPS','MAT','CLT','WG DC','AFR','BST TG']
fields = ['RPM','MAP','TPS','MAT','CLT','Boost duty 1','AFR','Boost target 1']

slots_8 = Spacing((res_x,res_y),(4,2),192)
slots_3 = Spacing((res_x,res_y),(3,1),192)


pages={}
animated_gauges = Group()
gauges = {}
for i,zipped in enumerate(zip(gauge_names,fields)):
    name,field = zipped
    gauges[name]=SingleGauge(slots_8[i],field,name,False)
    animated_gauges.add(gauges[name])
    
pages[1] = animated_gauges

animated_gauges2 = Group()
gauge12=DoubleGauge(slots_3[2])
gauge22=SingleGauge(slots_3[1],'AFR','AFR')
gauge32=SingleGauge(slots_3[0],boost=True)
animated_gauges2.add(gauge12)
animated_gauges2.add(gauge22)
animated_gauges2.add(gauge32)

pages[2] = animated_gauges2

# Run until the user asks to quit
clock = pygame.time.Clock()

running = True
# pygame.key.set_repeat(1,5)
n=1
quitTimer=False
data={}
while running:
    msgs = []
    print(data_queue.qsize())
    if not data_queue.empty():
        for i in range(5):
            try:
                msgs.append(data_queue.get_nowait())
            except Exception as e:
                print(e)
        
            if  data_queue.empty():
                break
    
    for msg in msgs:
        data.update(MS_can_def.decode(msg))
    
    
    animated_gauges.update_data(data)
    
    if quitTimer:
        if (time.monotonic()-quitTimer)>5:
            running = False    
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
            # if pressed[pygame.K_z]:
            print('changing pages')
            if n==1:
                n=2
            else:
                n=1

            if not quitTimer:
                quitTimer=time.monotonic()
                
        
                
        if event.type == pygame.FINGERUP or event.type == pygame.MOUSEBUTTONUP:
            quitTimer=False
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_q]:
                   running = False
        if pressed[pygame.K_UP]:
            gauge12.set_angle('temp',1)
        if pressed[pygame.K_DOWN]:
            gauge12.set_angle('temp',-1)
        if pressed[pygame.K_LEFT]:
            gauge12.set_angle('oil',1)
        if pressed[pygame.K_RIGHT]:
            gauge12.set_angle('oil',-1)
        # if pressed[pygame.K_w]:
        #     gauge2.set_angle(1)
        # if pressed[pygame.K_s]:
        #     gauge2.set_angle(-1) 
            

            
    screen.fill((56, 56, 60))
    pages[n].draw(screen)
    pages[n].update()



    # Flip the display

    pygame.display.flip()

    #clock.tick(60)

# Done! Time to quit.

pygame.quit()

reader.stop()
can_thread.run=False
can_thread.join()