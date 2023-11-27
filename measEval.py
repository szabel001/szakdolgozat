#============================================================================================================#
#=============================================== Imports ====================================================#
from importing_modules import *
from init import *
#============================================================================================================#
#=============================================== Evaluations ================================================#

## Create list of measObjects
for measnumber, measDict in enumerate(measDicts):
    measObjects.append(MeasClass(measDict, measnumber+1))

def averageOfPPM(x, y):
    num_points = 3
    x_averaged = np.array([np.array(x[i:i+num_points]).mean() for i in range(0, len(x), num_points)])
    y_averaged = np.array([np.array(y[i:i+num_points]).mean() for i in range(0, len(y), num_points)])

    return x_averaged, y_averaged

#https://stackoverflow.com/questions/43837179/best-fit-line-on-log-log-scales-in-python-2-7
def curvefit(x, y):
    fig=plt.figure()
    ax = fig.add_subplot(111)

    logA = np.log(x) #no need for list comprehension since all z values >= 1
    logB = np.log(y)

    m, c = np.polyfit(logA, logB, 1) # fit log(y) = m*log(x) + c
    y_fit = np.exp(m*logA + c) # calculate the fitted values of y 

    plt.plot(x, y_fit, color = 'black', linestyle = 'dashdot')

    ax.set_yscale('log')
    ax.set_xscale('log')
    m, b = np.polyfit(logA, logB, 1)

    #https://www.statology.org/curve-fitting-python/
    model5 = np.poly1d(np.polyfit(x, y, 5))
    polyline = np.linspace(0.01, 1000, 50)
    plt.plot(np.log(polyline), model5(polyline), color='orange')


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
    for meas in measObjects:
        oldValue = []           # to save the previous values of corrcoefDict (needed to update the dict)
        for name in mqNames:
            if name in corrcoefDict:
                oldValue = corrcoefDict[name]
                oldValue.append(meas.getCorrCoefValues(name))
                corrcoefDict[name] = oldValue
            else:
                corrcoefDict[name] = [meas.getCorrCoefValues(name)]
    return corrcoefDict

def printAllCorrCoefValues():
    for meas in measObjects:
        meas.printCorrCoefValues()

def plotAllCorrCoefValues():
    valueDict = getAllCorrCoefValues()
    i = 0
    with plt.style.context('bmh'):
        plt.title('Korreláció', fontsize=17)
        for i, name in enumerate(mqNames):
            plt.xlabel('Mérés sorszáma', fontsize=10)
            plt.ylabel('Összes szenzor korrelációs koefficienciája',  fontsize=10)
            plt.plot(range(1, len(valueDict[name])+1), np.absolute(valueDict[name]) , c=np.random.rand(3,), label= name, marker='.', linestyle='-',)
            i+=1
            # Put a legend below current axis
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    plt.show()

def plotAllMeasurements():
    i = 0
    with plt.style.context('bmh'):
        fig, ax = plt.subplots(nrows=3, ncols=3)
        for row in ax:
            for col in row:
                col.set_title(f'{measObjects[i].getMeasnumber()}. mérés', fontsize=15)
                for name in mqNames:
                    col.plot(np.array(measObjects[i].time)/1000, np.array(measObjects[i].getSensorArray(name)), label= name, marker='.', linestyle='-',)
                    col.set_xlabel("Idő (sec)", fontsize=10)
                    # col.set_ylabel("A/D converter's output (bit)")
                    col.set_ylabel("Szenzor kimenet (Feszültség - V)", fontsize=10)
                col.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="5", prop = { "size": 7 }, fancybox=True, shadow=True, ncol=1)
                i+=1
    plt.show()

def plotMQCharacteristic():
    RsValues = getallRs()
    delete_items = []
    for name in mqNames: 

        nh3_ppm = getallNH3ppm()
        Rs = np.array([x for _,x in sorted(zip(nh3_ppm, RsValues[name]))])
        nh3_ppm = sorted(nh3_ppm)

        for i in range(len(nh3_ppm)):
            if nh3_ppm[i] > 1000 or Rs[i]/SensorR0[name] > 10:
                delete_items.append(i)
        new_Rs = np.delete(Rs, delete_items)
        new_nh3_ppm = np.delete(nh3_ppm, delete_items)

        with plt.style.context('bmh'):
            avgPPM = averageOfPPM(nh3_ppm, Rs / SensorR0[name])
            nh3_ppm = avgPPM[0]
            Rs = avgPPM[1]
            nh3_ppm = MeasClass.ZscoreFilter(nh3_ppm)
            Rs = MeasClass.ZscoreFilter(Rs)
            curvefit(nh3_ppm, Rs/SensorR0[name])
            
            plt.scatter(nh3_ppm, Rs/SensorR0[name], c = 'g', label= name, marker='.', linestyle='-',)

            plt.title(f"{name} szenzor karakterisztikája")
            plt.xlabel("PPM")
            plt.ylabel("Rs/R0")
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="5", prop = { "size": 7 }, fancybox=True, shadow=True, ncol=1)
            plt.xscale('log')
            plt.yscale('log')

        plt.show()

def plotOneMQchar(num):
    meas = measObjects[num]
    for name in mqNames:
        RL = SensorRL[name]
        Rs = ((Vcc / np.array(meas.getSensorArray(name)))-1) * RL
        nh3_ppm = meas.getSensorArray('nh3_ppm')
        for i in range(len(nh3_ppm)):
            if nh3_ppm[i] > 1000 or nh3_ppm[i] < 0.01 or Rs[i]/SensorR0[name] > 100 or Rs[i]/SensorR0[name] < 0.01:
                np.delete(Rs, i)
                np.delete(nh3_ppm, i)
        with plt.style.context('bmh'):
            plt.scatter(nh3_ppm, Rs / SensorR0[name], label= name, marker='.', linestyle='-',)
            plt.title(f"{name} szenzor karakterisztikája")
            plt.xlabel("PPM")
            plt.ylabel("Rs/R0")
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="5", prop = { "size": 7 }, fancybox=True, shadow=True, ncol=1)
            plt.xscale('log')
            plt.yscale('log')
        plt.show()

#============================================================================================================#
#=============================================== Call functions =============================================#

# printAllCorrCoefValues()
plotAllCorrCoefValues()
# plotAllMeasurements()
plotMQCharacteristic()
# plotOneMQ(5)

#for meas in measObjects:
#    meas.plotMeas()