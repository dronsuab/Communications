#include <ESP8266WiFi.h>
#include <PubSubClient.h> 


#define SERIAL_SPEED 9600
#define STATIC_IP_OPTION 0
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
  digitalWrite(LED_BUILTIN, LOW);
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
    Serial.println("connected");
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
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  if(String(topic) == "PIN"){
    Serial.print("Equal");
    pinMode(5, OUTPUT);
    digitalWrite(5, HIGH);
  }
  
  // Switch on the LED if an 1 was received as first character
  if ((char)payload[0] == '1') {
    digitalWrite(BUILTIN_LED, LOW);   // Turn the LED on (Note that LOW is the voltage level
    // but actually the LED is on; this is because
    // it is acive low on the ESP-01)
  } else {
    digitalWrite(BUILTIN_LED, HIGH);  // Turn the LED off by making the voltage HIGH
  }

}
void reconnect(){
  while(!client.connected()){
    Serial.println("Reconnecting");
    String clientId = "ESP8266Client";
    clientId += String(random(0xffff),HEX);

   if(client.connect(clientId.c_str())){
    Serial.println("Connected");
    client.publish("outTopic", "helloWorld");
    client.subscribe("inTopic");
    client.subscribe("PIN");
   }
   else{
    Serial.print("failed, rc = ");
    Serial.println(client.state());
    Serial.println("Try again in 5 seconds...");
    delay(5000);
   }
  }
}
void setup() {
  // put your setup code here, to run once:
   int connectionStatus=0;
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);

  Serial.println("Serial Aviable");
  connectionStatus = ConnectWifi (STATIC_IP_OPTION);
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
  if(!client.connected()){
     reconnect();
  }
  client.loop();
}
