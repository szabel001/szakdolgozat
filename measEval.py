#============================================================================================================#
#=============================================== Imports ====================================================#
from importModules import *
from init import *
#============================================================================================================#
#=============================================== Evaluations ================================================#

def averageOfPPM(x = [], y = [], num_points = 5):
    x_averaged = np.array([np.array(x[i:i+num_points]).mean() for i in range(0, len(x), num_points)])
    y_averaged = np.array([np.array(y[i:i+num_points]).mean() for i in range(0, len(y), num_points)])
    return x_averaged, y_averaged

#https://stackoverflow.com/questions/43837179/best-fit-line-on-log-log-scales-in-python-2-7
def curvefit(x, y):
    fig=plt.figure()
    ax = fig.add_subplot(111)

    logA = np.log10(x) #no need for list comprehension since all z values >= 1
    logB = np.log10(y)

    m, c = np.polyfit(logA, logB, 1) # fit log(y) = m*log(x) + c
    y_fit = 10 ** (m*logA + c) # calculate the fitted values of y 

    plt.plot(x, y_fit, color = 'black', linestyle = 'dashdot')

    ax.set_yscale('log')
    ax.set_xscale('log')

    return m, c
    
def getallNH3ppm():
    allNH3ppm = []
    for meas in measObjects:
        allNH3ppm.extend(meas.getSensorArray("nh3_ppm"))
    return np.array(allNH3ppm)

def getallRs():
    allRs = {'MQ2': [], 'MQ3': [], 'MQ4': [], 'MQ5': [], 'MQ6': [], 'MQ7': [], 'MQ8': [], 'MQ9': [], 'MQ135': [], 'MQ137': []}
    for meas in measObjects:
        for name in mqNames:
            allRs[name].extend(meas.getSensorArray(name))
    for name in mqNames:
        RL = SensorRL[name]
        allRs[name] = ((Vcc / np.array(allRs[name]))-1) * RL
    return allRs

def getAllCorrCoefValues():
    for name in mqNames:
        corrcoefDict[name] = np.array([])
    for meas in measObjects:
        for name in mqNames:
                corrcoefDict[name] = np.append(corrcoefDict[name], meas.getCorrCoefValues(name))
            
    return corrcoefDict

def printAVGCCVal():
    corrcoefDict = getAllCorrCoefValues()
    for name in mqNames:
        print(f"{name} szenzor átlagos r értéke: {corrcoefDict[name].mean():.4f}\n")

def plotAllCCVal():
    valueDict = getAllCorrCoefValues()
    with plt.style.context('bmh'):
        plt.title('Korreláció', fontsize=17)
        for name in mqNames:
            plt.xlabel('Mérés sorszáma', fontsize=10)
            plt.ylabel('Korrelációs együttható',  fontsize=10)
            plt.plot(range(1, len(valueDict[name])+1), np.absolute(valueDict[name]) , c=mqColors[name], label= name, marker='.', linestyle='-',)
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    plt.show()

def plotAllMeas():
    i = 0
    with plt.style.context('bmh'):
        fig, ax = plt.subplots(nrows=2, ncols=3)
        for row in ax:
            for col in row:
                col.set_title(f'{measObjects[i].getMeasnumber()}. mérés', fontsize=15)
                for name in mqNames:
                    col.plot(np.array(measObjects[i].time)/1000, np.array(measObjects[i].getSensorArray(name)), label= name, marker='.', linestyle='-',)
                    col.set_xlabel("Idő (sec)", fontsize=10)
                    col.set_ylabel("Szenzor kimenet (Feszültség - V)", fontsize=10)
                col.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="5", prop = { "size": 7 }, fancybox=True, shadow=True, ncol=1)
                i+=1
    plt.show()

def plotMQChar():
    RSValues = getallRs()
    for name in mqNames:
        with plt.style.context('bmh'):
            nh3_ppm = getallNH3ppm()
            RS_R0 = RSValues[name] / SensorR0[name]
            m, b = curvefit(nh3_ppm, RS_R0)
            nh3_ppm, RS_R0 = averageOfPPM(nh3_ppm, RS_R0)
            plt.scatter(nh3_ppm, RS_R0, c = 'g', label= name, marker='.', linestyle='-',)
            plt.text(nh3_ppm[0], min(RS_R0), 'm = ' + str(m) + '\nb = ' + str(b), fontsize = 10, bbox=dict(facecolor='none',edgecolor='black',boxstyle='square')) 
            plt.title(f"{name} szenzor karakterisztikája")
            plt.xlabel("PPM")
            plt.ylabel("Rs/R0")
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="5", prop = { "size": 7 }, fancybox=True, shadow=True, ncol=1)
            plt.xscale('log')
            plt.yscale('log')

        plt.show()

printAVGCCVal()
plotMQChar()