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
import vhdl_gen as vhdl
import math

RegisterTypeSet = {"ReadOnly", "ReadWrite", "SplitReadWrite", "Write2Clear", "Write2Pulse"}

TemplateCode = """
    ------------------------------------------------------------------------------------------------
    -- I/O Connections assignments
    ------------------------------------------------------------------------------------------------
    S_AXI_AWREADY <= awready_s;
    S_AXI_WREADY  <= wready_s;
    S_AXI_BRESP   <= bresp_s;
    S_AXI_BVALID  <= bvalid_s;
    S_AXI_ARREADY <= arready_s;
    S_AXI_RDATA   <= rready_s;
    S_AXI_RRESP   <= rresp_s;
    S_AXI_RVALID  <= rvalid_s;

    ------------------------------------------------------------------------------------------------
    --write
    ------------------------------------------------------------------------------------------------
    waddr_p : process(S_AXI_ARESETN, S_AXI_ACLK)
    begin
        if S_AXI_ARESETN = '0' then
            awready_s <= '1';
            awaddr_s  <= (others => '1');
        elsif rising_edge(S_AXI_ACLK) then
            if (awready_s = '1' and S_AXI_AWVALID = '1' ) then
                awready_s <= '0';
                awaddr_s <= S_AXI_AWADDR;
            elsif (S_AXI_BREADY = '1' and bvalid_s = '1') then
                awready_s <= '1';
            elsif timeout_s = '1' then
                awready_s <= '1';
            end if;
        end if;
    end process;

    wdata_p : process (S_AXI_ACLK)
    begin
        if S_AXI_ARESETN = '0' then
            wready_s <= '1';
        elsif rising_edge(S_AXI_ACLK) then
            if (wready_s = '1' and S_AXI_WVALID = '1') then
                wready_s <= '0';
            elsif (S_AXI_BREADY = '1' and bvalid_s = '1') then
                wready_s <= '1';
            elsif timeout_s = '1' then
                wready_s <= '1';
            end if;
        end if;
    end process;

    wresp_p : process (S_AXI_ACLK)
    begin
        if S_AXI_ARESETN = '0' then
            bvalid_s  <= '0';
            bresp_s   <= "00";
        elsif rising_edge(S_AXI_ACLK) then
            if (wready_s = '1' and awready_s = '1' ) then
                bvalid_s <= '1';
                bresp_s  <= "00";
                bresp_timer_sr <= ( 0 => '1', others=>'0' );
            elsif wtimeout_s = '1' then
                bvalid_s <= '1';
                bresp_s  <= "10";
                bresp_timer_sr <= ( 0 => '1', others=>'0' );
            elsif bvalid_s = '1 then
                bresp_timer_sr <= bresp_timer_sr(14 downto 0) & bresp_timer_sr(15);
                if S_AXI_BREADY = '1' or bresp_timer_sr(15) = '0' then
                    bvalid_s <= '0';
                    bresp_s  <= "00";
                    bresp_timer_sr <= ( others=>'0' );
                end if;
            end if;
        end if;
    end process;

    wtimer_p : process (S_AXI_ACLK)
    begin
        if S_AXI_ARESETN = '0' then
            wtimeout_s   <= '0';
        elsif rising_edge(S_AXI_ACLK) then
            wtimeout_s <= wtimeout_sr(15);
            if wready_s = '1' or awready_s = '1' then
                wtimeout_sr <= ( 0 => '1', others=>'0');
            elsif wready_s = '1' and awready_s = '1' then
                wtimeout_sr (others=>'0');
            else
                wtimeout_sr <= wtimeout_sr(14 downto 0) & wtimeout_sr(15);
            end if;
        end if;
    end process;

    regwrite_en <= wready_s  and  awready_s;

    wreg_p : process (S_AXI_ACLK)
        variable loc_addr : integer;
    begin
        if S_AXI_ARESETN = '0' then
            regwrite_s <= (others => (others => '0'));
        elsif rising_edge(S_AXI_ACLK) then
            loc_addr := to_integer(unsigned(awaddr_s(C_S_AXI_ADDR_WIDTH-1 downto ADDR_LSB)));
            for j in regwrite_s'range loop
                for k in BYTE_NUM-1 downto 0 loop
                    for m in 7 downto 0 loop
                        if ext_clear_s(j)(k*8+m) = '1' then
                            regwrite_s(j)(k*8+m) <= '0';
                        elsif regwrite_en = '1' then
                            if S_AXI_WSTRB(k) = '1' then
                                if write2clear_c(j)(k*8+m) or write2pulse_c(j)(k*8+m) = '1' then
                                    if regwrite_s(j)(k*8+m) = '1' then
                                        regwrite_s(j)(k*8+m) <= '0';
                                    else
                                        regwrite_s(j)(k*8+m) <= S_AXI_WDATA(k*8+m);
                                    end if;
                                else
                                    regwrite_s(j)(k*8+m) <= S_AXI_WDATA(k*8+m);
                                end if;
                            end if;
                        end if;
                    end loop;
                end loop;
            end loop;
        end if;
    end process;

    ------------------------------------------------------------------------------------------------
    --Read
    ------------------------------------------------------------------------------------------------
    raddr_p : process(S_AXI_ARESETN, S_AXI_ACLK)
    begin
        if S_AXI_ARESETN = '0' then
            arready_s <= '0';
            araddr_s  <= (others => '1');
        elsif rising_edge(S_AXI_ACLK) then
            if (arready_s = '1' and S_AXI_ARVALID = '1') then
                arready_s <= '0';
                araddr_s  <= S_AXI_ARADDR;
            elsif rvalid_s = '1' then
                arready_s <= '1';
            end if;
        end if;
    end process;

    --AXI uses same channel for data and response.
    --one can consider that AXI-S RRESP is sort of TUSER.
    rresp_rdata_p : process(S_AXI_ARESETN, S_AXI_ACLK)
    begin
        if S_AXI_ARESETN = '0' then
            rvalid_s <= '0';
            rresp_s  <= "00";
        elsif rising_edge(S_AXI_ACLK) then
            if arready_s = '0' then --there is an address waiting for us.
                axi_rvalid <= '1';
                axi_rresp  <= "00"; -- 'OKAY' response
            elsif S_AXI_RREADY = '1' then
                --Read data is accepted by the master
                axi_rvalid <= '0';
            elsif rtimeout_s = '1' then
                --when it times out? when after doing my part, master does not respond
                --with the RREADY, meaning he havent read my data.
                axi_rvalid <= '0';
                axi_rresp  <= "10"; -- No one is expected to read this. Debug only.
            else
                axi_rvalid <= '0';
                axi_rresp  <= "00"; -- No one is expected to read this. Debug only.
            end if;
        end if;
    end process;

    rtimer_p : process (S_AXI_ACLK)
    begin
        if S_AXI_ARESETN = '0' then
            rtimeout_s   <= '0';
        elsif rising_edge(S_AXI_ACLK) then
            rtimeout_s <= wtimeout_sr(15);
            if rready_s = '0' then
                rtimeout_sr <= ( 0 => '1', others=>'0');
            else
                rtimeout_sr <= rtimeout_sr(14 downto 0) & rtimeout_sr(15);
            end if;
        end if;
    end process;

    --we only act if there is no pending read.
    regread_en <= arready_s nand rvalid_s;

    --get data from ports to bus
    read_reg_p : process( S_AXI_ACLK ) is
        variable loc_addr : integer;
        variable reg_tmp : reg_t := (others => (others => '0'));
    begin
        if (S_AXI_ARESETN = '0') then
            reg_tmp  := (others => (others => '0'));
            reg_lock := (others => (others => '0'));
        elsif (rising_edge (S_AXI_ACLK)) then
            for j in regread_s'range then
                for k in regread_s(0)'range then'
                    if regclear_s(j)(k) = '1' then
                        reg_tmp(j)(k)  <= '0';
                        reg_lock(j)(k) <= '0';
                    elsif regset_s(j)(k) = '1' then
                        reg_tmp(j)(k)  <= '1';
                        reg_lock(j)(k) <= '1';
                    elsif reg_lock(j)(k) = '0' then
                        reg_tmp(j)(k) <= regread_s(j)(k);
                    end if;
                end loop;
            end loop;
            --
            loc_addr := to_integer(axi_araddr(C_S_AXI_ADDR_WIDTH-1 downto ADDR_LSB);
            if regread_en = '1' then
                S_AXI_RDATA  <= reg_tmp(loc_addr);
            end if;
        end if;
    end process;
"""

def GetDirection(type):
    if type in ("ReadOnly", "Write2Clear", "SplitReadWrite"):
        return "in"
    else:
        return "out"

def GetSuffix(direction):
    if direction in ("in"):
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
        self.direction = GetDirection(type)
        self.vhdlType = "std_logic"
        self.name = name+GetSuffix(self.direction)
        self.radix = name

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

class registerBank(vhdl.basicVHDL):
    def __init__(self, entity_name, architecture_name, datasize, RegisterNumber):
        vhdl.basicVHDL.__init__(self, entity_name, architecture_name)
        self.generate_code = False
        self.reg = RegisterList()
        self.datasize = datasize
        self.addrsize = math.ceil(math.log(RegisterNumber,2))

        self.library.add("IEEE")
        self.library["IEEE"].package.add("numeric_std")
        self.library.add("stdexpert")
        self.library["stdexpert"].package.add("std_logic_expert")
        self.entity.generic.add("C_S_AXI_ADDR_WIDTH", "integer", str(self.addrsize))
        self.entity.generic.add("C_S_AXI_DATA_WIDTH", "integer", str(self.datasize))
        self.entity.port.add("S_AXI_ACLK", "in", "std_logic")
        self.entity.port.add("S_AXI_ARESETN", "in", "std_logic")
        self.entity.port.add("S_AXI_AWADDR", "in", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.entity.port.add("S_AXI_AWPROT", "in", "std_logic_vector(2 downto 0)")
        self.entity.port.add("S_AXI_AWVALID", "in", "std_logic")
        self.entity.port.add("S_AXI_AWREADY", "out", "std_logic")
        self.entity.port.add("S_AXI_WSTRB", "in", "std_logic_vector((C_S_AXI_DATA_WIDTH/8)-1 downto 0)")
        self.entity.port.add("S_AXI_WVALID", "in", "std_logic")
        self.entity.port.add("S_AXI_WREADY", "out", "std_logic")
        self.entity.port.add("S_AXI_BRESP", "out", "std_logic_vector(1 downto 0)")
        self.entity.port.add("S_AXI_BVALID", "out", "std_logic")
        self.entity.port.add("S_AXI_BREADY", "in", "std_logic")
        self.entity.port.add("S_AXI_ARADDR", "in", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.entity.port.add("S_AXI_ARPROT", "in", "std_logic_vector(2 downto 0)")
        self.entity.port.add("S_AXI_ARVALID", "in", "std_logic")
        self.entity.port.add("S_AXI_ARREADY", "out", "std_logic")
        self.entity.port.add("S_AXI_RDATA", "out", "std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0)")
        self.entity.port.add("S_AXI_RRESP", "out", "std_logic_vector(1 downto 0)")
        self.entity.port.add("S_AXI_RVALID", "out", "std_logic")
        self.entity.port.add("S_AXI_RREADY", "in", "std_logic")

        self.architecture.customTypes.add("type reg_t is array (NATURAL RANGE<>) of std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);")
        self.architecture.Signal.add("awaddr_s", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.architecture.Signal.add("awready_s", "std_logic")
        self.architecture.Signal.add("wready_s", "std_logic")
        self.architecture.Signal.add("bresp_s", "std_logic_vector(1 downto 0)")
        self.architecture.Signal.add("bvalid_s", "std_logic")
        self.architecture.Signal.add("wtimeout_sr", "std_logic_vector(15 downto 0)")
        self.architecture.Signal.add("wtimeout_s", "std_logic")

        self.architecture.Signal.add("araddr_s", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.architecture.Signal.add("arready_s", "std_logic")
        self.architecture.Signal.add("rresp_s", "std_logic_vector(1 downto 0)")
        self.architecture.Signal.add("rvalid_s", "std_logic")
        self.architecture.Signal.add("rtimeout_sr", "std_logic_vector(15 downto 0)")
        self.architecture.Signal.add("rtimeout_s", "std_logic")

        self.architecture.Signal.add("regwrite_s", "reg_t", "(others=>(others=>'0'))")
        self.architecture.Signal.add("regread_s", "reg_t", "(others=>(others=>'0'))")
        self.architecture.Signal.add("regclear_s", "reg_t", "(others=>(others=>'0'))")
        self.architecture.Signal.add("regset_s", "reg_t", "(others=>(others=>'0'))")

        self.architecture.Signal.add("regread_en", "std_logic")
        self.architecture.Signal.add("regwrite_en", "std_logic")

        for lines in TemplateCode.splitlines():
            self.architecture.bodyCodeHeader.add(lines)


    def add(self,number,name):
        self.reg.add(number,RegisterWord(name,self.datasize))

    def RegisterPortAdd(self):
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                try:
                    if "SplitReadWrite" in register[bit].RegType:
                        self.entity.port.add(register[bit].radix+GetSuffix("in"),"in",register[bit].vhdlType)
                        self.entity.port.add(register[bit].radix+GetSuffix("out"),"out",register[bit].vhdlType)
                    else:
                        self.entity.port.add(register[bit].name,register[bit].direction,register[bit].vhdlType)
                except:
                    pass

    def RegisterClearAdd(self):
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                try:
                    if register[bit].ExternalClear:
                        self.entity.port.add(register[bit].radix+"_clear_i",register[bit].direction,register[bit].vhdlType)
                except:
                    pass

    def RegisterConnection(self):
        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "--Register Connection")
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                if isinstance(register[bit], RegisterBit):
                    VectorRange = str(bit)
                    if isinstance(register[bit], RegisterSlice):
                        VectorRange = "%d downto %d" % (bit+register[bit].size-1, bit)
                        register[bit].name = register[bit].name+"(%d downto 0)" %  (register[bit].size-1)
                    if "ReadOnly" in register[bit].RegType:
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" % (index,VectorRange,register[bit].name))
                    elif "ReadWrite" in register[bit].RegType:
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" % (register[bit].name,index,VectorRange))
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= regwrite_s(%d)(%s);" % (index,VectorRange,index,VectorRange))
                    elif "SplitReadWrite" in register[bit].RegType:
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" % (register[bit].radix+GetSuffix("out"),index,VectorRange))
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" % (index,VectorRange,register[bit].radix+GetSuffix("in")))
                    elif "Write2Clear" in register[bit].RegType:
                        pass #self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" % (index,VectorRange,register[bit].name))
                    elif "Write2Pulse" in register[bit].RegType:
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" % (register[bit].name,index,VectorRange))
        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "")

    def RegisterSetConnection(self):
        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "--Set Connection for Write to Clear")
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                if isinstance(register[bit], RegisterBit):
                    VectorRange = str(bit)
                    if isinstance(register[bit], RegisterSlice):
                        VectorRange = "%d downto %d" % (bit+register[bit].size-1, bit)
                    if "Write2Clear" in register[bit].RegType:
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regset_s(%d)(%s) <= %s;" % (index,VectorRange,register[bit].name))
                        #self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regset_s(%d)(%s) <= regread_s(%d)(%s)" % (index,VectorRange,index,VectorRange))
        self.architecture.bodyCodeFooter.add("")

    def RegisterClearConnection(self):
        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "--External Clear Connection")
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                if isinstance(register[bit], RegisterBit):
                    clearname = register[bit].radix+"_clear_i"
                    defaultvalue = "'1'"
                    elsevalue = "'0'"
                    VectorRange = str(bit)
                    if isinstance(register[bit], RegisterSlice):
                        VectorRange = "%d downto %d" % (bit+register[bit].size-1, bit)
                        defaultvalue = "(others=>'1')"
                    if "Write2Clear" in register[bit].RegType:
                        elsevalue =  "regwrite_s(%d)(%s)" % (index,VectorRange)
                    if register[bit].ExternalClear:
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regclear_s(%d)(%s) <= %s when %s = '1' else %s;" % (index,VectorRange,defaultvalue,clearname,elsevalue))
        self.architecture.bodyCodeFooter.add("")

    def code(self):
        if (not self.generate_code):
            self.RegisterPortAdd()
            self.RegisterClearAdd()
            self.RegisterConnection()
            self.RegisterSetConnection()
            self.RegisterClearConnection()
            self.generate_code = True
        return vhdl.basicVHDL.code(self)

    def write_file(self):
        return vhdl.basicVHDL.write_file(self)

if __name__ == '__main__':

    #first we declare a register bank.
    #It is a 32 bit register with 8 possible positions.
    #we named the architecture "RTL".
    myregbank = registerBank("myregbank","rtl",32,8)

    #this is an axample of a read only register for ID, Golden number, Inputs
    #we add a position (address) and name it. Also, it is a 32bit, it must start at 0.
    #myregbank.add(REG_ADDRESS,"golden")
    #myregbank.reg[REG_ADDRESS].add(NAME,TYPE,START BIT POSITION,SIZE)
    myregbank.add(0,"golden")
    myregbank.reg[0].add("golden","ReadOnly",0,32)
    #this is an example for a read/write generic register.
    myregbank.add(1,"myReadWrite1")
    myregbank.reg[1].add("myReadWrite1","ReadWrite",0,32)
    #this is an example for a read/write generic register with external clear.
    myregbank.add(2,"myReadWrite2")
    myregbank.reg[2].add("myReadWrite2","ReadWrite",0,32)
    myregbank.reg[2].ExternalClear = True
    #this is an example of a write to clear register
    myregbank.add(3,"MyWriteToClear")
    myregbank.reg[3].add("MyWriteToClear","Write2Clear",0,32)
    #wee can use just a slice on any type. Lets create a slice.
    #we will use 2 16bit register.
    myregbank.add(4,"SlicedReg")
    myregbank.reg[4].add("pulse","Write2Pulse",0,16)
    myregbank.reg[4].add("pulse","Write2Pulse",16,16)

    #And we can create a very mixed register:
    #Bit 0 is goint to be a pulsed register. Write one, it pulses output.
    myregbank.add(5,"MixedRegister")
    myregbank.reg[5].add("PulseBit","Write2Pulse",0,1)
    myregbank.reg[5][0].ExternalClear = True #for example, we want to kill the pulse.
    myregbank.reg[5].add("Write2ClearBit","Write2Clear",1,1)
    myregbank.reg[5][1].ExternalClear = True #either my write or the external can clear it.
    myregbank.reg[5].add("ReadOnlyBit","ReadOnly",2,1)
    myregbank.reg[5][2].ExternalClear = True #I can force a '0' read.
    myregbank.reg[5].add("DivByte1","Write2Clear",8,8)
    myregbank.reg[5].add("DivByte2","ReadWrite",16,8)
    myregbank.reg[5].add("DivByte3","ReadOnly",24,8)

    #And we can create a very mixed register:
    #Bit 0 is goint to be a pulsed register. Write one, it pulses output.
    myregbank.add(6,"ReadAWriteB")
    myregbank.reg[6].add("ReadAWriteB","SplitReadWrite",0,32)


    print(myregbank.code())

    myregbank.write_file()
    print("-------------------------------------------------------------")
    print("The example will be stored at ./output/myregbank.vhd")
