import os
import json #for import from mqtt
import ast
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats #for Z-score filter
from rrcf import RCTree # for RRCF filter
#============================================================================================================#
#============================================ Initialize variable ===========================================#

Vcc = 5
mqNames = ['MQ2', 'MQ3', 'MQ4', 'MQ5', 'MQ6', 'MQ7', 'MQ8', 'MQ9', 'MQ135', 'MQ137']
SensorR0 = {'MQ2': 10, 'MQ3': 10, 'MQ4': 10, 'MQ5': 10, 'MQ6': 10, 'MQ7': 10, 'MQ8': 10, 'MQ9': 10, 'MQ135': 10, 'MQ137': 14}
SensorRL = {'MQ2': 1, 'MQ3': 1, 'MQ4': 1, 'MQ5': 1, 'MQ6': 1, 'MQ7': 1, 'MQ8': 1, 'MQ9': 1, 'MQ135': 1, 'MQ137': 1}
files = []              # to collect all opened files
files_mqtt = []
measDicts = []          # to collect all json from files
measDicts_mqtt = []
measObjects = []        # to collect all object created from jsons
corrcoefDict = {}       # to collect all corrcoef value from all measurements

#============================================================================================================#
#=============================================== Import files (sd card) =====================================#

i = 1
while os.path.isfile(f"szakdolgozat\meresek\sd\meas_{i}.txt"):
    files.append(open(f"szakdolgozat\meresek\sd\meas_{i}.txt", 'r'))
    i += 1

for file in files:
    measDicts.append(ast.literal_eval(''.join((file.read(),']'))))

#============================================================================================================#
#=============================================== Import files (mqtt) ========================================#
'''
i = 1
while os.path.isfile(f"meresek\mqtt\mqtt_meas_{i}.txt"):
    files.append(open(f"meresek\mqtt\mqtt_meas_{i}.txt", 'r'))
    i += 1

for file in files:
    lines = file.readlines()
    measList = []
    temp = {}
    for data in lines:
        line = json.loads(data)
        temp["time"] = line["time"]-1698103996217
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

'''
#============================================================================================================#
#=============================================== Create measClass============================================#

class measClass:
    def __init__(self, meas = [], measnumber = None):
        self.measnumber = measnumber
        self.meas = meas
        self.time = self.setValues("time")
        self.temperature = self.setValues("temperature")
        self.humidity = self.setValues("humidity")
        self.MQ2 = self.setValues("MQ2")
        self.MQ3 = self.setValues("MQ3")
        self.MQ4 = self.setValues("MQ4")
        self.MQ5 = self.setValues("MQ5")
        self.MQ6 = self.setValues("MQ6")
        self.MQ7 = self.setValues("MQ7")
        self.MQ8 = self.setValues("MQ8")
        self.MQ9 = self.setValues("MQ9")
        self.MQ135 = self.setValues("MQ135")
        self.MQ137 = self.setValues("MQ137")
        self.nh3_ppm = self.setValues("nh3_ppm")

    def setValues(self, mqSensor = ""):
        valueArray = []
        for i, val in enumerate(self.meas):
            if(self.measnumber > 1 and mqSensor.startswith('MQ')):
                valueArray.append(val[mqSensor]*5/4095 * 3.3/5)
            elif(mqSensor.startswith('MQ')):
                valueArray.append(val[mqSensor]*5/4095)
            elif (self.measnumber > 1 and (mqSensor == 'nh3_ppm')):
                valueArray.append(self.calcNH3ppm(self.MQ137[i]))
            elif mqSensor == 'nh3_ppm':
                valueArray.append(val["nh3_ppm"])
            else:
                valueArray.append(val[mqSensor])
        return self.rrcf(valueArray)
    
    def getMeasnumber(self):
        return self.measnumber

    def getSensorArray(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            Exception(f"measClass has no {name} attribute!")

    def getCorrCoefValues(self, mqArray = ""):
        ArrayToCompare = self.getSensorArray(mqArray)
        if(all(element == ArrayToCompare[0] for element in ArrayToCompare)):
            return 0
        else:
            corrcoeff = np.corrcoef(self.MQ137, ArrayToCompare)
            return corrcoeff[0][1]

    def printCorrCoefValues(self):
        print("# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #")
        print(f"The avegare temperature is: \t{np.average(self.temperature):.2f} °C")
        print(f"The avegage humidity is: \t{np.average(self.humidity):.2f} %")
        for name in mqNames:
            corrcoef = self.getCorrCoefValues(name)
            print(f"The Correlation coefficient of MQ137 and \t{name}  is \t\t{f'{corrcoef:.3f}' if not isinstance(corrcoef, str) else corrcoef}")
        print("# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\n\n")

    def plotMeas(self):
        for name in mqNames: 
            with plt.style.context('bmh'):
                plt.plot(np.array(self.time)/1000, np.array(self.getSensorArray(name)), label= name, marker='.', linestyle='-',)
                plt.title(f'{self.getMeasnumber()}. measurement')
                plt.xlabel("Time (sec)")
                # plt.ylabel("A/D converter's output (bit)")
                plt.ylabel("Sensor output (Voltage)")
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="5", prop = { "size": 7 }, fancybox=True, shadow=True, ncol=1)
            plt.show()

    def calcNH3ppm(self, MQ137):
        RL = SensorRL['MQ137']      #The value of resistor RL is 1K --> measured
        R0 = SensorR0['MQ137']     #The value of resistor R0 is 1K --> measured + calculated
        m  = -0.263    #Enter calculated Slope
        b = 0.42      #Enter calculated intercept

        VRL = MQ137
        Rs = ((Vcc/VRL)-1) * RL
        
        ratio = Rs/R0                           #find ratio Rs/Ro
        ppm = pow(10, ((np.log10(ratio)-b)/m))     #use formula to calculate ppm
        return ppm

    def rrcf(self, data, num_trees=100, shingle_size=1, threshold=2, replacement_strategy='median'):
        n = len(data)
        forest = []

        # Erdő létrehozása
        for _ in range(num_trees):
            tree = RCTree()
            forest.append(tree)

        for i in range(n):
            shingle = data[i:i + shingle_size]

            # A shingle értékeket minden fában beillesztjük
            for tree in forest:
                tree.insert_point(shingle, index=i)

        outliers = set()
        for i in range(n):
            codisp = np.mean([tree.codisp(i) for tree in forest])

            if codisp > threshold:
                outliers.add(i)

        # Kiugró értékek helyettesítése
        if replacement_strategy == 'median':
            replacement_value = np.median(data)
        elif replacement_strategy == 'mean':
            replacement_value = np.mean(data)

        for i in outliers:
            data[i] = replacement_value

        return data

#============================================================================================================#
#=============================================== Evaluations ================================================#

## Create list of measObjects
for measnumber, measDict in enumerate(measDicts):
    measObjects.append(measClass(measDict, measnumber+1))

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
        fig, ax = plt.subplots(nrows=3, ncols=2)
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

def ZscoreFilter(array):    # probably not the best
    # Z-score kiszámítása az adatokhoz
    z_scores = np.abs(stats.zscore(array))

    threshold = 0.005

    # Kiugró értékek kiszűrése
    outliers = np.where(z_scores > threshold)
    
    # Kiugró értékek helyettesítése a kiszűrés előtti és utáni értékek átlagával
    for i in outliers[0]:
        if i > 0 and i < len(array) - 1:
            array[i] = (array[i - 1] + array[i + 1]) / 2
        elif i == 0:
            array[i] = (array[i + 1] + array[i + 2]) / 2
        else:
            array[i] = (array[i - 1] + array[i - 2]) / 2
    return array

def getallNH3ppm():
    allNH3ppm = []
    for meas in measObjects:
        allNH3ppm.extend(meas.getSensorArray("nh3_ppm"))
    return allNH3ppm

def getallRs():
    Vcc = 5
    allRs = {'MQ2': [], 'MQ3': [], 'MQ4': [], 'MQ5': [], 'MQ6': [], 'MQ7': [], 'MQ8': [], 'MQ9': [], 'MQ135': [], 'MQ137': []}
    for meas in measObjects:
        for name in mqNames:
            allRs[name].extend(meas.getSensorArray(name))
    for name in mqNames:
        RL = SensorRL[name]
        print(allRs[name])
        allRs[name] = ((Vcc / np.array(allRs[name]))-1) * RL
    return allRs

def plotMQCharacteristic():
    RsValues = getallRs()
    for name in mqNames: 
        with plt.style.context('bmh'):
            plt.plot(getallNH3ppm(), RsValues[name] / SensorR0[name], label= name, marker='.', linestyle='-',)
            plt.title(f"{name} Sensor\'s characteristic")
            plt.xlabel("PPM")
            plt.ylabel("Rs/R0")
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="5", prop = { "size": 7 }, fancybox=True, shadow=True, ncol=1)
            plt.xscale('log')
        plt.show()

#============================================================================================================#
#=============================================== Call functions =============================================#

printAllCorrCoefValues()

plotAllCorrCoefValues()

plotAllMeasurements()

plotMQCharacteristic()

for meas in measObjects:
    meas.plotMeas()

