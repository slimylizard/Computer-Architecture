"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF0
        self.running = True
        self.PC = 0
        self.FL = 0b00000000
        
    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""
        if len(sys.argv) < 2:
            print("Insufficent arghments")
            print("Usage: filename file_to_open")
            sys.exit()

        address = 0

        try:
            with open(sys.argv[1]) as file:
                for line in file:
                    comment_split = line.split('#')
                    potential_num = comment_split[0]

                    if potential_num == '':
                        continue
                    if potential_num[0] == '1' or potential_num[0] == '0':
                        num = potential_num[:8]
                        self.ram[address] = int(num, 2)
                        address += 1
        except FileNotFoundError:
            print( 'not found')

        # For now, we've just hardcoded a program:

        #program = [
            # From print8.ls8
        #    0b10000010, # LDI R0,8
        #    0b00000000,
        #    0b00001000,
        #    0b01000111, # PRN R0
        #    0b00000000,
        #    0b00000001, # HLT
        #]

        #for instruction in program:
        #    self.ram[address] = instruction
        #    address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            self.FL &= 0b00000000
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL = 0b00000001
            if self.reg[reg_a] < self.reg[reg_b]:
                self.FL = 0b00000100
            if self.reg[reg_a] > self.reg[reg_b]:
                self.FL = 0b00000010

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            #self.fl,
            #self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        HLT = 0b00000001
        LDI = 0b10000010
        PRN = 0b01000111
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001
        ADD = 0b10100000
        CMP = 0b10100111
        JMP = 0b01010100
        JEQ = 0b01010101
        JNE = 0b01010110
        
        while self.running:
            #LDI instruction
            if self.ram[self.PC] == LDI:
                num_to_load = self.ram[self.PC + 2]
                reg_index = self.ram[self.PC + 1]
                self.reg[reg_index] = num_to_load
                self.PC += 3
            #PRN instruction
            elif self.ram[self.PC] == PRN:
                print(self.reg[self.ram[self.PC + 1]])
                self.PC += 2
            #HTL instruction
            elif self.ram[self.PC] == HLT:
                self.running = False
            #ADD instruction
            if self.ram[self.PC] == ADD:
                self.alu('ADD', self.ram[self.PC + 1], self.ram[self.PC + 2])
                self.PC += 3
            #MUL instruction
            if self.ram[self.PC] == MUL:
                first_factor = self.reg[self.ram[self.PC + 1]]
                second_factor = self.reg[self.ram[self.PC + 2]]
                product = first_factor * second_factor
                print(product)
                self.PC += 3
            #CMP instruction
            if self.ram[self.PC] == CMP:
                self.alu('CMP', self.ram[self.PC + 1], self.ram[self.PC + 2])
                self.PC += 3
            #JMP instruction
            if self.ram[self.PC] == JMP:
                self.PC = self.reg[self.ram[self.PC + 1]]
            #JEQ instruction
            if self.ram[self.PC] == JEQ:
                if self.FL & 1 is 1:
                    self.PC = self.reg[self.ram[self.PC + 1]]
                else:
                    self.PC += 2
            #JNE instruction
            if self.ram[self.PC] == JNE:
                if self.FL & 1 is 0:
                    self.PC = self.reg[self.ram[self.PC + 1]]
                else:
                    self.PC += 2
            #PUSH instruction
            if self.ram[self.PC] == PUSH:
                self.reg[7] -= 1
                num_to_push = self.reg[self.ram[self.PC + 1]]
                SP = self.reg[7]
                self.ram[SP] = num_to_push
                self.PC += 2
            #POP instruction
            if self.ram[self.PC] == POP:
                SP = self.reg[7]
                num_to_pop = self.ram[SP]
                self.reg[self.ram[self.PC + 1]] = num_to_pop
                self.reg[7] += 1
                self.PC += 2
            #CALL instruction
            if self.ram[self.PC] == CALL:
                self.reg[7] -= 1
                SP = self.reg[7]
                addr_next_instruction = self.PC + 2
                self.ram[SP] = addr_next_instruction
                self.PC = self.reg[self.ram[self.PC + 1]]
            #RET instruction
            if self.ram[self.PC] == RET:
                SP = self.reg[7]
                self.PC = self.ram[SP]
                self.reg[7] += 1
