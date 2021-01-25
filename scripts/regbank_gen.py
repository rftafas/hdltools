#################################################################################
# Copyright 2020 Ricardo F Tafas Jr
# Contrib.: T.P. Correa

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.
#################################################################################
## Contributor list:
## 2020 - Ricardo F Tafas Jr - https://github.com/rftafas
## 2020 - T.P. Correa - https://github.com/tpcorrea

import sys
import os
from datetime import datetime
import vhdl_gen as vhdl
import pkgvhdl_gen as pkgvhdl
import tb_gen as tbvhdl
import math
import random
from mdutils.mdutils import MdUtils

indent = vhdl.indent
RegisterTypeSet = {"ReadOnly", "ReadWrite", "SplitReadWrite", "Write2Clear", "Write2Pulse"}
vunitPort = ( "aclk", "--areset_n", "awaddr", "--awprot", "awvalid", "awready", "wdata", "wstrb", "wvalid", "wready", "bresp", "bvalid", "bready", "araddr", "--arprot", "arvalid", "arready", "rdata", "rresp", "rvalid", "rready" )

  

testBenchCode = """
S_AXI_ACLK <= not S_AXI_ACLK after 10 ns;

main : process
    variable rdata_v : std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0) := (others=>'0');
begin
    test_runner_setup(runner, runner_cfg);
    S_AXI_ARESETN     <= '0';
    wait until rising_edge(S_AXI_ACLK);
    wait until rising_edge(S_AXI_ACLK);
    S_AXI_ARESETN     <= '1';
    wait until rising_edge(S_AXI_ACLK);
    wait until rising_edge(S_AXI_ACLK);

    while test_suite loop
        if run("Sanity check for system.") then
            report "System Sane. Begin tests.";
            check_passed(result("Sanity check for system."));

        elsif run("Simple Run Test") then
            wait for 100 us;
            check_passed(result("Simple Run Test Pass."));

        elsif run("Read Only Test") then
--read_only_tag
        elsif run("Read and Write Test") then
--read_write_tag
        elsif run("Split Read Write Test") then
--split_read_write_tag
        elsif run("Write to Clear Test") then
--write_to_clear_tag
        end if;
    end loop;
    test_runner_cleanup(runner); -- Simulation ends here
end process;

test_runner_watchdog(runner, 101 us);

"""





TemplateCode = """
    ------------------------------------------------------------------------------------------------
    -- I/O Connections assignments
    ------------------------------------------------------------------------------------------------
    S_AXI_AWREADY <= awready_s;
    S_AXI_WREADY  <= wready_s;
    S_AXI_BRESP   <= bresp_s;
    S_AXI_BVALID  <= bvalid_s;
    S_AXI_ARREADY <= arready_s;
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
            if S_AXI_AWVALID = '1' then
                awready_s <= '0';
                awaddr_s <= S_AXI_AWADDR;
            elsif (S_AXI_BREADY = '1' and bvalid_s = '1') then
                awready_s <= '1';
            elsif wtimeout_s = '1' then
                awready_s <= '1';
            end if;
        end if;
    end process;

    wdata_p : process (S_AXI_ACLK)
    begin
        if S_AXI_ARESETN = '0' then
            wready_s <= '1';
        elsif rising_edge(S_AXI_ACLK) then
            if S_AXI_WVALID = '1' then
                wready_s <= '0';
            elsif (S_AXI_BREADY = '1' and bvalid_s = '1') then
                wready_s <= '1';
            elsif wtimeout_s = '1' then
                wready_s <= '1';
            end if;
        end if;
    end process;

    wreg_en_p : process (S_AXI_ACLK)
        variable lock_v : std_logic;
    begin
        if S_AXI_ARESETN = '0' then
            regwrite_en <= '0';
            lock_v := '0';
        elsif rising_edge(S_AXI_ACLK) then
            if lock_v = '1' then
                regwrite_en <= '0';
                if (S_AXI_BREADY = '1' and bvalid_s = '1') then
                    lock_v := '1';
                end if;
            elsif (wready_s = '0' or S_AXI_WVALID = '1' ) and ( awready_s = '0' or S_AXI_AWVALID = '1' )then
                regwrite_en <= '1';
                lock_v := '1';
            elsif wtimeout_s = '1' then
                regwrite_en <= '0';
                lock_v := '0';
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
            elsif bvalid_s = '1' then
                bresp_timer_sr <= bresp_timer_sr(14 downto 0) & bresp_timer_sr(15);
                if S_AXI_BREADY = '1' or bresp_timer_sr(15) = '1' then
                    bvalid_s <= '0';
                    bresp_s  <= "00";
                    bresp_timer_sr <= ( 0 => '1', others=>'0' );
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
                wtimeout_sr <= (others=>'0');
            else
                wtimeout_sr <= wtimeout_sr(14 downto 0) & wtimeout_sr(15);
            end if;
        end if;
    end process;

    wreg_p : process (S_AXI_ACLK)
        variable loc_addr : integer;
    begin
        if S_AXI_ARESETN = '0' then
            regwrite_s <= (others => (others => '0'));
        elsif rising_edge(S_AXI_ACLK) then
            loc_addr := to_integer(awaddr_s(C_S_AXI_ADDR_WIDTH-1 downto C_S_AXI_ADDR_LSB));
            for j in regwrite_s'range loop
                for k in C_S_AXI_ADDR_BYTE-1 downto 0 loop
                    for m in 7 downto 0 loop
                        if regclear_s(j)(k*8+m) = '1' then
                            regwrite_s(j)(k*8+m) <= '0';
                        elsif regwrite_en = '1' then                            
                            if j = loc_addr then
                                if S_AXI_WSTRB(k) = '1' then
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
    raddr_p : process (S_AXI_ARESETN, S_AXI_ACLK)
    begin
        if S_AXI_ARESETN = '0' then
            arready_s  <= '1';
            regread_en <= '0';
            araddr_s   <= (others => '1');
        elsif rising_edge(S_AXI_ACLK) then
            if S_AXI_ARVALID = '1' then
                arready_s  <= '0';
                araddr_s   <= S_AXI_ARADDR;
                regread_en <= '1';
            elsif rvalid_s = '1' and S_AXI_RREADY = '1' then
                arready_s  <= '1';
                regread_en <= '0';
            elsif rtimeout_s = '1' then
                arready_s  <= '1';
                regread_en <= '0';
            else
                regread_en <= '0';
            end if;
        end if;
    end process;

    --AXI uses same channel for data and response.
    --one can consider that AXI-S RRESP is sort of TUSER.
    rresp_rdata_p : process (S_AXI_ARESETN, S_AXI_ACLK)
    begin
        if S_AXI_ARESETN = '0' then
            rvalid_s <= '0';
            rresp_s  <= "00";
        elsif rising_edge(S_AXI_ACLK) then
            if regread_en = '1' then --there is an address waiting for us.
                rvalid_s <= '1';
                rresp_s  <= "00"; -- 'OKAY' response
            elsif S_AXI_RREADY = '1' then
                --Read data is accepted by the master
                rvalid_s <= '0';
            elsif rtimeout_s = '1' then
                --when it times out? when after doing my part, master does not respond
                --with the RREADY, meaning he havent read my data.
                rvalid_s <= '0';
                rresp_s  <= "10"; -- No one is expected to read this. Debug only.
            else
                rvalid_s <= '0';
                rresp_s  <= "00"; -- No one is expected to read this. Debug only.
            end if;
        end if;
    end process;

    rtimer_p : process (S_AXI_ACLK)
    begin
        if S_AXI_ARESETN = '0' then
            rtimeout_s   <= '0';
        elsif rising_edge(S_AXI_ACLK) then
            rtimeout_s <= rtimeout_sr(15);
            if S_AXI_RREADY = '1' then
                rtimeout_sr <= ( 0 => '1', others=>'0');
            elsif rvalid_s = '1' then
                rtimeout_sr <= rtimeout_sr(14 downto 0) & rtimeout_sr(15);
            end if;
        end if;
    end process;

    --get data from ports to bus
    read_reg_p : process( S_AXI_ACLK ) is
        variable loc_addr : integer;
        variable reg_tmp  : reg_t := (others => (others => '0'));
        variable reg_lock : reg_t := (others => (others => '0'));
    begin
        if (S_AXI_ARESETN = '0') then
            reg_tmp     := (others => (others => '0'));
            reg_lock    := (others => (others => '0'));
            S_AXI_RDATA <= (others => '0');
        elsif (rising_edge (S_AXI_ACLK)) then
            for j in regread_s'range loop
                for k in regread_s(0)'range loop
                    if regclear_s(j)(k) = '1' then
                        reg_tmp(j)(k)  := '0';
                        reg_lock(j)(k) := '0';
                    elsif regset_s(j)(k) = '1' then
                        reg_tmp(j)(k)  := '1';
                        reg_lock(j)(k) := '1';
                    elsif reg_lock(j)(k) = '0' then
                        reg_tmp(j)(k) := regread_s(j)(k);
                    end if;
                end loop;
            end loop;
            --
            loc_addr := to_integer(araddr_s(C_S_AXI_ADDR_WIDTH-1 downto C_S_AXI_ADDR_LSB));
            if regread_en = '1' then
                S_AXI_RDATA  <= reg_tmp(loc_addr);
            end if;
        end if;
    end process;
"""

def byte_enable_vector(start,end,size):
    vector = "\""
    tmp1 = math.floor(start/8)
    tmp2 = math.floor(end/8)
    j = math.ceil(size/8)-1
    while j >= 0:
        if (j < tmp1 or j > tmp2):
            vector += "0"
        else:
            vector += "1"
        j -= 1
    vector += "\""
    return vector

def random_vector(length):
    bits = "01"
    vector = "\""
    j = 0
    while j < length:
        vector += random.choice(bits)
        j += 1
    vector += "\""
    return vector

def random_bit():
    bits = "01"
    vector = "'"
    vector += random.choice(bits)
    vector += "'"
    return vector

def GetDirection(type):
    if type in ("ReadOnly", "Write2Clear", "SplitReadWrite"):
        return "in"
    else:
        return "out"


def InvertDirection(direction):
    if direction in ("in"):
        return "out"
    else:
        return "in"


def GetSuffix(direction):
    if direction in ("in"):
        return "_i"
    else:
        return "_o"


class RegisterBit:
    def __init__(self, name, type, init):
        self.name = name
        self.externalClear = False
        self.clearName = self.name+"_clear"
        self.vhdlType = "std_logic"
        self.radix = name
        self.size = 1
        self.description = ""
        self.position = ""

        if init is None:
            self.init = "'0'"
        else:
            self.init = init

        if type in RegisterTypeSet:
            self.regType = type
        else:
            self.regType = "SplitReadWrite"
            print("Register Type not known. Using SplitReadWrite")
            print(RegisterTypeSet)

        self.direction = GetDirection(type)
        self.vhdlName = self.name + GetSuffix(self.direction)
        self.updatePort()

    def updatePort(self):
        self.port = vhdl.PortList()
        self.port.add(self.vhdlName,self.direction,self.vhdlType)
        if self.externalClear:
            self.port.add(self.clearName+"_i", "in", "std_logic")

        if self.regType == "SplitReadWrite":
            self.inv_direction = InvertDirection(self.direction)
            self.inv_vhdlName = self.name + GetSuffix(self.inv_direction)
            self.port.add(self.inv_vhdlName,self.inv_direction,self.vhdlType)
    

    def addDescription(self, str):
        self.description = str

class RegisterSlice(RegisterBit):
    def __init__(self, name, type, size, init):
        RegisterBit.__init__(self, name, type, init)
        self.size = size
        self.vhdlRange = "(%d downto 0)" % (size-1)
        self.vhdlType = "std_logic_vector" + self.vhdlRange
        if init is None:
            self.init = "(others => '0')"
        else:
            self.init = init
        self.updatePort()

class RegisterWord(dict):
    def __init__(self, name, wordsize, value=None):
        dict.__init__(self)
        self.name = name
        self.wordsize = wordsize
        self.description = ""
        for j in range(self.wordsize):
            self[j] = ["empty"]
        if value is None:
            self.value = "(others => '0')"
        else:
            self.value = value

    def add(self, name, type, start, size, value=None):
        if "empty" in self[start]:
            if size > 1:
                self[start] = RegisterSlice(name, type, size, value)
            else:
                self[start] = RegisterBit(name, type, value)
            for j in range(start+1, start+size):
                if "empty" in self[j]:
                    self[j] = name+"(%d)" % j
                else:
                    print("Reg is already occupied by %s" % self[j].name)
            self[start].byte_enable = byte_enable_vector(start,start+size-1,self.wordsize)
        else:
            print("This reg is already occupied by %s" % self[start].name)

    def byteEnable(self, input):
        pass

    def addDescription(self, str):
        self.description = str


class RegisterList(dict):
    def add(self, number, Register):
        self[number] = Register
        self.description = ""

    def addDescription(self, str):
        self.description = str


class RegisterBank(vhdl.BasicVHDL):
    def __init__(self, entity_name, architecture_name, datasize, RegisterNumber):
        vhdl.BasicVHDL.__init__(self, entity_name, architecture_name)
        self.generate_code = False
        self.reg = RegisterList()
        self.datasize = pow(2,math.ceil(math.log(datasize, 2)))
        self.addr_low = math.log(self.datasize/8,2)
        self.addr_increment = math.ceil(pow(2,self.addr_low))
        self.addrsize = math.ceil(math.log(RegisterNumber, 2) + self.addr_low )
        self.useRecords = False

        #aux files
        self.document = MdUtils(file_name="output/"+entity_name, title='Register Bank: %s' % entity_name)
        self.version = datetime.now().strftime("%Y%m%d_%H%m")

        #Companion Package
        self.pkg = pkgvhdl.PkgVHDL(entity_name + "_pkg")
        self.pkg.library.add("IEEE")
        self.pkg.library["IEEE"].package.add("std_logic_1164")
        self.pkg.library["IEEE"].package.add("numeric_std")
        self.pkg.packageDeclaration.constant.add("package_version_c", "String", "\"%s\"" % self.version)
        self.pkg.packageDeclaration.customTypes.add("regtypes_t","Enumeration",RegisterTypeSet)
        self.pkg.packageDeclaration.customTypes.add("regnames_t","Enumeration")
        
        # Libraries
        self.library.add("IEEE")
        self.library["IEEE"].package.add("std_logic_1164")
        self.library["IEEE"].package.add("numeric_std")
        self.library.add("expert")
        self.library["expert"].package.add("std_logic_expert")
        self.work.add(self.pkg.name)

        # Generics
        self.entity.generic.add("C_S_AXI_ADDR_WIDTH", "integer", str(self.addrsize))
        self.entity.generic.add("C_S_AXI_DATA_WIDTH", "integer", str(self.datasize))

        # Architecture
        # Constant
        self.architecture.constant.add("register_bank_version_c", "String", "\"%s\"" % self.version)
        self.architecture.constant.add("C_S_AXI_ADDR_BYTE", "integer", "(C_S_AXI_DATA_WIDTH/8) + (C_S_AXI_DATA_WIDTH MOD 8)")
        self.architecture.constant.add("C_S_AXI_ADDR_LSB", "integer", str(math.ceil(self.addr_low)))
        self.architecture.constant.add("REG_NUM", "integer", "2**C_S_AXI_ADDR_BYTE")
        # Custom type
        self.architecture.customTypes.add("reg_t", "Array", "REG_NUM-1 downto 0", "std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0)")
        # Signals
        self.architecture.signal.add("awaddr_s", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.architecture.signal.add("awready_s", "std_logic")
        self.architecture.signal.add("wready_s", "std_logic")
        self.architecture.signal.add("wtimeout_sr", "std_logic_vector(15 downto 0)", "( 0 => '1', others=>'0')")
        self.architecture.signal.add("wtimeout_s", "std_logic")

        self.architecture.signal.add("bresp_s", "std_logic_vector(1 downto 0)")
        self.architecture.signal.add("bvalid_s", "std_logic")
        self.architecture.signal.add("bresp_timer_sr", "std_logic_vector(15 downto 0)", "( 0 => '1', others=>'0')")
        self.architecture.signal.add("wtimeout_s", "std_logic")

        self.architecture.signal.add("araddr_s", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.architecture.signal.add("arready_s", "std_logic")

        self.architecture.signal.add("rresp_s", "std_logic_vector(1 downto 0)")
        self.architecture.signal.add("rvalid_s", "std_logic")
        self.architecture.signal.add("rtimeout_sr", "std_logic_vector(15 downto 0)", "( 0 => '1', others=>'0')")
        self.architecture.signal.add("rtimeout_s", "std_logic")

        self.architecture.signal.add("regwrite_s", "reg_t", "(others=>(others=>'0'))")
        self.architecture.signal.add("regread_s", "reg_t", "(others=>(others=>'0'))")
        self.architecture.signal.add("regclear_s", "reg_t", "(others=>(others=>'0'))")
        self.architecture.signal.add("regset_s", "reg_t", "(others=>(others=>'0'))")

        self.architecture.signal.add("regread_en", "std_logic")
        self.architecture.signal.add("regwrite_en", "std_logic")

        self.architecture.bodyCodeHeader.add("assert register_bank_version_c = package_version_c\r\n" + indent(2) + "report \"Package and Register Bank version mismatch.\"\r\n" + indent(2) + "severity warning;\r\n")

        for lines in TemplateCode.splitlines():
            self.architecture.bodyCodeHeader.add(lines)
        
        self._resetPort()
        self._resetArchBodyFooter()

    # PRIVATE API
    def _resetArchBodyFooter(self):
        self.architecture.bodyCodeFooter = vhdl.GenericCodeBlock(1)

    def _resetPort(self):
        self.entity.port = vhdl.PortList()
        self.entity.port.add("S_AXI_ACLK", "in", "std_logic")
        self.entity.port.add("S_AXI_ARESETN", "in", "std_logic")
        self.entity.port.add("S_AXI_AWADDR", "in", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.entity.port.add("S_AXI_AWPROT", "in", "std_logic_vector(2 downto 0)")
        self.entity.port.add("S_AXI_AWVALID", "in", "std_logic")
        self.entity.port.add("S_AXI_AWREADY", "out", "std_logic")
        self.entity.port.add("S_AXI_WDATA", "in", "std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0)")
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


    def _registerPortAdd(self):
        if self.useRecords:
            self.entity.port.add(self.entity.name+"_i","in",self.entity.name+"_i_t")
            self.entity.port.add(self.entity.name+"_o","out",self.entity.name+"_o_t")
        else:
            for index in self.reg:
                register = self.reg[index]
                for field in register:
                    try:
                        register[field].updatePort()
                        for reg_port in register[field].port:
                            self.entity.port.append(register[field].port[reg_port])
                    except:
                        pass

    def _registerConnection(self):
        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "--Register Connection")
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                if isinstance(register[bit], RegisterBit):
                    vectorRange = str(bit)
                    if isinstance(register[bit], RegisterSlice):
                        vectorRange = "%d downto %d" % (bit+register[bit].size-1, bit)
                        register[bit].name = register[bit].name+"(%d downto 0)" % (register[bit].size-1)
                    if "ReadOnly" in register[bit].regType:
                        self.pkg.packageDeclaration.customTypes["regnames_t"].add(register[bit].vhdlName)
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" % (index, vectorRange, register[bit].vhdlName))
                    elif "SplitReadWrite" in register[bit].regType:
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" %
                                                             (register[bit].inv_vhdlName, index, vectorRange))
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" %
                                                             (index, vectorRange, register[bit].vhdlName))
                    elif "ReadWrite" in register[bit].regType:
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" % (register[bit].vhdlName, index, vectorRange))
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= regwrite_s(%d)(%s);" %
                                                             (index, vectorRange, index, vectorRange))
                    elif "Write2Clear" in register[bit].regType:
                        # self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" % (index,vectorRange,register[bit].name))
                        pass
                    elif "Write2Pulse" in register[bit].regType:
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" % (register[bit].vhdlName, index, vectorRange))
        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "")

    def _registerSetConnection(self):
        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "--Set Connection for Write to Clear")
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                if isinstance(register[bit], RegisterBit):
                    vectorRange = str(bit)
                    if isinstance(register[bit], RegisterSlice):
                        vectorRange = "%d downto %d" % (bit+register[bit].size-1, bit)
                    if "Write2Clear" in register[bit].regType:
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regset_s(%d)(%s) <= %s;" % (index, vectorRange, register[bit].vhdlName))
        self.architecture.bodyCodeFooter.add("")

    def _registerClearConnection(self):
            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "--External Clear Connection")
            for index in self.reg:
                register = self.reg[index]
                for bit in register:
                    if isinstance(register[bit], RegisterBit):
                        if self.useRecords:
                            clearname = register[bit].clearName
                        else:
                            clearname = register[bit].clearName + "_i"
                        defaultvalue = "'1'"
                        elsevalue = "'0'"
                        vectorRange = str(bit)
                        if isinstance(register[bit], RegisterSlice):
                            vectorRange = "%d downto %d" % (bit+register[bit].size-1, bit)
                            tmp = register[bit].vhdlRange.replace("(","")
                            tmp = tmp.replace(")","")
                            defaultvalue = "(%s => '1')" % tmp
                            elsevalue = "(%s => '0')" % tmp
                        if "Write2Clear" in register[bit].regType:
                            elsevalue = "regwrite_s(%d)(%s)" % (index, vectorRange)
                        if register[bit].externalClear:
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regclear_s(%d)(%s) <= %s when %s = '1' else %s;" %
                                                                (index, vectorRange, defaultvalue, clearname, elsevalue))
                        elif "Write2Clear" in register[bit].regType:
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regclear_s(%d)(%s) <= %s;" % (index, vectorRange, elsevalue) )


    def _generate(self):
        if (not self.generate_code):
            self._resetPort()
            self._resetArchBodyFooter
            self._registerPortAdd()
            self._registerConnection()
            self._registerSetConnection()
            self._registerClearConnection()
            self.pkg.packageDeclaration.component.append(self.object())
            self.generate_code = True


    # PUBLIC API
    def add(self, number, name):
        self.generate_code = False
        self.reg.add(number, RegisterWord(name, self.datasize))


    def SetPortAsRecord(self):
        self.generate_code = False
        self.useRecords = True
        out_record_name = self.entity.name+"_o_t"
        in_record_name = self.entity.name+"_i_t"
        self.pkg.packageDeclaration.customTypes.add(out_record_name, "Record")
        self.pkg.packageDeclaration.customTypes.add(in_record_name, "Record")
        for index in self.reg:
            register = self.reg[index]
            for element in register:
                try:
                    for j in register[element].port:
                        if register[element].externalClear:
                            self.pkg.packageDeclaration.customTypes[in_record_name].add(register[element].clearName,register[element].vhdlType)
                            self.reg[index][element].clearName = self.entity.name+"_i."+register[element].clearName
                        
                        if "SplitReadWrite" in register[element].regType:
                            self.pkg.packageDeclaration.customTypes[out_record_name].add(register[element].name,register[element].vhdlType)
                            self.pkg.packageDeclaration.customTypes[in_record_name].add(register[element].name,register[element].vhdlType)
                            self.reg[index][element].vhdlName = self.entity.name+"_i."+register[element].name
                            self.reg[index][element].inv_vhdlName = self.entity.name+"_o."+register[element].name
                        elif "out" in register[element].direction:
                            self.pkg.packageDeclaration.customTypes[out_record_name].add(register[element].name,register[element].vhdlType)
                            self.reg[index][element].vhdlName = self.entity.name+"_o."+register[element].name
                        else:
                            self.pkg.packageDeclaration.customTypes[in_record_name].add(register[element].name,register[element].vhdlType)
                            self.reg[index][element].vhdlName = self.entity.name+"_i."+register[element].name
                except:
                    pass
        

    def code(self):
        self._generate()
        return vhdl.BasicVHDL.code(self)

    def write_package(self):
        self.pkg.write_file()

    def write_document(self):
        self._generate()

        if (not os.path.exists("output")):
            os.makedirs("output")

        self.document.new_header(1, "Details")
        self.document.new_line("Data Width: %d" % self.datasize)
        self.document.new_line("Number of registers: %d" % len(self.reg))
        self.document.new_line("Version: v%s" % self.version)
        self.document.new_line("Register Bank auto-generated using the hdltools/regbank_gen.py")
        self.document.new_line()
        self.document.new_header(1, "List of Registers")
        self.document.new_line()
        for index in self.reg:
            register = self.reg[index]
            self.document.new_header(2, "Register %d: %s" % (index, register.name))
            self.document.new_line("Address: BASE + 0x%x" % index)
            if (register.description):
                self.document.new_line("Description: %s" % register.description)
            self.document.new_line()
            list_of_strings = ["Bit", "Field", "Type", "Reset", "Description"]
            numOfRows = 1
            for bit in register:
                if isinstance(register[bit], RegisterBit):
                    numOfRows = numOfRows + 1
                    if register[bit].size > 1:
                        range = "%d-%d" % (bit+register[bit].size-1, bit)
                    else:
                        range = "%d" % (bit)
                    field = register[bit].radix
                    type = register[bit].regType
                    # Default value
                    init = register[bit].init
                    if init == "(others => '0')" or init == "'0'":
                        init = "0x0"
                    elif init == "'1'":
                        init = "1"
                    else:
                        init = "0" + init.replace("\"", "")
                    # decription
                    description = register[bit].description
                    list_of_strings.extend([range, field, type, init, description])
            self.document.new_table(columns=5, rows=numOfRows, text=list_of_strings, text_align='center')
        self.document.new_line()
        self.document.new_line("hdltools available at https://github.com/rftafas/hdltools.")
        self.document.create_md_file()

    def write_header(self):
        self._generate()
        if (not os.path.exists("output")):
            os.makedirs("output")

        header_code = ""
        header_code = header_code + "#ifndef %s_H\n\r" % (self.entity.name.upper())
        header_code = header_code + "#define %s_H\n\r" % (self.entity.name.upper())

        header_code = header_code + "\n\r"
        header_code = header_code + "/*This auto-generated header file was created using hdltools. File version:*/\n\r"
        header_code = header_code + "#define %s_VERSION \"%s\"\n\r" % (self.entity.name.upper(), self.version)
        header_code = header_code + "\n\r"

        for index in self.reg:
            register = self.reg[index]
            header_code = header_code + "/*Register %s address */\n\r" % register.name
            header_code = header_code + "#define %s_OFFSET 0x%x\n\r" % (register.name.upper(), index)
            for bit in register:
                if isinstance(register[bit], RegisterBit):
                    header_code = header_code + "/*Register %s field %s */\n\r" % (register.name, register[bit].radix)
                    fieldName = register.name.upper() + "_" + register[bit].radix.upper()
                    header_code = header_code + "#define %s_FIELD_OFFSET %d\n\r" % (fieldName, bit)
                    header_code = header_code + "#define %s_FIELD_WIDTH %d\n\r" % (fieldName, register[bit].size)
                    # compute field mask
                    mask = 0
                    for i in range(bit, bit + register[bit].size):
                        mask = mask + 2**i
                    header_code = header_code + "#define %s_FIELD_MASK %s\n\r" % (fieldName, hex(mask))
                    # Field default value
                    if register[bit].init == "(others => '0')" or register[bit].init == "'0'":
                        header_code = header_code + "#define %s_RESET %s\n\r" % (fieldName, "0x0")
                    else:
                        header_code = header_code + "#define %s_RESET 0%s\n\r" % (fieldName, register[bit].init.replace("\"", ""))
            header_code = header_code + "\n\r"

        header_code = header_code + "\n\r"

        output_file_name = "output/"+self.entity.name+".h"
        # to do: check if file exists. If so, emit a warning and
        # check if must clear it.
        output_file = open(output_file_name, "w+")
        for line in header_code:
            output_file.write(line)

        output_file.close()

    def write_testbench(self):
        self._generate()
        testbench = vhdl.BasicVHDL(self.entity.name+"_tb","simulation")
        testbench.entity.generic.add("runner_cfg", "string", "")
        testbench.entity.generic.add("run_time", "integer", "100")
        testbench.library = self.library
        testbench.library.add("std")
        testbench.library["std"].package.add("textio")
        testbench.library.add("vunit_lib")
        testbench.library["vunit_lib"].context.add("vunit_context")
        testbench.library["vunit_lib"].context.add("vc_context")
        testbench.work.add(self.pkg.name)

        for element in self.entity.generic:
            testbench.architecture.constant.add(element,self.entity.generic[element].type,self.entity.generic[element].value)
        
        testbench.architecture.constant.add("axi_handle","bus_master_t","new_bus(data_length => C_S_AXI_DATA_WIDTH, address_length => C_S_AXI_ADDR_WIDTH)")
        testbench.architecture.constant.add("addr_increment_c","integer",str(self.addr_increment))
        
        for port in self.entity.port:
            testbench.architecture.signal.add(port,self.entity.port[port].type)
        # set starting value to clock. All other signals should be handled by reset.
        testbench.architecture.signal["S_AXI_ACLK"].value = "'0'"


        testbench.architecture.instances.add("entity vunit_lib.axi_lite_master","axi_master_u")
        testbench.architecture.instances["axi_master_u"].generic.add("bus_handle","axi_handle")

        tmp_j = 0
        for port in self.entity.port:
            if tmp_j < len(vunitPort):
                testbench.architecture.instances["axi_master_u"].port.add(vunitPort[tmp_j],port)
                tmp_j = tmp_j + 1


        testbench.architecture.instances.append(self.instanciation("dut_u"))
        read_only = vhdl.GenericCodeBlock(4)
        read_write = vhdl.GenericCodeBlock(4)
        split_read_write = vhdl.GenericCodeBlock(4)
        write_to_clear = vhdl.GenericCodeBlock(4)
        #adds a random value to all readable registers
        for index in self.reg:
            register = self.reg[index]
            reg_address = index * self.addr_increment
            for field in register:
                if not (isinstance(register[field],RegisterBit) or isinstance(register[field],RegisterSlice)):
                    break

                if register[field].size == 1:
                    tb_value = random_bit()
                    vector_location = "(%s)" % field
                    all_one = "'1'"
                    all_zero = "'0'"

                else:
                    tb_value = random_vector(register[field].size)
                    vector_location = "(%s downto %s)" % (register[field].size + field - 1, field)
                    all_one = "(others=>'1')"
                    all_zero = "(others=>'0')"

                if register[field].regType == "ReadOnly":
                    testbench.architecture.bodyCodeFooter.add(vhdl.indent(1) + "--Read Only: %s;" % register[field].vhdlName)
                    testbench.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= %s;" % (register[field].vhdlName, tb_value))
                    read_only.add(vhdl.indent(1) + "--Testing %s" % register[field].vhdlName)
                    read_only.add(vhdl.indent(1) + "read_bus(net,axi_handle,%d,rdata_v);" % reg_address )
                    read_only.add(vhdl.indent(1) + "check_equal(rdata_v%s,%s,result(\"Test Read: %s.\"));" % ( vector_location, register[field].vhdlName, register[field].vhdlName ))                        

                if register[field].regType == "ReadWrite":
                    tb_value = random_vector(self.datasize)
                    read_write.add(vhdl.indent(1) + "--Testing %s" % register[field].vhdlName)
                    read_write.add(vhdl.indent(1) + "rdata_v := %s;" % tb_value)
                    read_write.add(vhdl.indent(1) + "write_bus(net,axi_handle,%d,rdata_v,%s);" % (reg_address, register[field].byte_enable) )
                    read_write.add(vhdl.indent(1) + "read_bus(net,axi_handle,%d,rdata_v);" % reg_address )
                    read_write.add(vhdl.indent(1) + "check_equal(%s,rdata_v%s,result(\"Test Readback and Port value: %s.\"));" % ( register[field].vhdlName, vector_location, register[field].vhdlName ))                        

                if register[field].regType == "SplitReadWrite":
                    testbench.architecture.bodyCodeFooter.add(vhdl.indent(1) + "--Split Read and Write: %s;" % register[field].vhdlName)
                    testbench.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= %s;" % (register[field].vhdlName, tb_value))
                    split_read_write.add(vhdl.indent(1) + "--Testing %s" % register[field].vhdlName)
                    split_read_write.add(vhdl.indent(1) + "read_bus(net,axi_handle,%d,rdata_v);" % reg_address )
                    split_read_write.add(vhdl.indent(1) + "check_equal(rdata_v%s,%s,result(\"Test Read: %s.\"));" % ( vector_location, register[field].vhdlName, register[field].vhdlName ))                        
                    tb_value = random_vector(self.datasize)
                    split_read_write.add(vhdl.indent(1) + "--Testing %s" % register[field].inv_vhdlName)
                    split_read_write.add(vhdl.indent(1) + "rdata_v := %s;" % tb_value )
                    split_read_write.add(vhdl.indent(1) + "write_bus(net,axi_handle,%d,rdata_v,%s);" % (reg_address, register[field].byte_enable) )
                    split_read_write.add(vhdl.indent(1) + "wait for 1 us;")
                    split_read_write.add(vhdl.indent(1) + "check_equal(%s,rdata_v%s,result(\"Test Read: %s.\"));" % ( register[field].inv_vhdlName, vector_location, register[field].inv_vhdlName ))                        

                if register[field].regType == "Write2Clear":
                    write_to_clear.add(vhdl.indent(1) + "--Testing %s: Set to %s" % (register[field].vhdlName, all_one) )
                    write_to_clear.add(vhdl.indent(1) + "%s <= %s;" % (register[field].vhdlName, all_one))
                    write_to_clear.add(vhdl.indent(1) + "wait until rising_edge(S_AXI_ACLK);")
                    write_to_clear.add(vhdl.indent(1) + "%s <= %s;" % (register[field].vhdlName, all_zero))
                    write_to_clear.add(vhdl.indent(1) + "wait until rising_edge(S_AXI_ACLK);")
                    write_to_clear.add(vhdl.indent(1) + "read_bus(net,axi_handle,%d,rdata_v);" % reg_address )
                    write_to_clear.add(vhdl.indent(1) + "check(rdata_v%s = %s,result(\"Test Read Ones: %s.\"));" % ( vector_location, tb_value.replace('0','1'), register[field].vhdlName ))                        
                    write_to_clear.add(vhdl.indent(1) + "rdata_v := (others=>'0');" )
                    write_to_clear.add(vhdl.indent(1) + "rdata_v%s := %s;" % (vector_location, all_one) )
                    write_to_clear.add(vhdl.indent(1) + "write_bus(net,axi_handle,%d,rdata_v,%s);" % (reg_address, register[field].byte_enable) )
                    write_to_clear.add(vhdl.indent(1) + "read_bus(net,axi_handle,%d,rdata_v);" % reg_address )
                    write_to_clear.add(vhdl.indent(1) + "check(rdata_v%s = %s,result(\"Test Read Zeroes: %s.\"));" % ( vector_location, tb_value.replace('1','0'), register[field].vhdlName ))                        

        read_only.add(vhdl.indent(1) + "check_passed(result(\"Read Out Test Pass.\"));")
        read_write.add(vhdl.indent(1) + "check_passed(result(\"Read and Write Test Pass.\"));")
        split_read_write.add(vhdl.indent(1) + "check_passed(result(\"Split Read Write Test Pass.\"));")
        write_to_clear.add(vhdl.indent(1) + "check_passed(result(\"Write to Clear Test Pass.\"));")


        new_tb_code = testBenchCode.replace("--read_only_tag",read_only.code())
        new_tb_code = new_tb_code.replace("--read_write_tag",read_write.code())
        new_tb_code = new_tb_code.replace("--split_read_write_tag",split_read_write.code())
        new_tb_code = new_tb_code.replace("--write_to_clear_tag",write_to_clear.code())




        testbench.architecture.bodyCodeHeader.add(new_tb_code)

        testbench.write_file()


    def write_file(self):
        self._generate()
        self.pkg.write_file()
        vhdl.BasicVHDL.write_file(self)
        return True


if __name__ == '__main__':
    #This is one example for a register bank to serve as base for learning purposes.
    #It is not related to any core, block or nwither it have any meaning. Just a 
    #bunch of loose registers.

    # first we declare a register bank.
    # It is a 32 bit register with 8 possible positions.
    # we named the architecture "RTL".
    myregbank = RegisterBank("myregbank", "rtl", 32, 8)

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

    myregbank.write_document()
    myregbank.write_header()
    myregbank.write_testbench()
    myregbank.write_file()
    