#include "myEEPROM.h"

EEPROM_28C256 myEEPROM;

int char_to_HEX(char digit){
  int value = int(digit);
  if(value >= 48 && value <= 57) return value - '0';
  else if(value >= 65 && value <= 70) return 10 + value - 'A';
  else return -1;  
}

long parse_HEX_field(String field){
  
  if(field.indexOf("0x") != -1){
    field.remove(0, field.indexOf("0x")+2);
  }
  field.toUpperCase();
  
  long value = 0;
  for(int i=0; i<field.length(); i++){
    if(field[i] == ' ') continue;
    value *= 0x10;        
    value += char_to_HEX(field[i]); 
  }

  return value;
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(20);
}

void loop() {

  if(Serial.available()){

    char operation = Serial.read();

    if(operation == 'W' || operation == 'R'){

      String command = Serial.readString();

      int beginning = command.indexOf(",");
      int finish = command.indexOf(",", beginning+1);
      String field = command.substring(beginning+1, finish);
      long ADDR = parse_HEX_field(field);

      beginning = finish;
      finish = command.indexOf(",", beginning+1);
      field = command.substring(beginning+1, finish);
      int CHUNK_SIZE = parse_HEX_field(field);

      if(operation == 'R'){
        for(int i=0; i<CHUNK_SIZE; i++){
          if(i!=0) Serial.print(", ");
          Serial.print(myEEPROM.read(ADDR+i), HEX);
        }
        Serial.println();
      }
      else{
        beginning = finish;
        for(int i=0; i<CHUNK_SIZE; i++){
          finish = command.indexOf(",", beginning+1);
          field = command.substring(beginning+1, finish);
          byte DATA = parse_HEX_field(field);
          myEEPROM.write(ADDR+i, DATA);
          beginning = finish;
          delay(3);               // Should not be required but it ensure reliable writing
        }
        Serial.println("OE");
      }
    }
  }
}
