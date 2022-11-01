#define RED 11
#define GREEN 10
#define BLUE 9

#define MAX_WAIT 2000

unsigned long last_time;
bool active = false;   // if app on pc is active
int red, green, blue;

void setup()
{
  pinMode(RED, OUTPUT);
  pinMode(GREEN, OUTPUT);
  pinMode(BLUE, OUTPUT);
  Serial.begin(9600);
  last_time = millis();
}

void loop() {
    if (active && millis() - last_time > MAX_WAIT) {
        active = false;
        // turn off
        for (int i=100; i>=0; i--) {
          analogWrite(RED, red*i/100);
          analogWrite(GREEN, red*i/100);
          analogWrite(BLUE, red*i/100);
          delay(15);
        }
    }            
    while (Serial.available() > 0) {
        if (Serial.read() == 'a') {
            red = Serial.read();
            green = Serial.read();
            blue = Serial.read();
            
            if (!active) {
                // turn on
                for (int i=0; i<=100; i++) {
                    analogWrite(RED, red*i/100);
                    analogWrite(GREEN, red*i/100);
                    analogWrite(BLUE, red*i/100);
                    delay(15);
                }
                active = true;
            } else {
              analogWrite(RED, red);
              analogWrite(GREEN, green);
              analogWrite(BLUE, blue);
            }
            last_time = millis();
        }
    }
} 

// void loop()
// {
//   while (Serial.available()  0) {
//     if (Serial.read() == 'a') {
//       analogWrite(RED, Serial.read());
//       analogWrite(GREEN, Serial.read());
//       analogWrite(BLUE, Serial.read());
//     }  
//   }  
// }