#
#    Example cylindrical scan for testStandControl module
#
#    John Wieland, Nov 2024
###############################################################################

import numpy as np
from matplotlib import pyplot as plt
import testStandControlsClass as tsc
import time

###############################################################################

#generates a list of x,y coordinates on a circle of Nth points
#R0 radius in mm
def pt_lists_cyl(Nth,R0):
    thlist = np.arange(Nth)*2*np.pi/Nth
    Xlist = R0*np.cos(thlist)
    Ylist = R0*np.sin(thlist)
    return Xlist,Ylist

#generates points on a cylinder
#Nth points in azimuth
#R0 radius in mm
#zArr is array of z-axis positions, can be repeated for hysteresis compensation
def cyl_planes(Nth,R0,zArr):
    
    xArr,yArr = pt_lists_cyl(Nth,R0)
    
    zArr = np.sort(zArr)
    Nplane = zArr.shape
    
    xArr = np.tile(xArr,Nplane)
    yArr = np.tile(yArr,Nplane)
    zArr = np.repeat(zArr,Nth)

    return(np.stack((xArr,yArr,zArr)).T)

###############################################################################

#decide on longitudinal scan positions
Zlist = np.linspace(-50,50,11)
#optionally double back zlist for hysteresis minimization
#Zlist = np.concatenate((Zlist,np.flip(Zlist)))

#generate point cloud of scan positions
pos_data = cyl_planes(32,16,Zlist)
#generate empty array of same size for storing magnetic field data
mag_data = np.zeros(pos_data.shape)

#initializing test stand classes sets up raspberry pi movement controls
#and lakeshore crytronics teslameter
stand = tsc.stand()
probe = tsc.probe()

#paranoid wait time after setup
time.sleep(5)

#define origin point
r0 = [0,0,0]

ri = r0
stepNum = pos_data.shape[0]

#loop through measurment points
#move command only takes relative motion
for i,pos in enumerate(pos_data):
    stand.move_pt(ri,pos)
    mag_data[i] = probe.take_data()
    ri = pos
    
    print(f"Progress {round(i*100/stepNum,0)}%")

#move back to defined origin
stand.move_pt(ri,r0)

#close and cleanup controls
stand.cleanup()
probe.close()

np.save("mag_data",mag_data)
np.save("pos_data",pos_data)

print("=== SCAN COMPLETE ===")
