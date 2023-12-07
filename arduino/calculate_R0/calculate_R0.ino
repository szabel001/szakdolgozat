//mux control pins
#define s0  26
#define s1  25
#define s2  33
#define s3  32

//mux "SIG" pin (input for esp)
#define SIG 34

//mux EN input --> enable mux
#define EN 12

char *mqNames[10] ={"MQ2", "MQ3", "MQ4", "MQ5", "MQ6", "MQ7",  "MQ8", "MQ9", "MQ135", "MQ137"};
float Rl[10] = {2, 10, 15, 1, 20, 1, 1, 1, 1, 1}; //Define variable for R0

//Code to Calculate R0 
void setup() {
  Serial.begin(9600); //Baud rate 

  digitalWrite(EN, LOW);  //switch on enable pin

  pinMode(s0, OUTPUT);
  pinMode(s1, OUTPUT);
  pinMode(s2, OUTPUT);
  pinMode(s3, OUTPUT);

  //set up starting value 
  digitalWrite(s0, LOW);
  digitalWrite(s1, LOW);
  digitalWrite(s2, LOW);
  digitalWrite(s3, LOW);
}
 
void loop() { 
  for(int i = 0; i < 10;  i++)  {
    float sensor_volt;
    float RS_air;
    float R0;
    float sensorValue;
    for(int x = 0 ; x < 1000 ; x++)
    {
      sensorValue = sensorValue + mux_16(i);
      delay(1);
    }
    sensorValue = sensorValue/1000.0;
    sensor_volt = sensorValue*(3.3/4096.0);
    R0 = ((5/sensor_volt)-1)*Rl[i];

    Serial.print(mqNames[i]);
    Serial.print(" R0 = ");
    Serial.println(R0);
  }
  delay(1000);
   Serial.println("\n");
}



float mux_16(int channel){
  int controlPin[] = {s0, s1, s2, s3};

  int muxChannel[16][4] = {
    {0,0,0,0}, //channel 0
    {1,0,0,0}, //channel 1
    {0,1,0,0}, //channel 2
    {1,1,0,0}, //channel 3
    {0,0,1,0}, //channel 4
    {1,0,1,0}, //channel 5
    {0,1,1,0}, //channel 6
    {1,1,1,0}, //channel 7
    {0,0,0,1}, //channel 8
    {1,0,0,1}, //channel 9
    {0,1,0,1}, //channel 10
    {1,1,0,1}, //channel 11
    {0,0,1,1}, //channel 12
    {1,0,1,1}, //channel 13
    {0,1,1,1}, //channel 14
    {1,1,1,1}  //channel 15
  };

  for(int i = 0; i < 4; i++){
    digitalWrite(controlPin[i], muxChannel[channel][i]);
  }

  int value = analogRead(SIG);
  return value;
  }