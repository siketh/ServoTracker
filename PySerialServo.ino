#include <Servo.h> 

#define LED 13

Servo myservoX;  // create servo object to control a servo 
Servo myservoY;                // a maximum of eight servo objects can be created 
 
int posX = 0;    // variable to store the servo position 
int posY = 0;
 
void setup() 
{ 
  pinMode(LED, OUTPUT);
  
  Serial.begin(115200);
  Serial.println("Ready");
  
  myservoX.attach(9);  // attaches the servo on pin 9 to the servo object 
  myservoY.attach(3);
  myservoX.write(90);
  myservoY.write(70);
} 
 
 
void loop() 
{ 
    if(Serial.available()){
    posX = Serial.parseInt();
    Serial.println(posX);
    posY = Serial.parseInt();
    Serial.println(posY);
    
    myservoX.write(posX);
    myservoY.write(posY);
    
    
  }

//  myservoX.write(int(pos)*10);
}
