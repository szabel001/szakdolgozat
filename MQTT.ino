//==========================================
void setup_wifi() {
  delay(10);
  Serial.print("\nConnecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  randomSeed(micros());
  Serial.println("\nWiFi connected\nIP address: ");
  Serial.println(WiFi.localIP());
}

//=====================================
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
      //client.connect("cliend ID", "username","password") Replace with your Thingspeak MQTT Device Credentials
    if (client.connect("CDYXFRQOPAAsGSo5HxQVCDk", "CDYXFRQOPAAsGSo5HxQVCDk","GxRERDT928Qv9tBhDwuLymMZ")) {  
      Serial.println("connected");
      client.subscribe(subscribeTopicFor_Command_1);   // subscribe the topics here
      //client.subscribe(command2_topic);   
      
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");   // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

//========================================= messageReceived
void messageReceived(String &topic, String &payload) {
 Serial.println("incoming: " + topic + " - " + payload);
 
  //-- check for Virtuino Command 1
  if (topic==subscribeTopicFor_Command_1){
        Serial.println("Command 1 = "+payload);
        int v = payload.toInt();
        if (v>0) digitalWrite(2,HIGH);
        else digitalWrite(2,LOW);
   }

  /*//-- check for Virtuino Command 1
  if (topic==subscribeTopicFor_Command_2){
        Serial.println("Command 2 = "+payload);
   }
   */
}

//=======================================  
// This void is called every time we have a message from the broker

void callback(char* topic, byte* payload, unsigned int length) {
  String incommingMessage = "";
  for (int i = 0; i < length; i++) incommingMessage+=(char)payload[i];
  
  Serial.println("Message arrived ["+String(topic)+"]"+incommingMessage);
  
  //--- check the incomming message
    if( strcmp(topic,subscribeTopicFor_Command_1) == 0){
     if (incommingMessage.equals("1")) digitalWrite(2, LOW);   // Turn the LED on 
     else digitalWrite(2, HIGH);  // Turn the LED off 
  }
}



//======================================= publising as string
void publishMessage(const char* topic, String payload , boolean retained){
  if (client.publish(topic, payload.c_str()))
      Serial.println("Message publised ["+String(topic)+"]: "+payload);
}
