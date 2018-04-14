#include <ESP8266WiFi.h>
#include <PubSubClient.h> 

#define SERIAL_SPEED 9600
#define STATIC_IP_OPTION 0
#define BUFF_SIZE 30
/*char* WIFI_NAME = "TP-LINK_267304";
char* PASSWORD = "84551542";*/

//char* WIFI_NAME = "MOVISTAR_29B4";
//char* PASSWORD = "keyG6QjfecD7TfpCtDbh";

char* WIFI_NAME = "Marc";
char* PASSWORD = "nicedaytoday";

char* mqtt_server = "172.20.10.2";

IPAddress staticIP(192,168,1,113);
IPAddress gateway(192,168,1,1);
IPAddress subnet(255,255,255,0);

WiFiClient espClient;
PubSubClient client(espClient);

bool ConnectWifi(bool staticIP){
  bool success = 0;
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_NAME, PASSWORD);
  Serial.println("Connecting");
  while(WiFi.status() != WL_CONNECTED){
    digitalWrite(LED_BUILTIN, HIGH);
    delay(1000);
    digitalWrite(LED_BUILTIN, LOW);
    delay(1000);
  }
  if(staticIP){
    WiFi.config(staticIP,gateway,subnet); 
    Serial.println("STATIC IP SET");
  }
  Serial.println("");
  Serial.print("Connected to: ");
  Serial.println(WIFI_NAME);
  Serial.print("IP ADDRESS: ");
  Serial.println(WiFi.localIP());
  if(WiFi.status() == WL_CONNECTED){
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.println("connected to WiFi");
    success = 1;
  }
  else{
    Serial.println("Disonnected");
    digitalWrite(LED_BUILTIN, LOW);
    success = 0;
  }
  return success;
}
void callback(char* topic, byte* payload, unsigned int length){
  /*Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");*/
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
}
void reconnect(){
  while(!client.connected()){
    Serial.println("Reconnecting to broker");
    String clientId = "ESP8266ClientTEST";
    //clientId += String(random(0xffff),HEX);

   if(client.connect(clientId.c_str())){
    Serial.println("Connected to broker");
    client.publish("outTopic", "helloWorld");
    client.subscribe("inTopic");
   }
   else{
    Serial.print("failed, rc = ");
    Serial.println(client.state());
    Serial.println("Try again in 5 seconds...");
    delay(5000);
   }
  }
}
void checkUart(){
  if(Serial.available() > 0){
    char msg[BUFF_SIZE];
    char topic[BUFF_SIZE];
    int pos = 0;
    String sending, Stopic, aux = "";
    while(aux.indexOf('/') == -1 ){
      if(Serial.available() > 0){
        aux = Serial.readString();
        sending += aux;
      }
    }
    //parsing serial input
    pos = sending.indexOf(',');
    Stopic = sending.substring(0,pos);
    Serial.println(Stopic);
    Serial.println(sending);
    
    
    sending.toCharArray(msg, BUFF_SIZE);
    Stopic.toCharArray(topic, BUFF_SIZE);
    bool pcheck = client.publish(topic, msg);
    if(pcheck){
      Serial.println("msg sent");
    }
    else{
      Serial.println("Err sending msg");
      reconnect();
      client.publish(topic, msg);
      
    }
  }
}
void setup() {
  // put your setup code here, to run once:
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(SERIAL_SPEED);
  int connectionStatus = ConnectWifi(STATIC_IP_OPTION);
  if(connectionStatus == 1){
    digitalWrite(LED_BUILTIN, HIGH);
  }
  else{
    digitalWrite(LED_BUILTIN, LOW);
  }
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  // put your main code here, to run repeatedly:
  client.loop();
    if(!client.connected()){
     reconnect();
  }
  checkUart();
  
}
