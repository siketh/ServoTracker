#include <Servo.h> 

#define LED 13

Servo myservo;  // create servo object to control a servo 
                // a maximum of eight servo objects can be created 
 
int pos = 0;    // variable to store the servo position 
 
void setup() 
{ 
  pinMode(LED, OUTPUT);
  
  Serial.begin(9600);
  Serial.println("Ready");
  
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object 
} 
 
 
void loop() 
{ 
  if(Serial.available()){
    pos = Serial.parseInt();
    Serial.println(pos);
    if((pos > 180)|(pos < 0)){
      pos = 90; 
      Serial.println(pos);
    }
  }

//  myservo.write(int(pos)*10);
}
