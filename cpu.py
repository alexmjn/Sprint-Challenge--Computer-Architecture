"""CPU functionality."""

import sys

ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
DIV = 0b10100011
MOD = 0b10100100

CMP = 0b10100111 #00000aaa 00000bbb

JMP = 0b01010100 #00000rrr
JEQ = 0b01010101 #00000rrr
JNE = 0b01010110 #00000rrr

AND = 0b10101000 #bitwise AND, store in reg a
OR = 0b10101010
XOR = 0b10101011
NOT = 0b01101001 # bitwise NOT;
SHL = 0b10101100 # bitwise left shift of reg a by operand b
SHR = 0b10101101 # bitwise right shift of reg a by operand b

INC = 0b01100101
DEC = 0b01100110

CALL = 0b01010000
RET = 0b00010001

NOP = 0b00000000
HLT = 0b00000001 # halt, exit emulator
LDI = 0b10000010 # load "immediate", store a value, set a register to a value

PRN = 0b01000111
PUSH = 0b01000101
POP = 0b01000110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.pc = 0 #program counter
        self.sp = self.reg[7]
        self.mar = None # memory access register
        self.mdr = None # memory register
        self.IR = None # instruction register
        self.FL = [0] * 8 # internal register to flag comparisons
        self.branch_table = {
            HLT: self.hlt,
            LDI: self.ldi,
            PRN: self.prn,
            POP: self.pop,
            PUSH: self.push,
            ADD: self.add,
            SUB: self.sub,
            MUL: self.mul,
            DIV: self.div,
            CALL: self.call,
            RET: self.ret,
            JMP: self.jmp,
            CMP: self.comp,
            JEQ: self.jeq,
            JNE: self.jne,
            MOD: self.mod,
            AND: self.bitwiseand,
            OR: self.bitwiseor,
            XOR: self.bitwisexor,
            NOT: self.bitwisenot,
            SHL: self.shl,
            SHR: self.shr
        }

    def hlt(self):
        sys.exit()

    def ldi(self, op_a, op_b):
        self.reg[op_a] = op_b

    def prn(self, op_a):
        print(self.reg[op_a])

    def push(self, reg_num):
        self.reg[7] -= 1
        value = self.reg[reg_num]
        sp = self.reg[7]
        self.ram[sp] = value

    def pop(self, reg_num):
        sp = self.reg[7]
        value = self.ram[sp]
        self.reg[reg_num] = value
        self.reg[7] += 1

    def add(self, op_a, op_b):
        self.reg[op_a] += self.reg[op_b]

    def sub(self, op_a, op_b):
        self.reg[op_a] -= self.reg[op_b]

    def mul(self, op_a, op_b):
        self.reg[op_a] *= self.reg[op_b]

    def div(self, op_a, op_b):
        self.reg[op_a] /= self.reg[op_b]

    def mod(self, op_a, op_b):
        self.reg[op_a] %= self.reg[op_b]

    def call(self, reg_num):
        address = self.reg[reg_num]
        return_address = self.pc + 2
        self.reg[7] -= 1
        sp = self.reg[7]
        self.ram[sp] = return_address
        self.pc = address

    def ret(self):
        sp = self.reg[7]
        return_address = self.ram[sp]
        self.reg[7] += 1
        self.pc = return_address

    def comp(self, reg_a, reg_b):
        """Compares two registers' values and sets the equality flag"""
        self.FL = [0] * 8
        if self.reg[reg_a] == self.reg[reg_b]:
            self.FL[-1] = 1
        elif self.reg[reg_a] > self.reg[reg_b]:
            self.FL[-2] = 1
        else:
            self.FL[-3] = 1

    def jmp(self, reg_num):
        """Moves to a specific spot in the program counter."""
        self.pc = self.reg[reg_num]
        # offsets run()'s autoincrement after the command is performed
        self.pc -= 2

    def jeq(self, reg_num):
        if self.FL[-1] == 1:
            self.jmp(reg_num)

    def jne(self, reg_num):
        if self.FL[-1] != 1:
            self.jmp(reg_num)

    def bitwiseand(self, reg_a, reg_b):
        self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]

    def bitwiseor(self, reg_a, reg_b):
        self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]

    def bitwisexor(self, reg_a, reg_b):
        self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]

    def bitwisenot(self, reg_a):
        self.reg[reg_a] = ~self.reg[reg_a]

    def shl(self, reg_a, operand_b):
        self.reg[reg_a] = self.reg[reg_a] << operand_b
        if len(bin(self.reg[reg_a])) > 10:
            self.reg[reg_a] = list(bin(self.reg[reg_a]))[-8:]

    def shr(self, reg_a, operand_b):
        self.reg[reg_a] = self.reg[reg_a] >> (operand_b)

    def ram_write(self, address, value):
        self.ram[address] = value

    def ram_read(self, address):
        try:
            return self.ram[address]
        except KeyError:
            print("Invalid Register")
            return None

    def load(self):
        """Load a program into memory."""
        basePath = './examples/'
        file = 'call.ls8'
        if len(sys.argv) > 1:
            file = sys.argv[1]
        address = 0

        with open(basePath + file, 'r') as f:
            for line in f:
                line = line.split("#")

                try:
                    instruction = int(line[0], 2)
                except ValueError:
                    continue

                self.ram[address] = instruction
                address += 1




    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU.
        reads memory address and stores result in IR
        """
        self.IR = self.ram_read(self.pc)
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)

        while self.IR != HLT:
            num_arguments = ((self.IR & 0b11000000) >> 6)

            if num_arguments == 0:
                self.branch_table[self.IR]

            elif num_arguments == 1:
                self.branch_table[self.IR](operand_a)

            else:
                self.branch_table[self.IR](operand_a, operand_b)

            self.pc += (num_arguments + 1)
            self.IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
