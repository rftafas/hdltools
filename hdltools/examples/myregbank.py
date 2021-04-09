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
#It is not related to any core, block or nwither it have any meaning. Just a
#bunch of loose registers.

# first we declare a register bank.
# It is a 32 bit register with 8 possible positions.
# we named the architecture "RTL".
myregbank = hdltools.RegisterBank("myregbank", "rtl", 32, 8)

# this is an axample of a read only register for ID, Golden number, or other inputs
# we add a position (address) and name it.
# myregbank.add(REG_ADDRESS,"golden")
myregbank.add(0, "Golden")
# This golden number should be 32bit, it must start at 0. We have to name the segment, in
# this case, we will use 'G1'. It is not important here, but imagine multisegmented register...
# myregbank.reg[REG_ADDRESS].add(NAME,TYPE,START BIT POSITION,SIZE)
myregbank.reg[0].add("g1", "ReadOnly", 0, 32)
# this is an example for a read/write generic register.
myregbank.add(1, "ReadWrite1")
myregbank.reg[1].add("rw1", "ReadWrite", 0, 32)
# this is an example for a read/write generic register with external clear.
myregbank.add(2, "ReadWrite2")
myregbank.reg[2].add("rw2", "ReadWrite", 0, 32)
myregbank.reg[2].externalClear = True
# this is an example of a write to clear register
myregbank.add(3, "WriteToClear")
myregbank.reg[3].add("w2c1", "Write2Clear", 0, 32)
# wee can use just a slice on any type. Lets create a slice. This is why we have REGISTER_NAME
# and also some SEGMENT_NAME. In this case, we will have 2 16bit register (high and low).
# for whatever reason, we may want it pulsed.
myregbank.add(4, "SlicedReg")
myregbank.reg[4].add("pulse1", "Write2Pulse", 0, 16)
myregbank.reg[4].add("pulse2", "Write2Pulse", 16, 16)
# And we can create a very mixed register:
# Bit 0 is goint to be a pulsed register. Write one, it pulses output.
myregbank.add(5, "MixedRegister")
myregbank.reg[5].add("pulse3", "Write2Pulse", 0, 1)
myregbank.reg[5][0].externalClear = True  # for example, we want to kill the pulse.
myregbank.reg[5].add("w2c2", "Write2Clear", 1, 1)
myregbank.reg[5][1].externalClear = True  # either my write or the external can clear it.
myregbank.reg[5].add("ro1", "ReadOnly", 2, 1)
myregbank.reg[5][2].externalClear = True  # I can force a '0' read.
myregbank.reg[5].add("div1", "Write2Clear", 8, 8)
myregbank.reg[5].add("div2", "ReadWrite", 16, 8)
myregbank.reg[5].add("div3", "ReadOnly", 24, 8)

# And we can create a very mixed register:
# Bit 0 is goint to be a pulsed register. Write one, it pulses output.
myregbank.add(6, "ReadAWriteB")
myregbank.reg[6].add("rAwB", "SplitReadWrite", 0, 32)

myregbank.add(7, "reg2clear")
myregbank.reg[7].add("reg2clear", "ReadWrite", 0, 32)
myregbank.reg[7][0].externalClear = True

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