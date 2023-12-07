#include <Arduino.h>
#include <Adafruit_AHTX0.h>

#include <PubSubClient.h>
#include <WiFi.h>  

#include <SD.h>

#define PIN_SPI_CS 13 // The ESP32 pin GPIO13

//call constructor for aht
Adafruit_AHTX0 aht;

//mux control pins
#define s0  26
#define s1  25
#define s2  33
#define s3  32

//mux "SIG" pin (input for esp)
#define SIG 34

//mux EN input --> enable mux
#define EN 12
char *mq_sensors[10] = {"MQ2", "MQ3", "MQ4", "MQ5", "MQ6", "MQ7", "MQ8", "MQ9", "MQ135", "MQ137"};
float mq_data[10];
String dataText1;
String dataText2;
String measString;

String fileName;

float ppm;

// Replace the next variables with your SSID/Password combination
const char* ssid = "ssid";
const char* password = "ssid1234";

// Add your MQTT Broker IP address, example:
const char* mqtt_server = "192.168.137.1";

// MQTT Broker
const char *topic = "esp32/";
const char *mqtt_username = "";
const char *mqtt_password = "";
const int mqtt_port = 1883;

WiFiClient espClient;

PubSubClient client(espClient);

long lastMsg = 0;
long lastStart = 0;
char msg[50];
int value = 0;
String messageTemp = "off";

uint8_t qos = 2;

void setup(){
  Serial.begin(9600);
  setup_wifi();

  /*--------------------------------MUX---------------------------------------*/
  pinMode(s0, OUTPUT);
  pinMode(s1, OUTPUT);
  pinMode(s2, OUTPUT);
  pinMode(s3, OUTPUT);
  pinMode(EN, OUTPUT);
  pinMode(SIG, INPUT);


  //set up starting value 
  digitalWrite(s0, LOW);
  digitalWrite(s1, LOW);
  digitalWrite(s2, LOW);
  digitalWrite(s3, LOW);

  //enable mux's output
  digitalWrite(EN, LOW);
  /*--------------------------------ENDOF MUX---------------------------------------*/

  /*--------------------------------AHT SENSOR---------------------------------------*/
  if (! aht.begin()) {
    Serial.println("Could not find AHT? Check wiring");
    while (1); // stop the program
  }
  else { 
    Serial.println("AHT10 or AHT20 found");
  }
  /*--------------------------------ENDOF AHT SENSOR---------------------------------------*/

/*-----------------------------------------SD CARD ----------------------------------------*/
  SPI.begin(14, 2, 15, 13);

  if (!SD.begin(PIN_SPI_CS)) {
    Serial.println(F("SD CARD FAILED, OR NOT PRESENT!"));
    while (1); // stop the program
  }

  Serial.println(F("SD CARD INITIALIZED."));
  /*--------------------------------ENDOF SD CARD---------------------------------------*/

  /*--------------------------------MQTT connect---------------------------------------*/
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  while (!client.connected()) {
    String client_id = "esp32";
    Serial.printf("\nThe client %s connects to the MQTT broker\n", client_id.c_str());
    if (client.connect(client_id.c_str()), "", qos, 2, "") {
        client.subscribe("esp32/measSwitch");
        Serial.println("MQTT broker connected");
    } else {
        Serial.println("failed with state ");
        Serial.print(client.state());
        delay(2000);
    }
  }
  /*--------------------------------ENDOF MQTT---------------------------------------*/
}

void loop(){
  long now = millis();
  dataText1 = "";
  dataText2 = "";

  if (now - lastMsg > 1000) {
    lastMsg = now;

    if(WiFi.status() != WL_CONNECTED) {
      setup_wifi();
    }
    else if (!client.connected()) {
      reconnect();
    }

    client.loop();

    if (messageTemp == "on") {

      if (!SD.exists(fileName.c_str())) {
        Serial.println("SD card error!");
        while(1);
      }

      for(int i = 0; i < 10; i++) {
          mq_data[i] = mux_16(i);
      }

      sensors_event_t humidity, temp;
      aht.getEvent(&humidity, &temp);// populate temp and humidity objects with fresh data

      Serial.print("Temperature: "); Serial.print(temp.temperature); Serial.println(" degrees C");
      Serial.print("Humidity: "); Serial.print(humidity.relative_humidity); Serial.println("% rH");

      char tempString[8];
      dtostrf(temp.temperature, 1, 2, tempString);
      client.publish("esp32/temperature", tempString);

      char humidityString[8];
      dtostrf(humidity.relative_humidity, 1, 2, humidityString);
      client.publish("esp32/humidity", humidityString);

      for(int i = 0; i < 10; i++){
        Serial.print("Value of ");
        Serial.print(mq_sensors[i]);
        Serial.print(" is:\t");
        Serial.println(mq_data[i]);

        char valueString[8];
        dtostrf(mq_data[i], 1, 2, valueString);
        String topic = "esp32/";
        topic.concat(mq_sensors[i]);
        char char_array[topic.length() + 1];
        topic.toCharArray(char_array, topic.length() + 1);

        client.publish(char_array, valueString);

        if(mq_sensors[i] == "MQ137"){
          ppm = calculate_ppm(mq_data[i]);
          Serial.printf("Value of NH3 in ppm : %f", ppm);
          char valuePPM[8];
          dtostrf(ppm, 1, 2, valuePPM);
          client.publish("esp32/nh3_ppm", valuePPM);
        }
      }
      long time = millis() - lastStart;
      measString = 
      String("\n{\"time\":")         + time +
      String(",\n\"temperature\":")  + temp.temperature +
      String(",\n\"humidity\":")     + humidity.relative_humidity +
      String(",\n\"nh3_ppm\":")    + ppm +
      String(",\n\"MQ2\":")          + mq_data[0] +
      String(",\n\"MQ3\":")          + mq_data[1] +
      String(",\n\"MQ4\":")          + mq_data[2] +
      String(",\n\"MQ5\":")          + mq_data[3] +
      String(",\n\"MQ6\":")          + mq_data[4] +
      String(",\n\"MQ7\":")          + mq_data[5] +
      String(",\n\"MQ8\":")          + mq_data[6] +
      String(",\n\"MQ9\":")          + mq_data[7] +
      String(",\n\"MQ135\":")        + mq_data[8] +
      String(",\n\"MQ137\":")        + mq_data[9] +
      String("},\n");

      appendFile(SD, fileName.c_str(), measString.c_str());
    }
  }
}