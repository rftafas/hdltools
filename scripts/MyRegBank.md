
Register Bank: MyRegBank
========================

# Details
  
Data Width: 32  
Number of registers: 7  
Version: v20210103_0901  
Register Bank auto-generated using the hdltools/regbank_gen.py  

# List of Registers
  

## Register 0: golden
  
Address: BASE + 0x0  

|Bit|Field|Type|Reset|Description|
| :---: | :---: | :---: | :---: | :---: |
|31-0|golden|ReadOnly|0x0||

## Register 1: myReadWrite1
  
Address: BASE + 0x1  

|Bit|Field|Type|Reset|Description|
| :---: | :---: | :---: | :---: | :---: |
|31-0|myReadWrite1|ReadWrite|0x0||

## Register 2: myReadWrite2
  
Address: BASE + 0x2  
Description: To improve the documentation you can add a description to any                                        register or register field using the * addDescription() * method.  

|Bit|Field|Type|Reset|Description|
| :---: | :---: | :---: | :---: | :---: |
|31-0|myReadWrite2|ReadWrite|0x00000023|Example of ReadWrite register.|

## Register 3: MyWriteToClear
  
Address: BASE + 0x3  

|Bit|Field|Type|Reset|Description|
| :---: | :---: | :---: | :---: | :---: |
|31-0|MyWriteToClear|Write2Clear|0x0||

## Register 4: SlicedReg
  
Address: BASE + 0x4  

|Bit|Field|Type|Reset|Description|
| :---: | :---: | :---: | :---: | :---: |
|15-0|pulse1|Write2Pulse|0x0||
|31-16|pulse2|Write2Pulse|0x0||

## Register 5: MixedRegister
  
Address: BASE + 0x5  

|Bit|Field|Type|Reset|Description|
| :---: | :---: | :---: | :---: | :---: |
|0|PulseBit|Write2Pulse|0x0||
|1|Write2ClearBit|Write2Clear|0x0||
|2|ReadOnlyBit|ReadOnly|1||
|15-8|DivByte1|Write2Clear|0x0||
|23-16|DivByte2|ReadWrite|0x0||
|31-24|DivByte3|ReadOnly|0x0||

## Register 6: ReadAWriteB
  
Address: BASE + 0x6  

|Bit|Field|Type|Reset|Description|
| :---: | :---: | :---: | :---: | :---: |
|31-0|ReadAWriteB|SplitReadWrite|0x0||
  
  
hdltools available at https://github.com/rftafas/hdltools.