#include "Beomote.h"
#include "Common.h"

int irPin = 10;



void setup() {
  Serial.begin(115200);
  
  Beo.initialize(irPin);
}

void loop() {
  BeoCommand cmd;
  
  if (Beo.receive(cmd)) {
    String str = "";
    str += pad(String(cmd.link, HEX));
    str += pad(String(cmd.address, HEX));
    str += pad(String(cmd.command, HEX));
    
    if (str.length() > 0) {
      Serial.print(str + '\n');
    }
  }
}
