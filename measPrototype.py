#============================================================================================================#
#=============================================== Imports ====================================================#
from importing_modules import *
from init import *

slope = {'MQ2': 9.49, 'MQ3': 10.33, 'MQ4': 3735, 'MQ5': 499, 'MQ6': 568.24, 'MQ7': 28.41, 'MQ8': 6.46, 'MQ9': 61.5, 'MQ135': 499, 'MQ137': 20} 
intercept =  {'MQ2': 2, 'MQ3': 10, 'MQ4': 15, 'MQ5': 1, 'MQ6': 20, 'MQ7': 1, 'MQ8': 1, 'MQ9': 1, 'MQ135': 1, 'MQ137': 1,}

def calcSensorPPM(meas, mqName):
    Vcc = 5
    
    RL = SensorRL[mqName]      #The value of resistor RL is 1K --> measured
    R0 = SensorR0[mqName]     #The value of resistor R0 is 1K --> measured + calculated
    m = slope[mqName]    #Enter calculated Slope
    b = intercept[mqName]     #Enter calculated intercept
    VRL = meas.getSensorArray(mqName) * 3.3 / 4095
    RS = ((Vcc/VRL)-1) * RL
    ratio = RS/R0                           #find ratio Rs/Ro
    ppm = pow(10, ((np.log10(ratio)-b)/m))     #use formula to calculate ppm
    return ppm