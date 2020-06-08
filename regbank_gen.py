import sys
import os
import vhdl_gen as vhdl
import math

RegisterTypeSet = {"ReadOnly", "ReadWrite", "Write2Clear", "Write2Pulse"}

def GetDirection(type):
    if type in ("ReadOnly", "Write2Clear"):
        return "in"
    else:
        return "out"

class RegisterBit:
    def __init__(self,name,type, *args):
        if type in RegisterTypeSet:
            self.RegType = type
        else:
            self.RegType = "ReadOnly"
        self.ExternalClear = False
        self.name = name
        self.direction = GetDirection(type)
        self.vhdlType = "std_logic"
    def port(self):
        return (self.name,self.direction,self.vhdlType)

class RegisterSlice(RegisterBit):
    def __init__(self,name,type,size):
        RegisterBit.__init__(self,name,type)
        self.size = size
        self.vhdlType = "std_logic_vector(%s downto 0)" % str(size-1)

Port = vhdl.PortList()
regbit1 = RegisterBit("bitname1","ReadOnly")
regslice1 = RegisterSlice("slicename","ReadOnly",5)
Port.add(regbit1.name,regbit1.direction,regbit1.vhdlType)
Port.add(regslice1.name,regslice1.direction,regslice1.vhdlType)
print Port.code()

class RegisterWord:
    def __init__(self,name,size):
        self.bits = [None] * size

    def AddBit(self,position, regbit):
        if self.bits[position] == None:
            self.bits[position] = regbit
        else:
            print("This reg is already occupied by %s" % self.bits[position].name)
    def AddSlice(self, position, regslice):
        for j in range(position,position+regslice.size):
            self.AddBit( j, regslice)

class RegisterList:
    def __init__(self):
        self.list = []

    def add(self,number,Register):
        self.list[number] = Register

    def code(self):
        hdl_code = ""
        for j in self.list:
            if type in ("ReadOnly", "Write2Clear"):
                hdl_code = hdl_code + "reg_read_s(%i) <= %s;\r\n"


my_reg = RegisterWord("myregister",32)
my_reg.AddBit(0,regbit1)
my_reg.AddBit(31,regbit1)
my_reg.AddSlice(5,regslice1)

reg_list = RegisterList();
reg_list.add(0,my_reg)


#Without using the "VHDL FILE"
# def regbank_create(name,qty,size):
#
#     addr_witdh = str(math.ceil(math.log(qty,2)))
#     data_witdh = str(size)
#     regbank = vhdl_gen.vhdl_file(name,"behavioral")
#     #libraries
#     Library = LibraryList()
#     Library["IEEE"] = LibraryObj("IEEE")
#     Library["IEEE"].package.add("numeric_std")
#     #entity - generic
#     Entity =
#     Entity.generic.add("C_S_AXI_ADDR_WIDTH", "integer", addr_witdh)
#     Entity.generic.add("C_S_AXI_DATA_WIDTH", "integer", data_witdh)
#     #entity - port
#     regbank.entity.port.add("S_AXI_ACLK", "in", "std_logic")
#     regbank.entity.port.add("S_AXI_ARESETN", "in", "std_logic")
#     regbank.entity.port.add("S_AXI_AWADDR", "in", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
#     regbank.entity.port.add("S_AXI_AWPROT", "in", "std_logic_vector(2 downto 0)")
#     regbank.entity.port.add("S_AXI_AWVALID", "in", "std_logic")
#     regbank.entity.port.add("S_AXI_AWREADY", "out", "std_logic")
#     regbank.entity.port.add("S_AXI_WSTRB", "in", "std_logic_vector((C_S_AXI_DATA_WIDTH/8)-1 downto 0)")
#     regbank.entity.port.add("S_AXI_WVALID", "in", "std_logic")
#     regbank.entity.port.add("S_AXI_WREADY", "out", "std_logic")
#     regbank.entity.port.add("S_AXI_BRESP", "out", "std_logic_vector(1 downto 0)")
#     regbank.entity.port.add("S_AXI_BVALID", "out", "std_logic")
#     regbank.entity.port.add("S_AXI_BREADY", "in", "std_logic")
#     regbank.entity.port.add("S_AXI_ARADDR", "in", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
#     regbank.entity.port.add("S_AXI_ARPROT", "in", "std_logic_vector(2 downto 0)")
#     regbank.entity.port.add("S_AXI_ARVALID", "in", "std_logic")
#     regbank.entity.port.add("S_AXI_ARREADY", "out", "std_logic")
#     regbank.entity.port.add("S_AXI_RDATA", "out", "std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0)")
#     regbank.entity.port.add("S_AXI_RRESP", "out", "std_logic_vector(1 downto 0)")
#     regbank.entity.port.add("S_AXI_RVALID", "out", "std_logic")
#     regbank.entity.port.add("S_AXI_RREADY", "in", "std_logic")
#
#     #adds custom code not provided by lib.
#     regbank.architecture.declaration_code("type reg_t is array (NATURAL RANGE<>) of std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);\r\n")
#
#     regbank.architecture.signal.add("axi_awaddr", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)", "")
#     regbank.architecture.signal.add("axi_awready", "std_logic", "")
#     regbank.architecture.signal.add("axi_wready", "std_logic", "")
#     regbank.architecture.signal.add("axi_bresp", "std_logic_vector(1 downto 0)", "")
#     regbank.architecture.signal.add("axi_bvalid", "std_logic", "")
#     regbank.architecture.signal.add("axi_araddr", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)", "")
#     regbank.architecture.signal.add("axi_arready", "std_logic", "")
#     regbank.architecture.signal.add("axi_rdata", "std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0)", "")
#     regbank.architecture.signal.add("axi_rresp", "std_logic_vector(1 downto 0)", "")
#     regbank.architecture.signal.add("axi_rvalid", "std_logic", "")
#
#     regbank.architecture.constant.add("slv_reg_write", "reg_t", "(others=>(others=>'0'))")
#     regbank.architecture.constant.add("slv_reg_read", "reg_t", "(others=>(others=>'0'))")
#     regbank.architecture.constant.add("write_vec", "reg_t", "(others=>(others=>'0'))")
#     regbank.architecture.constant.add("read_fec", "reg_t", "(others=>(others=>'0'))")
#
#     regbank.architecture.body_code = "  --Test adding custom body code.\r\n"
#
#     return regbank
#
# regbank = regbank_create("test_axim_regbank",4,32)
# print Library.code()
