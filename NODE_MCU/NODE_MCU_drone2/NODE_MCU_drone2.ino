#include <ESP8266WiFi.h>
#include <PubSubClient.h> 

#define SERIAL_SPEED 115200
#define STATIC_IP_OPTION 0
#define N_ToSubs 4

char* WIFI_NAME = "Marc"; 
char* PASSWORD = "nicedaytoday";

char* mqtt_server = "172.20.10.2";
String myself = "drone2";
String mycontroller = "controller2";
String myteam = "red";
String ToSubs[] = {"GOVER","DEAD","LED","CFIRE"};


IPAddress staticIP(192,168,1,113);
IPAddress gateway(192,168,1,1);
IPAddress subnet(255,255,255,0);

WiFiClient espClient;
PubSubClient client(espClient);

bool ConnectWifi(bool staticIP){
  bool success = 0;
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_NAME, PASSWORD);
  //Serial.println("Connecting");
  while(WiFi.status() != WL_CONNECTED){
    digitalWrite(LED_BUILTIN, HIGH);
    delay(1000);
    digitalWrite(LED_BUILTIN, LOW);
    delay(1000);
  }
  if(staticIP){
    WiFi.config(staticIP,gateway,subnet); 
    //Serial.println("STATIC IP SET");
  }
  Serial.println("");
  Serial.print("Connected to: ");
  Serial.println(WIFI_NAME);
  Serial.print("IP ADDRESS: ");
  Serial.println(WiFi.localIP());
  if(WiFi.status() == WL_CONNECTED){
    digitalWrite(LED_BUILTIN, HIGH);
    //Serial.println("connected to WiFi");
    success = 1;
  }
  else{
    //Serial.println("Disonnected");
    digitalWrite(LED_BUILTIN, LOW);
    success = 0;
  }
  return success;
}
void callback(char* topic, byte* payload, unsigned int length){
  String Spayload, Stopic(topic);
  int pos;
  for (int i = 0; i < length; i++) {
    Spayload += (char)payload[i];
  }
  pos = Spayload.indexOf(',');
  
  if(Stopic == "LED"){
    //<TOPIC,DRON(MYSELF),LIFES>
    String sub = Spayload.substring(pos+1);
    int pos2 = sub.indexOf(',');
    String dest = sub.substring(0,pos2);
    if(dest == myself){
      Spayload += '/';
      Serial.print(Spayload);
    }
  }
  else if(Stopic == "CFIRE"){
    String sub = Spayload.substring(pos+1);
    int pos2 = sub.indexOf(',');
    String dest = sub.substring(0,pos2);
    if(dest == mycontroller){
      Spayload += ',';
      Spayload += myself;
      Spayload += '/';
      Serial.print(Spayload);
    }
  }
  else if(Stopic == "DEAD"){
    //<TOPIC,CONTROLLER,DRON(MYSELF)>
    String sub = Spayload.substring(pos+1);
    int pos2 = sub.indexOf(',');
    String dest = sub.substring(pos2+1);
    if(dest == myself){
      Spayload += '/';
      Serial.print(Spayload);
    }
  }
  else if(Stopic == "GOVER"){
    //<TOPIC>
    Spayload += '/';
    Serial.print(Spayload);
  }
}
void reconnect(){
  while(!client.connected()){
    //Serial.println("Reconnecting to broker");
   if(client.connect(myself.c_str())){
    //Serial.println("Connected to broker");
    int i = 0;
    bool done = 0;
    while(!done){
      for(i = 0; i<N_ToSubs; i++){
        done = client.subscribe(ToSubs[i].c_str());
      }
    }
   }
   else{
    /*Serial.print("failed, rc = ");
    Serial.println(client.state());
    Serial.println("Try again in 5 seconds...");*/
    delay(2000);
   }
  }
}
void checkUart(){
  if(Serial.available() > 0){
    int pos = 0;
    String sending, Stopic, aux = "";
    while(aux.indexOf("/") == -1 ){
      if(Serial.available() > 0){
        aux = Serial.readString();
        sending += aux;
      }
    }
    sending.remove(sending.length()-1);
    //parsing serial input
    pos = sending.indexOf(',');
    Stopic = sending.substring(0,pos);
    
    bool pcheck = client.publish(Stopic.c_str(), sending.c_str());
    if(!pcheck){
      //Serial.println("Err sending msg");
      reconnect();
      client.publish(Stopic.c_str(), sending.c_str());
    }
  }
}
void setup() {
  // put your setup code here, to run once:
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(SERIAL_SPEED);
  Serial.setTimeout(5);
  int connectionStatus = ConnectWifi(STATIC_IP_OPTION);
  if(connectionStatus == 1){
    digitalWrite(LED_BUILTIN, HIGH);
  }
  else{
    digitalWrite(LED_BUILTIN, LOW);
  }
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  client.connect(myself.c_str());
  String msg = myself;
  msg += ',';
  msg += myteam;
  msg += ',';
  msg += mycontroller;
  client.publish("WantToPlay",msg.c_str());
  int i = 0;
  for(i = 0; i<N_ToSubs; i++){
    client.subscribe(ToSubs[i].c_str());
  }
}
void loop() {
  // put your main code here, to run repeatedly:
  client.loop();
    if(!client.connected()){
     reconnect();
  }
  checkUart();
  
}
