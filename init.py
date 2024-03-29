from importModules import *
#============================================================================================================#
#============================================ Initialize variable ===========================================#

Vcc = 5
source = ""

files = []              # to collect all opened files
files_mqtt = []
measDicts = []          # to collect all json from files
measDicts_mqtt = []
measObjects = []        # to collect all object created from jsons
corrcoefDict = {}       # to collect all corrcoef value from all measurements

mqNames = ['MQ2', 'MQ3', 'MQ4', 'MQ5', 'MQ6', 'MQ7', 'MQ8', 'MQ9', 'MQ135', 'MQ137']
mqColors = {'MQ2': 'red', 'MQ3': 'pink', 'MQ4': 'orange', 'MQ5': 'grey', 'MQ6': 'blue', 'MQ7': 'green', 'MQ8': 'purple', 'MQ9': 'darkblue', 'MQ135': 'yellow', 'MQ137': 'black'}
SensorR0 = {'MQ2': 25.17, 'MQ3': 26.08, 'MQ4': 3735, 'MQ5': 499, 'MQ6': 568.24, 'MQ7': 28.41, 'MQ8': 10.66, 'MQ9': 61.5, 'MQ135': 499, 'MQ137': 12.95} 
SensorRL = {'MQ2': 2, 'MQ3': 10, 'MQ4': 15, 'MQ5': 1, 'MQ6': 20, 'MQ7': 1, 'MQ8': 1, 'MQ9': 1, 'MQ135': 1, 'MQ137': 1,}

#============================================================================================================#
#=============================================== Set source =================================================#

while source != "SD" and source != "MQTT":
    source = input("Adja meg a kívánt forrást! (MQTT / SD):").upper().strip()
    if(source != "SD" and source != "MQTT"):
        print("Nem megfelelően adta meg a forrás nevét! Próbálja újra! (SD / MQTT)")

#============================================================================================================#
#=============================================== Import files (sd card) =====================================#

if source == 'SD':
    path = '.\meresek\sd\\'
    arr = os.listdir(path)
    arr.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    for txtName in arr:
        files.append(open(path+txtName, 'r'))
    for file in files:
        measDicts.append(ast.literal_eval(file.read()))

#============================================================================================================#
#=============================================== Import files (mqtt) ========================================#

if source == 'MQTT':
    path = '.\meresek\mqtt\\'
    arr = os.listdir(path)
    arr.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    for txtName in arr:
        files.append(open(path+txtName, 'r'))

    for file in files:
        lines = file.readlines()
        measList = []
        temp = {}
        for data in lines:
            line = ast.literal_eval(data)
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
#=============================================== Create measClass============================================#

class MeasClass:
    def __init__(self, meas = [], measnumber = None):
        self.meas = meas
        self.measnumber = measnumber
        self.time = self.setValues("time")
        self.temperature = self.setValues("temperature")
        self.humidity = self.setValues("humidity")
        self.nh3_ppm = self.setValues("nh3_ppm")
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

    def setValues(self, mqName = ""):
        valueArray = []
        for val in self.meas:
            if mqName.startswith('MQ'):
                mq_voltage = val[mqName]*3.3/4095
                if mq_voltage < 0.1 or mq_voltage > 3:
                    mq_voltage = 0.01
                valueArray.append(mq_voltage)
            elif mqName == 'nh3_ppm':
                ppm = self.calcNH3ppm(val['MQ137'])
                valueArray.append(ppm)
            elif mqName == 'time':
                valueArray.append((val[mqName]-self.meas[0]['time'])/1000)
            else:
                valueArray.append(val[mqName])
        return np.array(valueArray)

    def getMeasnumber(self):
        return self.measnumber

    def getSensorArray(self, mqName):
        if hasattr(self, mqName):
            return getattr(self, mqName)
        else:
            Exception(f"measClass has no {mqName} attribute!")

    def getCorrCoefValues(self, mqName = ""):
        ArrayToCompare = self.getSensorArray(mqName)
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
                plt.scatter(np.array(self.time)/1000, np.array(self.getSensorArray(name)), label= name, marker='.', linestyle='-',)
                plt.scatter(np.array(self.time)/1000, np.array(self.getSensorArray('nh3_ppm'))/1000, label= name, marker='.', linestyle='-',)
                plt.title(f'{self.getMeasnumber()}. measurement')
                plt.xlabel("Time (sec)")
                # plt.ylabel("A/D converter's output (bit)")
                plt.ylabel("Sensor output (Voltage)")
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="5", fancybox=True, shadow=True, ncol=1)
            plt.show()

    def calcNH3ppm(self, MQ137):
        RL = SensorRL['MQ137']      #The value of resistor RL is 1K --> measured
        R0 = SensorR0['MQ137']     #The value of resistor R0 is 1K --> measured + calculated
        m = -0.2701    #Enter calculated Slope
        b = -0.2276    #Enter calculated intercept
        Vcc = 5
        VRL = MQ137 * 3.3 / 4095
        RS = ((Vcc/VRL)-1) * RL
        ratio = RS/R0                           #find ratio Rs/Ro
        ppm = 10 ** ((np.log10(ratio)-b)/m)     #use formula to calculate ppm
        return ppm
    
## Create list of measObjects
for measnumber, measDict in enumerate(measDicts):
    measObjects.append(MeasClass(measDict, measnumber+1))