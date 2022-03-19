//Set ADDRESS shift register pins
const int ORCLK = A0;       // Output register clock
const int SRCLK = A1;       // Shift register clock
const int SRD = A2;         // Data line

//Set EEPROM control pins (active low)
const int OE = A3;          // Output enable
const int CE = A4;          // Chip enable
const int WE = A5;          // Write enable

//Set EEPROM I/O connections
const int IOROM[8] = {5, 6, 7, 8, 9, 10, 11, 12};

//Set maximum dimension of the EEPROM
const int MAX_ADDR = 32767;

class EEPROM_28C256{
  private:
    bool io_output;
    void set_io_output(bool pin_status);
    void set_address(long address);
  public:
      EEPROM_28C256();
      byte read(long address);
      void write(long address, byte data);  
};

void EEPROM_28C256::set_io_output(bool pin_status){
  if(pin_status == true){
    for(int i=0; i<8; i++) pinMode(IOROM[i], OUTPUT);
    io_output = true;
  }
  else{
    for(int i=0; i<8; i++) pinMode(IOROM[i], INPUT);
    io_output = false;
  }
}

void EEPROM_28C256::set_address(long address){
  byte low = address % 0x0100;
  byte high = (address-low) / 0x0100;
  digitalWrite(ORCLK, LOW);
  shiftOut(SRD, SRCLK, MSBFIRST, high);
  shiftOut(SRD, SRCLK, MSBFIRST, low);
  digitalWrite(ORCLK, HIGH);    
}

EEPROM_28C256::EEPROM_28C256(){
  pinMode(SRD, OUTPUT);
  pinMode(SRCLK, OUTPUT);
  pinMode(ORCLK, OUTPUT);
  pinMode(WE, OUTPUT);
  pinMode(OE, OUTPUT);
  pinMode(CE, OUTPUT);
  set_io_output(false);
  
  digitalWrite(OE, HIGH);
  digitalWrite(WE, HIGH);
  digitalWrite(CE, HIGH);
}

byte EEPROM_28C256::read(long address){
  
  if(io_output == true) set_io_output(false);
  
  set_address(address);
  
  digitalWrite(CE, LOW);
  digitalWrite(OE, LOW);
  delayMicroseconds(2);

  byte value = 0;
  for(int i=7; i>=0; i--){
    value *= 2;
    value += (digitalRead(IOROM[i]) == HIGH)? 1 : 0;
  }

  digitalWrite(CE, HIGH);
  digitalWrite(OE, HIGH);
  delayMicroseconds(1);

  return value;
}

void EEPROM_28C256::write(long address, byte data){

  if(io_output == false) set_io_output(true);
  
  digitalWrite(OE, HIGH);
  delayMicroseconds(1);
  
  set_address(address);
  delayMicroseconds(1);
  
  digitalWrite(CE, LOW);
  delayMicroseconds(1);
  
  digitalWrite(WE, LOW);
  delayMicroseconds(1);

  byte current = data;
  for(int i=0; i<8; i++){
    byte rem = current % 2;
    current = (current-rem)/2;
    if(rem == 0) digitalWrite(IOROM[i], LOW);
    else digitalWrite(IOROM[i], HIGH);
  }
  delayMicroseconds(5);

  digitalWrite(WE, HIGH);
  delayMicroseconds(1);
  
  digitalWrite(CE, HIGH);
  delayMicroseconds(1);
  
  digitalWrite(OE, LOW);
  delayMicroseconds(1);
  
}
