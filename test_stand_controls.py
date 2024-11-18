#
#   Control/Aquisition Library for FAST/IOTA magnet test stand
#
#   John Wieland, Jan 17, 2024
###############################################################################

from time import sleep
import numpy as np
import RPi.GPIO as GPIO
import socket

###############################################################################

class stand:

    def __init__(self):
        #set up raspberry pi GPIO pins for stepper motors
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)

        self.Dpins = [16,12,18] #x,y,z axes pins for direction
        self.Ppins = [11,7,13] #x,y,z axes pins for steps
        self.sdir = [True,False,False] #directional convention
        #Axes are selected to be right handed with +y "up"

        for pin in (self.Dpins+self.Ppins):
            GPIO.setup(pin, GPIO.OUT)

    #Moves the test stand from point ri to rf
    #where locations are given as vectors of [x,y,z]
    def move_pt(self,ri,rf,lstep_mm=1e3,t_delay=5e-6):
        ri = np.array(ri)
        rf = np.array(rf)
        ds = np.round((rf - ri)*lstep_mm,0).astype(int)
    
        #add logical statment for direction of step
        dirArr = np.equal(np.where(ds>0,True,False),self.sdir)
    
        GPIO.output(self.Dpins,dirArr.tolist())
    
        ds = np.abs(ds)
    
        for i in range(ds.max()):
            stepCheck = np.where(ds>i,True,False)
    
            #convoluted typcasting to get around GPIO not accepting 
            #numpy arrays
            GPIO.output(np.array(self.Ppins)[stepCheck].tolist(),True)
            sleep(t_delay)
            GPIO.output(self.Ppins,False)
            sleep(t_delay)

    #Function to move an integer number of steps along a single, selected axis
    #intended for testing purposes
    def move_step(self,step,axis,t_delay=5e-6):
        
        if axis.lower() == "x" or axis.lower() == "mid":
            axInd = 0
        elif axis.lower() == "y" or axis.lower() == "short":
            axInd = 1
        elif axis.lower() == "z" or axis.lower() == "long":
            axInd = 2
        else:
            raise Exception("Valid Axis Not supplied")
    
        #add logical and statment for flipping required axes
        if step < 0:
            GPIO.output(self.Dpins[axInd],False == self.sdir[axInd])
        else:
            GPIO.output(self.Dpins[axInd],True == self.sdir[axInd])
            
        for i in range(abs(step)):
            GPIO.output(self.Ppins[axInd],True)
            sleep(t_delay)
            GPIO.output(self.Ppins[axInd],False)
            sleep(t_delay)

    #cleanup attribute for end of acquisition
    def cleanup(self):
        GPIO.cleanup()

###############################################################################

class probe:

    #initialize connection with lakeshore crytronics teslameter
    def __init__(self,
                 TCP_IP = '192.168.0.12',
                 TCP_PORT =7777,
                 BUFFER_SIZE = 1024):
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.BUFFER_SIZE = BUFFER_SIZE
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.TCP_IP,self.TCP_PORT))


    #pulls hall probe data from teslameter
    #TODO verify delay times, time.sleep in seconds
    def take_data(self,convert = True):
        sleep(0.50) #delay for clearing stale data from buffer after movement
        command = b'FETC:DC? ALL' + b'\n'
        self.s.send(command)
        sleep(0.30) #delay for communication to complete
        vals = (self.s.recv(self.BUFFER_SIZE).decode("utf-8")).split(',')
        vallist = [float(ival) for ival in vals]
    
        #convert direction of probe output to match test stand axes
        if convert:
            valArr = np.array(vallist)
            #swap x and y axis on hall probe
            valArr[[2,1]] = valArr[[1,2]]
            #swap sign of y axis
            valArr[2] = -valArr[2]
            #return only directional info, magnitude unneccesary
            return valArr[1:].tolist()
        else:
            return vallist

    #close attribute for end of acquisition
    def close(self):
        self.s.close()

###############################################################################
