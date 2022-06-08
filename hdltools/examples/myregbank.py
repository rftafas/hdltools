#################################################################################
# Copyright 2020 Ricardo F Tafas Jr

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.
#################################################################################
import sys
import os
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import hdltools

#This is one example for a register bank to serve as base for learning purposes.
#It is not related to any core, block or neither it have any meaning. Just a
#bunch of loose registers.

# first we declare a register bank.
# It is a 32 bit register with 8 possible positions.
# we named the architecture "RTL". Remember, VHDL is case insensitive so careful with naming.
myregbank = hdltools.RegisterBank("myregbank", "rtl", 32, 8)

# this is an axample of a read only register for ID, Golden number, or other inputs
# we add a position (address) and name it.
# myregbank.add(REG_ADDRESS,"golden")
myregbank.add(0, "golden")
# This golden number should be 32bit, it must start at 0. We have to name the segment, in
# this case, we will use 'G1'. It is not important here, but imagine multisegmented register...
# myregbank.reg[REG_ADDRESS].add(NAME,TYPE,START BIT POSITION,SIZE)
myregbank.reg[0].add("g1", "ReadOnly", 0, 32)
# This is an example for a read/write generic register. Pretty standard.
myregbank.add(1, "ReadWrite1")
myregbank.reg[1].add("rw1", "ReadWrite", 0, 32)
# this is an example for a read/write generic register with external clear.
myregbank.add(2, "ReadWrite2")
myregbank.reg[2].add("rw2", "ReadWrite", 0, 32)
myregbank.reg[2].externalClear = True
# this is an example of a write to clear register. Meaning it captures a '1' and stays that way until cleared
# by writing '1' to it.
myregbank.add(3, "WriteToClear")
myregbank.reg[3].add("w2c1", "Write2Clear", 0, 32)
# wee can use just a slice on any type. Lets create a slice. This is why we have REGISTER_NAME
# and also some SEGMENT_NAME. In this case, we will have 2 16bit register (high and low).
# for whatever reason, we may want it pulsed.
# Slices can be of any type.
myregbank.add(4, "SlicedReg")
myregbank.reg[4].add("pulse1", "Write2Pulse", 0, 16)
myregbank.reg[4].add("pulse2", "Write2Pulse", 16, 16)
# And we can create a very mixed register:
myregbank.add(5, "MixedRegister")
# Bit 0 is goint to be a pulsed register. Write one, it pulses output.
# for this example, we want to kill the pulse generation with external signal.
myregbank.reg[5].add("pulse3", "Write2Pulse", 0, 1)
myregbank.reg[5][0].externalClear = True
# bit 1 is a write to clear. but besides the writeto clear, we also want an external source to clear its content.
myregbank.reg[5].add("w2c2", "Write2Clear", 1, 1)
myregbank.reg[5][1].externalClear = True
# bit 2 is a readonly to wich I can force a 0 value to be read. Why? Pointless but possible.
myregbank.reg[5].add("ro1", "ReadOnly", 2, 1)
myregbank.reg[5][2].externalClear = True
#We used bits 0-1-2 but we are going to jump to bit 8 and forward. It's possible to skip unused bits and keep them
#'reserved for future use'. Probably the synthesis tool will eliminate uneeded associated logic.
#just to fill re rest of the register:
myregbank.reg[5].add("div1", "Write2Clear", 8, 8)
myregbank.reg[5].add("div2", "ReadWrite", 16, 8)
myregbank.reg[5].add("div3", "ReadOnly", 24, 8)
# We will jump register 6 on purpose. Probably the synthesis tool will remove any logic
# related to it. So we don't need to follow all possible registers.
# And we can track read action on a register. the minimal amount of possible tracking for reading is byte.
# Byte 0 is readonly. Reading it generates a pulse. Writing to it creates no action.
myregbank.add(7, "ActionTest")
# Action is detected per register and on each byte of a register. This means:
# This is a register wise signal, meaning all parts of this register enjoy the same signal source and distinction is more
# for better understanding of signal relations. Treating individual bits is made externally with edge detectors and logic.
# All register types can work with write and read actions. Even ReadOnly will detect a write attempt if activitySignal
# is true.
myregbank.reg[7].add("read_only_action", "ReadOnly", 0, 8)
myregbank.reg[7][0].activitySignal = True
myregbank.reg[7].add("read_write_action", "ReadWrite", 8, 8)
myregbank.reg[7][8].activitySignal = True
myregbank.reg[7].add("split_rw_action", "SplitReadWrite", 16, 8)
myregbank.reg[7][16].activitySignal = True
myregbank.reg[7].add("wr2clr_action", "Write2Clear", 24, 8)
myregbank.reg[7][24].activitySignal = True

try:
    if "-r" in sys.argv[1]:
        myregbank.SetPortAsRecord()
except:
    print("----------------------------------------------------------------")
    print("To generate this example with a record output, add \"-r\".")

print("----------------------------------------------------------------")
print("Outputs:")
print("HDL File:      ./output/myregbank.vhd")
print("HDL Package:   ./output/myregbank_pkg.vhd")
print("HDL Testbench: ./output/myregbank_tb.vhd")
print("Markdown:      ./output/myregbank.md")
print("C header file: ./output/myregbank.h")
print("----------------------------------------------------------------")

myregbank()