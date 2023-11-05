#include <Arduino.h>
#include <Adafruit_AHTX0.h>

#include <SD.h>

//--------------------------------------------------------------------
//------------------------ Settings-----------------------------------
//--------------------------------------------------------------------
char ssid[] = "ssid"; //  Change this to your network SSID (name).
char pass[] = "ssid1234";    // Change this your network password

//------ MQTT broker settings and topics
const char* mqtt_server = "mqtt3.thingspeak.com";

//-- published settings
const char* publishTopic1 ="channels/2149993/publish";   //REPLACE THE NUMBER 114938 WITH YOUR channel ID  
const char* publishTopic2 ="channels/2149994/publish";   //REPLACE THE NUMBER 114938 WITH YOUR channel ID  

//-- subscribed settings Virtuino command 1   
const char* subscribeTopicFor_Command_1="channels/2149993/subscribe/fields/field1";   //REPLACE THE NUMBER 114938 WITH YOUR channel ID  
//const char* subscribeTopicFor_Command_2="channels/2149994/subscribe/fields/field2";   //REPLACE THE NUMBER 114938 WITH YOUR channel ID  

const unsigned long postingInterval = 5L * 1000L; // Post data every 5 seconds.

 
#define PIN_SPI_CS 5 // The ESP32 pin GPIO5
//SD_card's file
File measFile;
//------------------------ Variables-----------------------------------
//-------------------------------------------------------------------------
#ifdef ESP8266
 #include <ESP8266WiFi.h>  
 #else
 #include <WiFi.h>  
#endif
 
#include <PubSubClient.h>
#include <WiFiClient.h>
WiFiClient espClient;
PubSubClient client(espClient);  // Download the library PubSubClient from the arduino library manager

unsigned long lastUploadedTime = 0;

//call constructor for aht
Adafruit_AHTX0 aht;

//mux control pins
#define s0  12
#define s1  14
#define s2  27
#define s3  26

//mux "SIG" pin (input for esp)
#define SIG_pin 34

//mux EN input --> enable mux
#define EN 25
char *mq_sensors[10] = {"MQ2", "MQ3", "MQ4", "MQ5", "MQ6", "MQ7", "MQ8", "MQ9", "MQ135", "MQ137 (NH3)"};
float mq_data[10];
String dataText1;
String dataText2;

void  setup(){
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

  //set up SD card
  if (!SD.begin(PIN_SPI_CS)) {
    Serial.println(F("SD CARD FAILED, OR NOT PRESENT!"));
  }
  else {
  Serial.println(F("SD CARD INITIALIZED."));

  if (!SD.exists("meas.txt")) {
    Serial.println(F("meas.txt doesn't exist. Creating meas.txt file..."));
    // create a new file by opening a new file and immediately close it
    measFile = SD.open("meas.txt", FILE_WRITE);
    measFile.close();
  }

  // recheck if file is created or not
  if (SD.exists("meas.txt"))
    Serial.println(F("meas.txt exists on SD Card."));
  else
    Serial.println(F("meas.txt doesn't exist on SD Card."));
  }

  //enable mux's output
  digitalWrite(EN, LOW);

   if (! aht.begin()) {
    Serial.println("Could not find AHT? Check wiring");
    while (1) delay(10);
  }
  Serial.println("AHT10 or AHT20 found");

  Serial.begin(115200);

  // while (!Serial) delay(1);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop(){
  dataText1 = "";
  dataText2 = "";
  sensors_event_t humidity, temp;
  aht.getEvent(&humidity, &temp);// populate temp and humidity objects with fresh data
  Serial.print("Temperature: "); Serial.print(temp.temperature); Serial.println(" degrees C");
  Serial.print("Humidity: "); Serial.print(humidity.relative_humidity); Serial.println("% rH");
  
  float val[10] = {0};

  if (measFile) {
    measFile = SD.open("meas.txt", FILE_WRITE);
    measFile.print(millis());
    measFile.print(" ");
    measFile.println("");
          
    measFile.print("Temperature: "); Serial.print(temp.temperature); Serial.println(" degrees C");
    measFile.print("Humidity: "); Serial.print(humidity.relative_humidity); Serial.println("% rH");
  }

  for(int i = 0; i< 10; i++){
      val[i] = mux_16(i);
      Serial.print("Value of ");
      Serial.print(mq_sensors[i]);
      Serial.print(" is:\t");
      Serial.println(val[i]);
    if(measFile) {
      measFile.println(mq_sensors[i]);
      measFile.print("\t");
      measFile.print(val[i]);
      measFile.println("");
    }
    dataText1 += String("&field" + String(i+1) + "=" + String(val[i]));
    if(i>7)
      dataText2 += String("&field" + String(i-7) + "=" + String(val[i]));
    if(i==9){
      dataText2 += String("&field3=" + String(temp.temperature));
      dataText2 += String("&field4=" + String(humidity.relative_humidity));
    }
  }

    publishMessage(publishTopic1,dataText1,true);
    publishMessage(publishTopic2,dataText2,true);
 
  for(int i = 0; i < 20; i++)
      Serial.print("# # ");
  delay(1000);
  //measFile.close();
  Serial.println("");

  if (!client.connected()) reconnect();
  client.loop();
}