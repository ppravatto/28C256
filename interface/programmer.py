import serial, time, os, glob, readline
from serial.serialutil import SerialException
from tqdm import tqdm

def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]

readline.set_completer_delims(' \t\n;')
readline.parse_and_bind('tab: complete')
readline.set_completer(complete)


CONNECTION_DELAY = 2
MAX_CHUNK_SIZE = 256

def Error(message, remove=True):
    print("")
    print("\u001b[31mERROR\u001b[0m: {}".format(message))
    print("")
    if remove == True:
        dummy = input("Please remove chip and press ENTER ...")
    exit()

class EEPROM_programmer():
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, timeout=4):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

    def check_address(self, address):
        if address < 0 or address > 0x7fff:
            Error("Invalid address ({})".format(hex(address)))
    
    def check_data(self, data):
        if data < 0 or data > 0xff:
            Error("Invalid data ({})".format(hex(data)))
    
    def check_chunk_size(self, size):
        if size < 0 or size > MAX_CHUNK_SIZE:
            Error("Invalid chunk size ({})".format(size))
    
    def open(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(CONNECTION_DELAY)
        except SerialException:
            Error("Failure in opening serial port {}".format(self.port), remove=False)
    
    def close(self):
        self.serial.close()

    def read_chunk(self, address, size):
        self.check_address(address)
        self.check_chunk_size(size)
        self.serial.write(bytes("R, {}, {}".format(hex(address), hex(size)), 'UTF-8'))
        line = str(self.serial.read_until())[2:-5]
        sline = line.split(',')
        data = [int(val, 16) for val in sline]
        return data
    
    def read_from_address(self, address):
        return self.read_chunk(address, 1)

    
    def write_chunk(self, address, size, data):
        self.check_address(address)
        self.check_chunk_size(size)
        if len(data) != size:
            Error("Mismatch between size of data vector ({}) and chunk size ({})".format(len(data), size))
        for element in data:
            self.check_data(element)
            string = "W, {}, {}".format(hex(address), hex(size))
            for i in range(size):
                string += ", {}".format(hex(data[i]))
        self.serial.write(bytes(string, 'UTF-8'))
        line = str(self.serial.read_until())[2:-5]
        if line != "OE":
            Error("Unexpected writing operation termination")
    
    def write_to_address(self, address, value):
        self.write_chunk(address, 1, [value])
    
    def fill(self, value):
        self.check_data(value)
        print("")
        data = [value for i in range(MAX_CHUNK_SIZE)]
        for chunk in tqdm(range(int(0x8000/MAX_CHUNK_SIZE)), desc="Writing memory"):
            address = MAX_CHUNK_SIZE*chunk
            self.write_chunk(address, MAX_CHUNK_SIZE, data)
        time.sleep(2)
        for chunk in tqdm(range(int(0x8000/MAX_CHUNK_SIZE)), desc="Verifying data"):
            address = MAX_CHUNK_SIZE*chunk
            found = self.read_chunk(address, MAX_CHUNK_SIZE)
            if found != data:
                Error("Incorrect data encountered in chunk starting with address {}".format(hex(address)))
        print("")
        print("\u001b[32mSUCCESS\u001b[0m")

    def memory_dump(self):          
        dump = []
        for chunk in range(int(0x8000/0x10)):
            address = 0x10*chunk
            data = self.read_chunk(address, 0x10)
            dumpline = " ".join([str(hex(val)) for val in data])
            print("{} | {}".format(hex(address), dumpline)) 
            for val in data:
                dump.append(int(val))
        return bytearray(dump)
        
    

if __name__ == "__main__":

    os.system('cls' if os.name == 'nt' else 'clear')
    port = input("Please select serial port (default: /dev/ttyUSB0): ")
    port = "/dev/ttyUSB0" if port=="" else port
    
    programmer = EEPROM_programmer(port=port)
    programmer.open()

    os.system('cls' if os.name == 'nt' else 'clear')
    dummy = input("Please insert chip and press ENTER...")
    
    while True:
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Modes of operation:")
            print("  (1) Memory dump")
            print("  (2) Read from address")
            print("  (3) Write to address")
            print("  (4) Program from binary file")
            print("  (5) Fill memory with byte")
            print("")
            mode = input("Select the operation code (default: 1): ")
            try:
                mode = int(mode)
            except:
                pass
            else:
                if mode>0 and mode<6:
                    break
        
        os.system('cls' if os.name == 'nt' else 'clear')

        if mode == "" or mode == 1:
            dump = programmer.memory_dump()
            filename = input("\nSelect a name for the output binary file (default: not save): ")
            if filename != "":
                with open(filename, 'wb') as dumpfile:
                    dumpfile.write(dump)

        elif mode == 2:
            print("Reading from single address")
            address = input("  Select address (hex value): ")
            address = int(address, 16)
            byte = programmer.read_from_address(address)[0]
            print("")
            print("Address: {}, Data: {}".format(hex(address), hex(byte)))
            

        elif mode == 3:
            print("Writing to single address")
            address = input("  Select address (hex value): ")
            address = int(address, 16)
            data = input("  Select byte value to write (hex value): ")
            data = int(data, 16)
            programmer.write_to_address(address, data)

        elif mode == 4:
            print("Writing binary file to memory")
            filename = input("  Select path to source binary file: ")
            
            if os.path.isfile(filename) == True:
                data = []
                with open(filename, "rb") as file:
                    while True:
                        byte = file.read(1)
                        if not byte:
                            break
                        else:
                            value = int.from_bytes(byte, 'big')
                            data.append(value)

                reminder = len(data)%MAX_CHUNK_SIZE
                complete_chunks = int((len(data)-reminder)/MAX_CHUNK_SIZE)

                chunks = []
                for i in range(complete_chunks):
                    chunk = data[i*MAX_CHUNK_SIZE, (i+1)*MAX_CHUNK_SIZE]
                    chunks.append(chunk)
                if reminder != 0:
                    chunks.append(data[-reminder::])

                address = 0
                for i in tqdm(range(len(chunks)), desc="Writing memory"):
                    chunk = chunks[i]
                    programmer.write_chunk(address, len(chunk), chunk)
                    address += len(chunk)
                
                time.sleep(2)
                address = 0
                for i in tqdm(range(len(chunks)), desc="Verifying data"):
                    size = len(chunks[i])
                    found = programmer.read_chunk(address, size)
                    if(found != chunks[i]):
                        print("***************************")
                        print(found)
                        print(chunks[i])
                        Error("Incorrect data encountered in chunk starting with address {}".format(hex(address))) 
                    address += size

                print("")
                print("\u001b[32mSUCCESS\u001b[0m")

            else:
                Error("'{}' file not found".format(filename))          
        
        elif mode == 5:
            print("Filling memory with single byte value")
            data = input("  Select byte value to write (hex value): ")
            data = int(data, 16)
            programmer.fill(data)

        print("")
        choice = input("Do you want to perform another operation (y/n)? ")
        if choice.upper() == "Y":
            pass
        else:
            break

    print("")
    dummy = input("Please remove chip and press ENTER ...")
    programmer.close()

    exit()

