# 28C256 EEPROM Programmer
This repository describes a simple open-source programmer for the [28C256](http://ww1.microchip.com/downloads/en/DeviceDoc/doc0006.pdf) 32kB EEPROM memory.

The device has been thought as an affordable tool to aid the hobbyist in the development of small 8-bit computer projects (e.g. 6502 or Z80 processors based computers).

The programmer can be controlled directly via the Arduino serial port. A `python3` code is provided as a terminal-based interface.

#### Disclamers
This repository and all its content are provided "as is" without any kind of warranty. Any use of the software and hardware described and contained in this project is at your own risk. The authors cannot be held liable for any damage or harm deriving directly or indirectly from the use, direct or indirect, of what is contained in this repository.


## Hardware description
The project is based around the [ATmega328P](https://ww1.microchip.com/downloads/en/DeviceDoc/ATmega48A-PA-88A-PA-168A-PA-328-P-DS-DS40002061B.pdf) 8-bit microcontroller contained in an Arduino Nano board.

The 8 I/O EEPROM pins are directly driven by the Arduino digital pins in the range from `D5` to `D12`. The 15 EEPROM address lines are driven through the use of two [74HC595](https://www.ti.com/lit/ds/symlink/sn74hc595.pdf?ts=1647597704824&ref_url=https%253A%252F%252Fwww.google.com%252F) 8-bit shift registers organized in a cascade configuration. The analog pins of the Arduino board (`A0` to `A5`) are used to operate both the control pins of the EEPROM (WE, RE, OE) and the data and clock lines of the shift registers.

The electronic schematic, available as a `.pdf` file in the `hardware` folder, is the following:

![alt text](https://github.com/ppravatto/28C256/blob/main/hardware/Schematic.png)

The Gerber files for the PCB, designed using the EasyEDA software, are also available in the `hardware` folder.

### Components
The components required to build the programmer are the following:
* 1x Arduino Nano board
* 1x 28-Pin ZIF socket (or regular socket)
* 2x SN74HC595 Shift Registers (16-Pin DIP package)
* 3x 100nF MLCC 0805 SMD capacitors (6.3V or higher)

The Arduino board can be soldered directly onto the PCB using the integrated pin headers but I would suggest the use of 2.54mm pitch pin header connectors.

TIP: In order to avoid unwanted short circuits while operating the board I would suggest mounting it in a non-conductive enclosure (keep in mind that the screw holes are plated and connected to the GND) or to use rubber feet to lift the board from the work surface.

## Software
The programmer is designed to interface with the computer via USB. A serial connection with a baud rate of 115200 is set as the default.

The Arduino code is provided in the `firmware` folder and can be loaded directly to the Nano board using the [Arduino IDE](https://www.arduino.cc/en/software) or, alternatively, directly using the [Arduino CLI](https://github.com/arduino/arduino-cli). Once flashed with the firmware, the board is completely stand-alone and will listen to the serial port awaiting instructions. These can be provided manually by the user using the serial monitor of the Arduino IDE or, more conveniently, using the `python3` program provided in the `interface` folder.

### Serial commands
The programmer accepts two types of serial commands that directly encode a read/write operation of a memory chunk. The default maximum chunk is set to 256 bytes. All the command fields must be provided in `HEX` format. The firmware is not case sensitive and automatically strips the encoding format (e.g. the inputs `0xEA`, `0xea`, `EA`, `ea` should be equivalent).

To read a chunk of `SIZE` bytes of memory starting from the address `ADDR` the following command must be used:
```
R, ADDR, SIZE
```

To write a chunk of `SIZE` bytes to the memory starting from the address `ADDR` the following command must be used:
```
W, ADDR, SIZE, <DATA>
```
where `<DATA>` represents a list of comma-separated bytes of length `SIZE`. When the writing operation has been completed the programmer returns the `OE` (operation ended) message on the serial port.

### Command-line interface
The programmer can be controlled through a `python3` script that automatically implements some base features. To run the script the following requirements must be satisfied:

* `python3` interpreter (3.8.12)
* [`pyserial` library](https://pythonhosted.org/pyserial/) (3.5)
* [`tqdm` library](https://tqdm.github.io/) (4.62.3)

Please notice how the version indicated between brackets represents the version used during development and do not represent a strict requirement, other version may work as well.

#### How to use the interface
After connecting the programmer to the computer via USB, **without any EEPROM in the socket**, the program interface can be started running the command:
```
python3 programmer.py
```
If the connection is established successfully the program will invite you to insert the EEPROM in the socket and press enter.

Once this operation is completed the desired operation can be selected using the provided menu. At the moment the following operations are implemented:

* `Memory dump`: prints on screen the content of the whole memory in lines of 16 bytes encoded in `HEX` format.
* `Read from address`: read the byte value located at a given address
* `Write to address`: write a byte to a given address
* `Program from binary file`: set the EEPROM content using a binary file
* `Fill memory with byte`: set all the addresses to the same byte value

Once the desired operations have been completed the interface will ask you to remove the EEPROM chip and press enter. This will close the serial connection and terminate the program.

During all the operations the autocomplete function can be invoked using the `TAB` key.



