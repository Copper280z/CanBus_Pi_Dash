# -*- coding: utf-8 -*-
"""
Created on Thu Oct 28 17:53:31 2021

@author: rocke
"""
import pygame
import numpy as np
import glob
import os
from PIL import Image
from data_limits import limits

class Group(pygame.sprite.Group):
    def update_data(self,data):
        for sprite in self.sprites():
            sprite.update_value(data)

class DoubleGauge(pygame.sprite.Sprite):
    def __init__(self,pos):
        pos_x,pos_y = pos
        super().__init__()
        self.size = 192
        self.radius = int(self.size/3.3)
        
        # self.angle_1 = -46
        # self.angle_2 = 45
        self.angles={'temp':-46,'oil':45}
        self.angle_limits = {'temp':(-48,-133),'oil':(45,133)}
        # self.font = pygame.freetype.SysFont('Arial', 24)
        self.original_image = pygame.image.load('temp_oil_gauge.png')

        self.center1 = (int(self.size/2), 0)
        self.center2 = (int(self.size/2), 192)
        self.centers={'temp':self.center1,'oil':self.center2}
        #####################################
        self.make_image()
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x,pos_y]
        
        
    def make_image(self):
        self.image = self.original_image.copy()#pygame.image.load('temp_oil_gauge.png')

        self.endpoints={}
        for key in self.angles:
            self.endpoints[key] = np.subtract(self.centers[key],(self.radius*np.cos(self.angles[key]*np.pi/180),self.radius*np.sin(self.angles[key]*np.pi/180)))
        # self.endpoint2 = np.subtract(self.center2,(self.radius*np.cos(self.angle_2*np.pi/180),self.radius*np.sin(self.angle_2*np.pi/180)))

        #pygame.Surface([self.size, self.size])
        
        pygame.draw.line(self.image , color=(228, 245, 211) , start_pos=self.center1, end_pos=self.endpoints['temp'] , width=6)
        pygame.draw.rect(self.image,(0,0,0),pygame.Rect(78,0,34,11))
        
        pygame.draw.line(self.image , color=(228, 245, 211) , start_pos=self.center2, end_pos=self.endpoints['oil'] , width=6)
        pygame.draw.rect(self.image,(0,0,0),pygame.Rect(78,192-11,34,11))
    def set_angle(self,key,change):
        
        self.angles[key]=self.angles[key]+change
        print(self.angles)
    def update(self):
        self.make_image()
        
    def update_value(self,data):
        pass

class SingleGauge(pygame.sprite.Sprite):
    def __init__(self,pos,field=False,name=False,boost=False):
        pos_x,pos_y = pos
        super().__init__()
        self.field=field
        self.size = 192
        self.radius = int(self.size/2.5)
        self.angle = -46
        self.angle_limits = (-45,225)
        self.name = name
        self.isboost=boost
        # self.font = pygame.freetype.SysFont('Arial', 24)
        if self.isboost:
            self.original_image = pygame.image.load('Booost Gauge.png')
        else:
            self.font = pygame.font.Font('Pixels-Regular.ttf',24)
            self.original_image = pygame.image.load('Blank Gauge.png')
        self.center_blk = pygame.image.load('Gauge Center.png')

        self.center = (int(self.size/2), int(self.size/2))
        # self.center2 = (int(self.size/2), 192)
        # self.centers={'temp':self.center1,'oil':self.center2}
        #####################################
        self.make_image()
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x,pos_y]
        
        
    def make_image(self):
        self.image = self.original_image.copy()
        self.endpoint = np.subtract(self.center,(self.radius*np.cos(self.angle*np.pi/180),self.radius*np.sin(self.angle*np.pi/180)))
        pygame.draw.line(self.image , color=(228, 245, 211) , start_pos=self.center, end_pos=self.endpoint , width=6)
        
        # pygame.draw.circle(self.image,(0,0,0),self.center,10)
        self.image.blit(self.center_blk,self.image.get_rect())
        if not self.isboost:
            text=self.font.render(self.name, True,(228,228,228))
            textrect = text.get_rect()
            self.image.blit(text,(self.size//2-textrect.width//2,152))
        
    def set_angle(self,change):
        
        self.angle=self.angle+change
        print(self.angle)
        
    def update(self):
        self.make_image() 
        
    def update_value(self,data):
        if self.field:
            if self.field in data.keys():
                self.angle = (self.angle_limits[0]*(limits[self.field][1]-data[self.field])+self.angle_limits[1]*(data[self.field]-limits[self.field][0]))/(limits[self.field][1]-limits[self.field][0])
                if self.angle<self.angle_limits[0]:
                    self.angle=self.angle_limits[0]
                if self.angle>self.angle_limits[1]:
                    self.angle=self.angle_limits[1]
                #print(self.angle)