# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 20:04:40 2021

@author: rocke
"""
import struct

keys = {1520:['SecL', 'PW', 'PW2', 'RPM'],
        1522:['Barometer','MAP','MAT','CLT'],
        1523:['TPS','Batt V','AFR','AFR 2'],
        1537:['Boost duty 1','Boost duty 2', 'Boost target 1', 'Boost target 2']}

coeffs = {'SecL':[1,1,0],
          'PW':[1,1000,0],
          'PW2':[1,1000,0],
          'RPM':[1,1,0],
          'Barometer':[1,10,0],
          'MAP':[1,10,0],
          'MAT':[1,10,0],
          'CLT':[1,10,0],
          'TPS':[1,10,0],
          'Batt V':[1,10,0],
          'AFR':[1,10,0],
          'AFR 2':[1,10,0],
          'Boost duty 1':[1,1,0],
          'Boost duty 2':[1,1,0],
          'Boost target 1':[1,10,0],
          'Boost target 2':[1,10,0]}

dtype = {'SecL':'>H',
          'PW':'>H',
          'PW2':'>H',
          'RPM':'>H',
          'Barometer':'>h',
          'MAP':'>h',
          'MAT':'>h',
          'CLT':'>h',
          'TPS':'>h',
          'Batt V':'>h',
          'AFR':'>h',
          'AFR 2':'>h',
          'Boost duty 1':'>h',
          'Boost duty 2':'>h',
          'Boost target 1':'>h',
          'Boost target 2':'>h'}

offset = {'SecL':0,
          'PW':2,
          'PW2':4,
          'RPM':6,
          'Barometer':0,
          'MAP':2,
          'MAT':4,
          'CLT':6,
          'TPS':0,
          'Batt V':2,
          'AFR':4,
          'AFR 2':4,
          'Boost duty 1':0,
          'Boost duty 2':2,
          'Boost target 1':4,
          'Boost target 2':6}

length = {'SecL':2,
          'PW':2,
          'PW2':2,
          'RPM':2,
          'Barometer':2,
          'MAP':2,
          'MAT':2,
          'CLT':2,
          'TPS':2,
          'Batt V':2,
          'AFR':2,
          'AFR 2':2,
          'Boost duty 1':2,
          'Boost duty 2':2,
          'Boost target 1':2,
          'Boost target 2':2}

def decode(can_bytes):
    #print(can_bytes)
    output = {}
    try:
        ID = can_bytes.id
    except AttributeError:
        ID = can_bytes.arbitration_id
    #print(ID)
    if ID in keys.keys():
        for key in  keys[ID]:
            output[key] = coeffs[key][0]*struct.unpack(dtype[key],can_bytes.data[offset[key]:(offset[key]+length[key])])[0]/coeffs[key][1]+coeffs[key][2]
    
    return output
        