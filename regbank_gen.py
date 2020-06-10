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

def GetSuffix(type):
    if type in ("ReadOnly", "Write2Clear"):
        return "_i"
    else:
        return "_o"

class RegisterBit:
    def __init__(self,name,type):
        if type in RegisterTypeSet:
            self.RegType = type
        else:
            self.RegType = "ReadOnly"
            print("Register Type not known. Using ReadOnly")
            Print(RegisterTypeSet)
        self.ExternalClear = False
        self.name = name+GetSuffix(type)
        self.radix = name
        self.direction = GetDirection(type)
        self.vhdlType = "std_logic"

class RegisterSlice(RegisterBit):
    def __init__(self,name,type,size):
        RegisterBit.__init__(self,name,type)
        self.size = size
        self.vhdlrange = "(%d downto 0)" % size
        self.vhdlType = "std_logic_vector(%d downto 0)" % (size-1)

class RegisterWord(dict):
    def __init__(self,name,size):
        dict.__init__(self)
        self.name = name
        for j in range(size):
            self[j] = ["empty"]

    def add(self,name,type,start,size):
        if "empty" in self[start]:
            if size > 1:
                self[start] = RegisterSlice(name,type,size)
            else:
                self[start] = RegisterBit(name,type)
                for j in range(start+1,start+size):
                    if "empty" in self[j]:
                        self[j] = name+"(%d)" % j
                    else:
                        print("Reg is already occupied by %s" % self[j].name)
        else:
            print("This reg is already occupied by %s" % self[start].name)

class RegisterList(dict):
    def add(self,number,Register):
        self[number] = Register

class RegisterBank(vhdl.BasicVHDL):
    def __init__(self, entity_name, architecture_name, datasize, RegisterNumber):
        vhdl.BasicVHDL.__init__(self, entity_name, architecture_name)
        self.reg = RegisterList()
        self.datasize = datasize
        self.addrsize = math.ceil(math.log(RegisterNumber,2))

        self.Library.add("IEEE")
        self.Library["IEEE"].package.add("numeric_std")
        self.Library.add("stdexpert")
        self.Library["stdexpert"].package.add("std_logic_expert")
        self.Entity.generic.add("C_S_AXI_ADDR_WIDTH", "integer", str(self.addrsize))
        self.Entity.generic.add("C_S_AXI_DATA_WIDTH", "integer", str(self.datasize))
        self.Entity.port.add("S_AXI_ACLK", "in", "std_logic")
        self.Entity.port.add("S_AXI_ARESETN", "in", "std_logic")
        self.Entity.port.add("S_AXI_AWADDR", "in", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.Entity.port.add("S_AXI_AWPROT", "in", "std_logic_vector(2 downto 0)")
        self.Entity.port.add("S_AXI_AWVALID", "in", "std_logic")
        self.Entity.port.add("S_AXI_AWREADY", "out", "std_logic")
        self.Entity.port.add("S_AXI_WSTRB", "in", "std_logic_vector((C_S_AXI_DATA_WIDTH/8)-1 downto 0)")
        self.Entity.port.add("S_AXI_WVALID", "in", "std_logic")
        self.Entity.port.add("S_AXI_WREADY", "out", "std_logic")
        self.Entity.port.add("S_AXI_BRESP", "out", "std_logic_vector(1 downto 0)")
        self.Entity.port.add("S_AXI_BVALID", "out", "std_logic")
        self.Entity.port.add("S_AXI_BREADY", "in", "std_logic")
        self.Entity.port.add("S_AXI_ARADDR", "in", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.Entity.port.add("S_AXI_ARPROT", "in", "std_logic_vector(2 downto 0)")
        self.Entity.port.add("S_AXI_ARVALID", "in", "std_logic")
        self.Entity.port.add("S_AXI_ARREADY", "out", "std_logic")
        self.Entity.port.add("S_AXI_RDATA", "out", "std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0)")
        self.Entity.port.add("S_AXI_RRESP", "out", "std_logic_vector(1 downto 0)")
        self.Entity.port.add("S_AXI_RVALID", "out", "std_logic")
        self.Entity.port.add("S_AXI_RREADY", "in", "std_logic")

        self.Architecture.CustomTypes.add("type reg_t is array (NATURAL RANGE<>) of std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);")
        self.Architecture.Signal.add("axi_awaddr", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.Architecture.Signal.add("axi_awready", "std_logic")
        self.Architecture.Signal.add("axi_wready", "std_logic")
        self.Architecture.Signal.add("axi_bresp", "std_logic_vector(1 downto 0)")
        self.Architecture.Signal.add("axi_bvalid", "std_logic")
        self.Architecture.Signal.add("axi_araddr", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.Architecture.Signal.add("axi_arready", "std_logic")
        self.Architecture.Signal.add("axi_rdata", "std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0)")
        self.Architecture.Signal.add("axi_rresp", "std_logic_vector(1 downto 0)")
        self.Architecture.Signal.add("axi_rvalid", "std_logic")

        self.Architecture.Signal.add("regwrite_s", "reg_t", "(others=>(others=>'0'))")
        self.Architecture.Signal.add("regread_s", "reg_t", "(others=>(others=>'0'))")
        self.Architecture.Signal.add("regclear_s", "reg_t", "(others=>(others=>'0'))")

        self.Architecture.Signal.add("regread_en", "std_logic")
        self.Architecture.Signal.add("regwrite_en", "std_logic")
        self.Architecture.Signal.add("aw_en", "std_logic")

        self.Architecture.BodyCodeHeader.add("S_AXI_AWREADY	<= axi_awready;")
        self.Architecture.BodyCodeHeader.add("S_AXI_WREADY	<= axi_wready;")
        self.Architecture.BodyCodeHeader.add("S_AXI_BRESP	<= axi_bresp;")
        self.Architecture.BodyCodeHeader.add("S_AXI_BVALID	<= axi_bvalid;")
        self.Architecture.BodyCodeHeader.add("S_AXI_ARREADY	<= axi_arready;")
        self.Architecture.BodyCodeHeader.add("S_AXI_RDATA	<= axi_rdata;")
        self.Architecture.BodyCodeHeader.add("S_AXI_RRESP	<= axi_rresp;")
        self.Architecture.BodyCodeHeader.add("S_AXI_RVALID	<= axi_rvalid;")


    def add(self,number,name):
        self.reg.add(number,RegisterWord(name,self.datasize))

    def RegisterPortAdd(self):
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                try:
                    self.Entity.port.add(register[bit].name,register[bit].direction,register[bit].vhdlType)
                except:
                    pass

    def RegisterClearAdd(self):
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                try:
                    if register[bit].ExternalClear:
                        self.Entity.port.add(register[bit].radix+"_clear_i",register[bit].direction,register[bit].vhdlType)
                except:
                    pass

    def RegisterConnection(self):
        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "--Register Connection")
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                if isinstance(register[bit], RegisterBit):
                    VectorRange = str(bit)
                    if isinstance(register[bit], RegisterSlice):
                        VectorRange = "%d downto %d" % (bit+register[bit].size-1, bit)
                        register[bit].name = register[bit].name+"(%d downto 0)" %  (register[bit].size-1)
                    if "ReadOnly" in register[bit].RegType:
                        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" % (index,VectorRange,register[bit].name))
                    elif "ReadWrite" in register[bit].RegType:
                        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" % (register[bit].name,index,VectorRange))
                        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= regwrite_s(%d)(%s);" % (index,VectorRange,index,VectorRange))
                    elif "Write2Clear" in register[bit].RegType:
                        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" % (index,VectorRange,register[bit].name))
                    elif "Write2Pulse" in register[bit].RegType:
                        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" % (register[bit].name,index,VectorRange))
        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "")


    def RegisterClearConnection(self):
        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "--External Clear Connection")
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                if isinstance(register[bit], RegisterBit):
                    clearname = register[bit].radix+"_clear_i"
                    VectorRange = str(bit)
                    if isinstance(register[bit], RegisterSlice):
                        VectorRange = "%d downto %d" % (bit+register[bit].size-1, bit)
                        clearname = "(others=>%s)" % clearname
                    if register[bit].ExternalClear:
                        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "regclear_s(%d)(%s) <= %s;" % (index,VectorRange,clearname))
        self.Architecture.BodyCodeFooter.add("")

    def code(self):
        self.RegisterPortAdd()
        self.RegisterClearAdd()
        self.RegisterConnection()
        self.RegisterClearConnection()
        return vhdl.BasicVHDL.code(self)

myregbank = RegisterBank("myregbank","rtl",32,8)
myregbank.add(0,"golden")
myregbank.reg[0].add("golden","ReadOnly",0,32)
myregbank.add(1,"scrap1")
myregbank.reg[1].add("scrap1","ReadWrite",0,32)
myregbank.reg[1][0].ExternalClear = True
myregbank.add(2,"scrap2")
myregbank.reg[2].add("scrap2","ReadWrite",0,32)
myregbank.reg[2][0].ExternalClear = True

myregbank.add(3,"diverse")
myregbank.reg[3].add("pulse","Write2Pulse",0,1)
myregbank.reg[3].add("w2l","Write2Clear",2,1)
myregbank.reg[3].add("rot","ReadOnly",24,8)
myregbank.reg[3][0].ExternalClear = True
myregbank.reg[3][2].ExternalClear = True
myregbank.reg[3][24].ExternalClear = True

print(myregbank.code())


#Without using the "VHDL FILE"
# def regbank_create(name,qty,size):
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
#     regbank.architecture.signal.add("axi_awaddr", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
#     regbank.architecture.signal.add("axi_awready", "std_logic")
#     regbank.architecture.signal.add("axi_wready", "std_logic")
#     regbank.architecture.signal.add("axi_bresp", "std_logic_vector(1 downto 0)")
#     regbank.architecture.signal.add("axi_bvalid", "std_logic")
#     regbank.architecture.signal.add("axi_araddr", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
#     regbank.architecture.signal.add("axi_arready", "std_logic")
#     regbank.architecture.signal.add("axi_rdata", "std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0)")
#     regbank.architecture.signal.add("axi_rresp", "std_logic_vector(1 downto 0)")
#     regbank.architecture.signal.add("axi_rvalid", "std_logic")
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
