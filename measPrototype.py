#============================================================================================================#
#=============================================== Imports ====================================================#
from importing_modules import *
from init import *

m = {'MQ2': -0.27324, 'MQ8': -0.12571, 'MQ137': -0.27598}
b = {'MQ2': -1.67173, 'MQ8': -1.63444, 'MQ137': -3.08072}

def calcSensorPPM(meas, mqName):
    Vcc = 5
    RL = SensorRL[mqName]      #The value of resistor RL is 1K --> measured
    R0 = SensorR0[mqName]     #The value of resistor R0 is 1K --> measured + calculated
    VRL = meas.getSensorArray(mqName) * 3.3 / 4095
    RS = ((Vcc/VRL)-1) * RL
    ratio = RS/R0                           #find ratio Rs/Ro
    ppm = pow(10, ((np.log10(ratio)-b[mqName])/m[mqName]))     #use formula to calculate ppm
    return ppm