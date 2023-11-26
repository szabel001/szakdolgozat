from importing_modules import *

mqNames = ['MQ2', 'MQ3', 'MQ4', 'MQ5', 'MQ6', 'MQ7', 'MQ8', 'MQ9', 'MQ135', 'MQ137']
SensorR0 = {'MQ2': 9.49, 'MQ3': 10.33, 'MQ4': 3735, 'MQ5': 499, 'MQ6': 568.24, 'MQ7': 28.41, 'MQ8': 6.46, 'MQ9': 61.5, 'MQ135': 499, 'MQ137': 6} 
SensorRL = {'MQ2': 2, 'MQ3': 10, 'MQ4': 15, 'MQ5': 1, 'MQ6': 20, 'MQ7': 1, 'MQ8': 1, 'MQ9': 1, 'MQ135': 1, 'MQ137': 1,}

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

    def setValues(self, mqSensor = ""):
        valueArray = []
        for val in self.meas:
            if mqSensor.startswith('MQ'):
                valueArray.append(val[mqSensor]*3.3/4095)
            elif mqSensor == 'nh3_ppm':
                ppm = self.calcNH3ppm(val['MQ137'])
                valueArray.append(ppm)
            elif mqSensor == 'time':
                valueArray.append(val[mqSensor]-self.meas[0]['time'])
            else:
                valueArray.append(val[mqSensor])
        return valueArray
    
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
                plt.scatter(np.array(self.time)/1000, np.array(self.getSensorArray(name)), label= name, marker='.', linestyle='-',)
                plt.title(f'{self.getMeasnumber()}. measurement')
                plt.xlabel("Time (sec)")
                # plt.ylabel("A/D converter's output (bit)")
                plt.ylabel("Sensor output (Voltage)")
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize="5", fancybox=True, shadow=True, ncol=1)
            plt.show()

    def calcNH3ppm(self, MQ137):
        RL = SensorRL['MQ137']      #The value of resistor RL is 1K --> measured
        R0 = SensorR0['MQ137']     #The value of resistor R0 is 1K --> measured + calculated
        m = -0.276    #Enter calculated Slope
        b = -0.224     #Enter calculated intercept
        Vcc = 5
        VRL = MQ137 * 3.3 / 4095
        RS = ((Vcc/VRL)-1) * RL
        ratio = RS/R0                           #find ratio Rs/Ro
        ppm = pow(10, ((np.log10(ratio)-b)/m))     #use formula to calculate ppm
        return ppm
    
    @staticmethod
    def ZscoreFilter(array):    # probably not the best
        # Z-score kiszámítása az adatokhoz
        z_scores = np.abs(stats.zscore(array))

        threshold = 2

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