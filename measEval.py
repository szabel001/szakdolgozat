#============================================================================================================#
#=============================================== Imports ====================================================#
from importing_modules import *
from measClass import *
#============================================================================================================#
#============================================ Initialize variable ===========================================#

Vcc = 5
#mqNames = ['MQ2', 'MQ3', 'MQ4', 'MQ5', 'MQ6', 'MQ7', 'MQ8', 'MQ9', 'MQ135', 'MQ137']
#SensorR0 = {'MQ2': 9.49, 'MQ3': 10.33, 'MQ4': 3735, 'MQ5': 499, 'MQ6': 568.24, 'MQ7': 28.41, 'MQ8': 6.46, 'MQ9': 61.5, 'MQ135': 499, 'MQ137': 6} 
#SensorRL = {'MQ2': 2, 'MQ3': 10, 'MQ4': 15, 'MQ5': 1, 'MQ6': 20, 'MQ7': 1, 'MQ8': 1, 'MQ9': 1, 'MQ135': 1, 'MQ137': 1,}
files = []              # to collect all opened files
files_mqtt = []
measDicts = []          # to collect all json from files
measDicts_mqtt = []
measObjects = []        # to collect all object created from jsons
corrcoefDict = {}       # to collect all corrcoef value from all measurements

Polynomial = np.polynomial.Polynomial

source = 'SD'

#============================================================================================================#
#=============================================== Import files (sd card) =====================================#

if source == 'SD':
    path = '\meresek\sd\\'
    arr = os.listdir('\meresek\sd')
    arr.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    for txtName in arr:
        files.append(open(path+txtName, 'r'))
    for file in files:
        measDicts.append(ast.literal_eval(file.read()))

#============================================================================================================#
#=============================================== Import files (mqtt) ========================================#
if source == 'MQTT':
    path = '\meresek\mqtt\\'
    arr = os.listdir('\meresek\mqtt')
    arr.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    for txtName in arr:
        files.append(open(path+txtName, 'r'))

    for file in files:
        lines = file.readlines()
        measList = []
        temp = {}
        for data in lines:
            line = json.loads(data)
            temp["time"] = line["time"]
            if line["topic"] == "esp32/temperature":
                temp["temperature"] = line["payload"]
            elif line["topic"] == "esp32/humidity":
                temp["humidity"] = line["payload"]
            elif line["topic"] == "esp32/MQ2":
                temp["MQ2"] = line["payload"]
            elif line["topic"] == "esp32/MQ3":
                temp["MQ3"] = line["payload"]
            elif line["topic"] == "esp32/MQ4":
                temp["MQ4"] = line["payload"]
            elif line["topic"] == "esp32/MQ5":
                temp["MQ5"] = line["payload"]
            elif line["topic"] == "esp32/MQ6":
                temp["MQ6"] = line["payload"]
            elif line["topic"] == "esp32/MQ7":
                temp["MQ7"] = line["payload"]
            elif line["topic"] == "esp32/MQ8":
                temp["MQ8"] = line["payload"]
            elif line["topic"] == "esp32/MQ9":
                temp["MQ9"] = line["payload"]
            elif line["topic"] == "esp32/MQ135":
                temp["MQ135"] = line["payload"]
            elif line["topic"] == "esp32/MQ137":
                temp["MQ137"] = line["payload"]
            elif line["topic"] == "esp32/nh3_ppm":
                temp["nh3_ppm"] = line["payload"]
            if line["topic"] == "esp32/nh3_ppm":
                measList.append(temp)
                temp = {}
        measDicts.append(measList)

#============================================================================================================#
#=============================================== Evaluations ================================================#

## Create list of measObjects
for measnumber, measDict in enumerate(measDicts):
    measObjects.append(MeasClass(measDict, measnumber+1))

def printAllCorrCoefValues():
    for meas in measObjects:
        meas.printCorrCoefValues()

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

def plotAllCorrCoefValues():
    valueDict = getAllCorrCoefValues()
    i = 0
    with plt.style.context('bmh'):
        plt.title('Correlation', fontsize=17)
        for i, name in enumerate(mqNames):
            plt.xlabel('Number of measurement', fontsize=10)
            plt.ylabel('All sensor\'s Correlation coefficient',  fontsize=10)
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
                col.set_title(f'{measObjects[i].getMeasnumber()}. measurement', fontsize=15)
                for name in mqNames:
                    col.plot(np.array(measObjects[i].time)/1000, np.array(measObjects[i].getSensorArray(name)), label= name, marker='.', linestyle='-',)
                    col.set_xlabel("Time (sec)", fontsize=10)
                    # col.set_ylabel("A/D converter's output (bit)")
                    col.set_ylabel("Sensor output (Voltage)", fontsize=10)
                col.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="5", prop = { "size": 7 }, fancybox=True, shadow=True, ncol=1)
                i+=1
    plt.show()

def averageOfPPM(x, y):
    # Pontok száma, amire átlagolni szeretnénk
    num_points = 10

    x = MeasClass.ZscoreFilter(x)
    y = MeasClass.ZscoreFilter(y)

    # Átlagolás az x tengely mentén
    x_averaged = np.array([np.array(x[i:i+num_points]).mean() for i in range(0, len(x), num_points)])

    # Átlagolás a y tengely mentén
    y_averaged = np.array([np.array(y[i:i+num_points]).mean() for i in range(0, len(y), num_points)])

    return x_averaged, y_averaged

def curvefit(x, y):
    fig=plt.figure()
    ax = fig.add_subplot(111)

    z=np.arange(1, len(x)+1) #start at 1, to avoid error from log(0)

    logA = np.log(z) #no need for list comprehension since all z values >= 1
    logB = np.log(y)

    m, c = np.polyfit(logA, logB, 1) # fit log(y) = m*log(x) + c
    y_fit = np.exp(m*logA + c) # calculate the fitted values of y 

    plt.plot(z, y, color = 'r')
    plt.plot(z, y_fit, ':')

    ax.set_yscale('symlog')
    ax.set_xscale('symlog')
    #slope, intercept = np.polyfit(logA, logB, 1)
    plt.xlabel("Pre_referer")
    plt.ylabel("Popularity")
    ax.set_title('Pre Referral URL Popularity distribution')

def getallNH3ppm():
    allNH3ppm = []
    for meas in measObjects:
        allNH3ppm.extend(meas.getSensorArray("nh3_ppm"))
    return np.array(allNH3ppm)

def getallRs():
    Vcc = 5
    allRs = {'MQ2': [], 'MQ3': [], 'MQ4': [], 'MQ5': [], 'MQ6': [], 'MQ7': [], 'MQ8': [], 'MQ9': [], 'MQ135': [], 'MQ137': []}
    for meas in measObjects:
        for name in mqNames:
            allRs[name].extend(meas.getSensorArray(name))
    for name in mqNames:
        RL = SensorRL[name]
        allRs[name] = ((Vcc / np.array(allRs[name]))-1) * RL
    return allRs

def plotMQCharacteristic():
    RsValues = getallRs()
    delete_items = []
    for name in mqNames: 
        nh3_ppm = getallNH3ppm()
        Rs = RsValues[name]
        for i in range(len(nh3_ppm)):
            if nh3_ppm[i] > 1000 or nh3_ppm[i] < 0.1 or Rs[i]/SensorR0[name] > 10000 or Rs[i]/SensorR0[name] < 0.000001:
                delete_items.append(i)
        new_Rs = np.delete(Rs, delete_items)
        new_nh3_ppm = np.delete(nh3_ppm, delete_items)
        with plt.style.context('bmh'):
            # x = averageOfPPM(getallNH3ppm(), RsValues[name] / SensorR0[name])[0]
            # y = averageOfPPM(getallNH3ppm(), RsValues[name] / SensorR0[name])[1]
            # curvefit(x, y)
            # plt.plot(x, a + b * np.log(x), color = "blue")
            plt.scatter(nh3_ppm, Rs/SensorR0[name], label= name, marker='.', linestyle='-',)
            # plt.scatter(x, y, label= name, c = "green", marker='.', linestyle='-', alpha=0.2,)
            plt.title(f"{name} Sensor\'s characteristic")
            plt.xlabel("PPM")
            plt.ylabel("Rs/R0")
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="5", prop = { "size": 7 }, fancybox=True, shadow=True, ncol=1)
            plt.xscale('log')
            plt.yscale('log')
        plt.show()

def plotOneMQ(num):
    meas = measObjects[num]
    for name in mqNames:
        RL = SensorRL[name]
        Rs = ((Vcc / np.array(meas.getSensorArray(name)))-1) * RL
        nh3_ppm = meas.getSensorArray('nh3_ppm')
        for i in range(len(nh3_ppm)):
            if nh3_ppm[i] > 1000 or nh3_ppm[i] < 0.01 or Rs/SensorR0[name] > 100 or Rs/SensorR0[name] < 0.01:
                Rs.pop(i)
                nh3_ppm.pop(i)
        with plt.style.context('bmh'):
            plt.scatter(nh3_ppm, Rs / SensorR0[name], label= name, marker='.', linestyle='-',)
            plt.title(f"{name} Sensor\'s characteristic")
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
# plotOneMQ(4)

for meas in measObjects:
    meas.plotMeas()


    #2 3 4 5 7