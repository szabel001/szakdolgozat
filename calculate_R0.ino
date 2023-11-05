//mux control pins
#define s0  26
#define s1  25
#define s2  33
#define s3  32

//mux "SIG" pin (input for esp)
#define SIG 34

//mux EN input --> enable mux
#define EN 12

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
  
  float sensor_volt; //Define variable for sensor voltage 
  float RS_air; //Define variable for sensor resistance
  float R0; //Define variable for R0
  float Rl = 1; //Define variable for R0
  float sensorValue; //Define variable for analog readings 
  for(int x = 0 ; x < 500 ; x++) //Start for loop 
  {
    sensorValue = sensorValue + mux_16(9); //Add analog values of sensor 500 times 
  }
  sensorValue = sensorValue/500.0; //Take average of readings
  sensor_volt = sensorValue*(5/4096.0); //Convert average to voltage 
  RS_air = ((5*Rl)/sensor_volt)-Rl; //Calculate RS in fresh air 
  R0 = RS_air/3.6; //Calculate R0 
 
  Serial.print("R0 = "); //Display "R0"
  Serial.println(R0); //Display value of R0 
  delay(1000); //Wait 1 second 
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