#============================================================================================================#
#=============================================== Imports ====================================================#
from importModules import *
from init import *

#m = {'MQ2': -0.265896, 'MQ8': -0.127572, 'MQ137': -0.2701}
#b = {'MQ2': 0.227674, 'MQ8': 0.089634, 'MQ137': -0.2276}

m = {'MQ2': -0.665896, 'MQ8': -0.327572, 'MQ137': -0.2701}
b = {'MQ2': 0.227674, 'MQ8': 0.089634, 'MQ137': -0.2276}
def calcNH3ppm(meas, mqName = "MQ137"):
    Vcc = 5
    RL = SensorRL[mqName]      #The value of resistor RL is 1K --> measured
    R0 = SensorR0[mqName]     #The value of resistor R0 is 1K --> measured + calculated
    VRL = meas.getSensorArray(mqName)
    RS = ((Vcc/VRL)-1) * RL
    ratio = RS/R0
    ppm = pow(10, ((np.log10(ratio)-b[mqName])/m[mqName]))
    idxs = np.where(ppm > 200)
    for i in idxs:
        ppm[i] = 0
    return ppm

def plotPPMs():
    ppms = {'MQ2': [], 'MQ8':[], 'MQ137':[]}
    keysList = [key for key in ppms]
    for meas in measObjects[:]:
        for key in keysList:
            ppms[key] = np.append(ppms[key], calcNH3ppm(meas, key))

    for key in keysList:
        with plt.style.context('bmh'):
            plt.scatter(list(range(len(ppms[key]))), ppms[key], label= key, marker='.', linestyle='-', color=mqColors[key])
            plt.xlabel("Mérési pont sorszáma")
            plt.ylabel("Számított PPM")
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="5", fancybox=True, shadow=True, ncol=1)
    plt.show()

plotPPMs()