"""CPU functionality."""

import sys


filename = sys.argv[1]

# CPU class - def load - load a program into memory
# Load - address = 0  ---> program counter, index of the current instruction
#     - program = array of bytes ---> MEMORY , RAM  -->   inside there's instructions

# Register Immediate: Saves value at specified register
LDI = 0b10000010
# Print the value at specified register
PRN = 0b01000111
# Halt
HLT = 0b00000001
# Add
ADD = 0b10100000
# Multiply
MUL = 0b10100010
# Compare
CMP = 0b10100111
# Push
PUSH = 0b01000101
# Pop
POP = 0b01000110
# Store
ST = 0b10000100
# Call a subroutine
CALL = 0b01010000
# Return
RET = 0b00010001
# Jump, jump to address
JMP = 0b01010100
# Jump if equal flag is true
JEQ = 0b01010101
# Jump if not equal
JNE = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.register = [0] * 8  # 8 general-purpose register
        self.ram = [0] * 256  # 256 bytes of memory
        self.pc = 0  # internal register counter
        self.FL = [0, 0, 0, 0, 0, 0, 0, 0]  # special purpose register
        self.SP = 7
        self.register[7] = 0xF4
        self.branchtable = {
            # load functions into branchtable
            LDI: self.LDI,
            PRN: self.PRN,
            ADD: self.ADD,
            MUL: self.MUL,
            PUSH: self.PUSH,
            POP: self.POP,
            CALL: self.CALL,
            RET: self.RET,
            CMP: self.CMP,
            JEQ: self.JEQ,
            JNE: self.JNE,
            JMP: self.JMP,
            HLT: self.HLT,
        }

    def load(self):
        """Load a program into memory."""

        if (len(sys.argv)) != 2:
            print("remember to pass the second file name")
            print("usage: python3 fileio.py <second_file_name.py>")
            sys.exit()

        address = 0
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    # parse the file to isolate the binary opcodes
                    possible_number = line[:line.find('#')]
                    if possible_number == '':
                        continue  # skip to next iteration of loop
                    instruction = int(possible_number, 2)
                    self.ram[address] = instruction
                    address += 1
        except FileNotFoundError:
            print(f'Error from {sys.argv[0]}: {sys.argv[1]} not found')
            sys.exit()

        # For now, we've just hardcoded a program:

        ''' program = [
            # From print8.ls8
            0b10000010,  # LDI in R0 save 8  
            0b00000000,  #R0                 
            0b00001000,  #8
            0b01000111,  # PRN R0
            0b00000000,  #R0
            0b00000001,  # HLT
        ]
        for instruction in program:
            self.ram[address] = instruction
            address += 1 '''

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        #self.FL = [0,0,0,0,0,"L","G","E"]
        #self.FL = [0,0,0,0,0,0,0,0]
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == CMP:
            # print("in alu")
            if self.register[reg_a] == self.register[reg_b]:
                # print("EqUAL", self.register[reg_a], self.register[reg_b])
                # set the Equal `E` flag to 1
                self.FL[-1] = 1
                # print("FLAG REG", self.FL)
                # print("(FL -1)", self.FL[-1])
            elif self.register[reg_a] < self.register[reg_b]:
                print(self.register[reg_a], "LESS THAN", self.register[reg_b])
                self.FL[-3] = 1
                # print("FLAG REG", self.FL)
                # print("FL -3", self.FL[-3])
            elif self.register[reg_a] > self.register[reg_b]:
                # print(self.register[reg_a],
                #       "GREATER THAN", self.register[reg_b])
                self.FL[-2] = 1
                # print("FLAG REG", self.FL)
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, address):
        value = self.ram[address]
        return value

    def ram_write(self, value, address):
        self.ram[address] = value

    def LDI(self):
        # print("LDI")
        reg_num = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.register[reg_num] = value
        self.pc += 3  # 3byte instruction
        # print("registers", self.register)

    def PRN(self):
        reg_num = self.ram_read(self.pc + 1)
        print(self.register[reg_num])
        self.pc += 2  # 2byte instruction

    def ADD(self):
        reg_num1 = self.ram[self.pc + 1]
        reg_num2 = self.ram[self.pc + 2]
        self.register[reg_num1] += self.register[reg_num2]
        self.pc += 3

    def MUL(self):
        reg_num1 = self.ram[self.pc + 1]
        reg_num2 = self.ram[self.pc + 2]
        self.register[reg_num1] *= self.register[reg_num2]
        self.pc += 3

    def PUSH(self):  # Push the value in the given register on the stack.
        # decrement sp
        self.register[self.SP] -= 1
        # get the value we want to store from the register
        reg_num = self.ram[self.pc + 1]
        # value is in register ith that number
        value = self.register[reg_num]
        # register 7 points to that address
        top_address = self.register[self.SP]
        # find it in ram and store the value there
        self.ram[top_address] = value
        # increment pc to next instruction
        self.pc += 2

    def POP(self):
        # find out the address of top of stack -- register[SP] points to ir
        top_address = self.register[self.SP]
        # the value is the number in ram at that address
        value = self.ram[top_address]
        # what's the register in the instruction
        reg_num = self.ram[self.pc + 1]
        # put the value in that register
        self.register[reg_num] = value
        # increment sp
        self.register[7] += 1
        # increment pc to next instruction
        self.pc += 2

    def CALL(self):  # contains a register operand
        # that register contains the address we want to jump to, address of a function
        # since CALL instruction takes two bytes to execute we want to access self.ram(pc + 2)
        return_address = self.pc + 2  # we're going to return here after
        # push it to the stack
        # decrement SP
        self.register[self.SP] -= 1
        # check what's the top address:
        top_address = self.register[self.SP]
        # find it in RAM and store the return_address there
        self.ram[top_address] = return_address
        # get the register number from pc+1
        reg_num = self.ram[self.pc + 1]
        # the address it's whatever is stored in that register number
        subroutine_address = self.register[reg_num]
        # call it
        self.pc = subroutine_address

    def RET(self):
        # get the value from top of stack
        top_address = self.register[self.SP]
        value = self.ram[top_address]
        self.pc = value

    def CMP(self):  # takes 2 operands
        # compare the values in the two registers
        # print("CMP")
        reg_num1 = self.ram[self.pc + 1]
        reg_num2 = self.ram[self.pc + 2]
        self.alu(CMP, reg_num1, reg_num2)
        self.pc += 3

    def JEQ(self):  # one operand
        # if the `equal` flag is set to TRUE (1), jump to the address stored in the given register
        if self.FL[-1] == 1:
            # print("JEqq")
            reg_num = self.ram[self.pc + 1]
            # print("regnum, ", reg_num)
            address = self.register[reg_num]
            # print("address in", reg_num, "is----", address)
            # print("self.pc is before", self.pc)
            self.pc = address
            # print("self.pc is now", self.pc)
        else:
            # print("NOT JEQ")
            # print("self.pc is before", self.pc)
            self.pc += 2
            # print("self.pc is now", self.pc)

    def JNE(self):
        # if the `equal` flag is set to False (0), jump to the address stored in the given register
        #self.FL = [0,0,0,0,0,"L","G","E"]
        if self.FL[-1] == 0:
            # print("JNE")
            reg_num = self.ram[self.pc + 1]
            # print("regnum, ", reg_num)
            address = self.register[reg_num]
            # print("address in", reg_num, "is----", address)
            # print("self.pc is before", self.pc)
            self.pc = address
            # print("self.pc is now", self.pc)
        else:
            # print("NOT JNE")
            # print("self.pc is before", self.pc)
            self.pc += 2
            # print("self.pc is now", self.pc)

    def JMP(self):
        # print("JMP")
        # jump to the address stored in the given register
        reg_num = self.ram[self.pc + 1]
        # print("regnum, ", reg_num)
        address = self.register[reg_num]
        # print("address in", reg_num, "is----", address)
        # set pc to the address stored in the register
        # print("self.pc is before", self.pc)
        self.pc = address
        # print("self.pc is now", self.pc)

    def HLT(self):
        # print("RAM is ", self.ram[:35])
        running = False
        sys.exit(0)

    def run(self):
        running = True

        while running:
            ir = self.ram_read(self.pc)
            # print("IR is,", ir)
            if ir in self.branchtable:
                self.branchtable[ir]()

            else:
                print((f'Unknown instruction: {ir}, at address PC: {self.pc}'))
                sys.exit(1)
