#============================================================================================================#
#=============================================== Imports ====================================================#
from importModules import *
from init import *

m = {'MQ2': -0.265896, 'MQ8': -0.127572, 'MQ137': -0.2701}
b = {'MQ2': 0.227674, 'MQ8': -0.089634, 'MQ137': -0.2276}
def calcNH3ppm(meas, mqName = "MQ137"):
    Vcc = 5
    RL = SensorRL[mqName]      #The value of resistor RL is 1K --> measured
    R0 = SensorR0[mqName]     #The value of resistor R0 is 1K --> measured + calculated
    VRL = meas.getSensorArray(mqName)
    RS = ((Vcc/VRL)-1) * RL
    ratio = RS/R0
    ppm = pow(10, ((np.log10(ratio)-b[mqName])/m[mqName]))
    if(mqName == 'MQ2'):
        ppm = ppm / 20
    if(mqName == 'MQ8'):
        ppm = ppm * 2
    idxs = np.where(ppm > 100)
    for i in idxs:
        ppm[i] = 0
    return ppm

def plotPPM():
    ppms = {'MQ2': [], 'MQ8':[], 'MQ137':[]}
    hum = []
    temp = []
    keysList = [key for key in ppms]
    for meas in measObjects[:]:
        for key in keysList:
            ppms[key] = np.append(ppms[key], calcNH3ppm(meas, key))
        hum.extend(meas.getSensorArray('humidity'))
        temp.extend(meas.getSensorArray('temperature'))
    with plt.style.context('bmh'):
        plt.scatter(list(range(len(ppms[key]))), hum, label= 'páratartalom', marker='v', linestyle='-', color='blue')
        plt.scatter(list(range(len(ppms[key]))), temp, label= 'hőmérséklet', marker='*', linestyle='-', color='green')
        for key in keysList:
            plt.scatter(list(range(len(ppms[key]))), ppms[key], label= key, marker='.', linestyle='-', color=mqColors[key])
            plt.xlabel("Mérési pont sorszáma")
            plt.ylabel("Számított PPM")
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="5", fancybox=True, shadow=True, ncol=1)
    plt.show()

def plotDiff():
    hum = []
    temp = []
    ppms = {'MQ2': [], 'MQ8':[], 'MQ137':[]}
    idx  = np.where(ppms['MQ137'] == 0)
    keysList = [key for key in ppms]
    for meas in measObjects[:]:
        for key in keysList:
            ppms[key] = np.append(ppms[key], calcNH3ppm(meas, key))
        hum.extend(meas.getSensorArray('humidity'))
        temp.extend(meas.getSensorArray('temperature'))

    with plt.style.context('bmh'):
        for key in keysList:
            plt.plot(list(range(len(ppms[key]))), hum, label= 'páratartalom', linestyle='-', color='blue', linewidth=2, alpha=0.4)
            plt.plot(list(range(len(ppms[key]))), temp, label= 'hőmérséklet',    linestyle='-', color='orange',linewidth=2, alpha=0.4)
            offset = ppms['MQ137'] - ppms[key] 
            plt.scatter(list(range(len(ppms[key]))), ppms['MQ137'], label= 'MQ137', marker='.', linestyle='-', color='black')
            plt.scatter(list(range(len(ppms[key]))), ppms[key], label= key, marker='.', linestyle='-', color=mqColors[key])
            plt.scatter(list(range(len(ppms[key]))), offset, label= key + ' offset', marker='v', linestyle='dashdot', color='green')
            plt.xlabel("Mérési pont sorszáma")
            plt.ylabel("Számított PPM")
            plt.title(f"{key} szenzor ")
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="10", fancybox=True, shadow=True, ncol=1)
            plt.show()