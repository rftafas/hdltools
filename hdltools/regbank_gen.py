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
import hdltools.vhdl_gen as vhdl
import hdltools.pkgvhdl_gen as pkgvhdl
import math
import random
from mdutils.mdutils import MdUtils

indent = vhdl.indent
RegisterTypeSet = {"ReadOnly", "ReadWrite", "SplitReadWrite", "Write2Clear", "Write2Pulse"}

vunitPort = {
    "aclk" : "S_AXI_ACLK",
    "--areset_n" : "S_AXI_ARESETN",
    "awaddr" : " S_AXI_AWADDR",
    "--awprot" : "S_AXI_AWPROT",
    "awvalid" : "S_AXI_AWVALID",
    "awready" : "S_AXI_AWREADY",
    "wdata" : "S_AXI_WDATA",
    "wstrb" : "S_AXI_WSTRB",
    "wvalid" : "S_AXI_WVALID",
    "wready" : "S_AXI_WREADY",
    "bresp" : "S_AXI_BRESP",
    "bvalid" : "S_AXI_BVALID",
    "bready" : "S_AXI_BREADY",
    "araddr" : "S_AXI_ARADDR",
    "--arprot" : "S_AXI_ARPROT",
    "arvalid" : "S_AXI_ARVALID",
    "arready" : "S_AXI_ARREADY",
    "rdata" : "S_AXI_RDATA",
    "rresp" : "S_AXI_RRESP",
    "rvalid" : "S_AXI_RVALID",
    "rready" : "S_AXI_RREADY"
}


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
        elsif run("Write to Pulse Test") then
--write_to_pulse_tag
        elsif run("External Clear Test") then
--external_clear_tag
        end if;
    end loop;
    test_runner_cleanup(runner); -- Simulation ends here
end process;

test_runner_watchdog(runner, 101 us);

"""

templateScript = '''
from os.path import join, dirname
import sys

try:
    from vunit import VUnit
except:
    print("Please, intall vunit_hdl with 'pip install vunit_hdl'")
    print("Also, make sure to have either GHDL or Modelsim installed.")
    exit()


root = dirname(__file__)

vu = VUnit.from_argv()
vu.add_osvvm()
vu.add_verification_components()

try:
    expert = vu.add_library("expert")
    expert.add_source_files(join(root, "stdexpert/src/*.vhd"))
except:
    print("Missing std_logic_expert. Please, run:")
    print("git clone https://github.com/rftafas/stdexpert.git")
    exit()

lib = vu.add_library("<name>")
lib.add_source_files(join(root, "./*.vhd"))
test_tb = lib.entity("<name>_tb")
test_tb.scan_tests_from_file(join(root, "<name>_tb.vhd"))

test_tb.add_config(
    name="run_time",
    generics=dict(run_time=100)
)

vu.main()
'''

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
                    lock_v := '0';
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
        variable loc_addr : INTEGER;
    begin
        if S_AXI_ARESETN = '0' then
            regwrite_s <= (others => (others => '0'));
            write_activity_s <= (others => (others => '0'));
        elsif rising_edge(S_AXI_ACLK) then
            loc_addr := to_integer(awaddr_s(C_S_AXI_ADDR_WIDTH - 1 downto C_S_AXI_ADDR_LSB));
            write_activity_s <= (others => (others => '0'));
            if regwrite_en = '1' then
                for k in C_S_AXI_DATA_WIDTH/8 - 1 downto 0 loop
                    if S_AXI_WSTRB(k) = '1' then
                        regwrite_s(loc_addr)( (k+1)*8-1 downto 8*k ) <= S_AXI_WDATA( (k+1)*8-1 downto 8*k );
                        write_activity_s(loc_addr)( (k+1)*8-1 downto 8*k ) <= (others => '1');
                    end if;
                end loop;
            else
                for j in regwrite_s'range loop
                    for k in C_S_AXI_DATA_WIDTH - 1 downto 0 loop
                        if regclear_s(j)(k) = '1' then
                            regwrite_s(j)(k) <= '0';
                        end if;
                    end loop;
                end loop;
            end if;
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
                read_activity_s(loc_addr) <= (others=>'1');
                S_AXI_RDATA  <= reg_tmp(loc_addr);
            else
                read_activity_s(loc_addr) <= (others=>'0');
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

class auxInputBit:
    def __init__(self, name):
        self.name = name
        self.vhdlName = name + "_i"

class auxOutputBit:
    def __init__(self, name):
        self.name = name
        self.vhdlName = name + "_o"

class RegisterBit:
    def __init__(self, name, type, init):
        self.name = name
        self.activitySignal = False
        self.actionReadName  = self.name+"_rd_act"
        self.actionWriteName = self.name+"_wr_act"
        self.vhdlType = "std_logic"
        self.size = 1
        self.vhdlRange = "1"
        self.relativeLocation = "0"
        self.description = ""

        self.activitySignal = False
        self.actionRead  = auxOutputBit(name+"_rd_act")
        self.actionWrite = auxOutputBit(name+"_wr_act")

        self.externalClear = False
        self.clear = auxInputBit(name+"_clr")


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

        self.inv_direction = InvertDirection(self.direction)
        self.inv_vhdlName = self.name + GetSuffix(self.inv_direction)

    def convertRecord(self,entity_name):
        self.vhdlName = entity_name + GetSuffix(self.direction) + "." + self.name
        self.inv_vhdlName = entity_name + GetSuffix(self.inv_direction) + "." + self.name
        self.clear.vhdlName = entity_name + "_i." + self.clear.name
        self.actionRead.vhdlName  = entity_name + "_o." + self.actionRead.name
        self.actionWrite.vhdlName  = entity_name + "_o." + self.actionWrite.name


    def addDescription(self, str):
        self.description = str

class RegisterSlice(RegisterBit):
    def __init__(self, name, type, size, init):
        RegisterBit.__init__(self, name, type, init)
        self.size = size
        self.vhdlRange = "(%d downto 0)" % (size-1)
        self.vhdlName = self.vhdlName
        self.inv_vhdlName = self.inv_vhdlName

        self.vhdlType = "std_logic_vector" + self.vhdlRange
        if init is None:
            self.init = "(others => '0')"
        else:
            self.init = init

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
                self[start].relativeLocation = "%d downto %d" % (start+size-1, start)
            else:
                self[start] = RegisterBit(name, type, value)
                self[start].relativeLocation = "%d" % (start)

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
        self.architecture.constant.add("REG_NUM", "integer", "2**(C_S_AXI_ADDR_WIDTH-C_S_AXI_ADDR_LSB)")
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

        self.architecture.signal.add("read_activity_s", "reg_t", "(others=>(others=>'0'))")
        self.architecture.signal.add("write_activity_s", "reg_t", "(others=>(others=>'0'))")

        self.architecture.signal.add("regread_en", "std_logic")
        self.architecture.signal.add("regwrite_en", "std_logic")

        self.architecture.bodyCodeHeader.add("assert register_bank_version_c = package_version_c\r\n" + indent(2) + "report \"Package and Register Bank version mismatch.\"\r\n" + indent(2) + "severity warning;\r\n")

        for lines in TemplateCode.splitlines():
            self.architecture.bodyCodeHeader.add(lines)

        self._resetPort()
        self._resetArchBodyFooter()

    # PRIVATE API
    def _resetArchBodyFooter(self):
        self.architecture.bodyCodeFooter = vhdl.GenericCodeBlock()

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
        for local_port in list(self.entity.port.keys()):
            self.entity.port[local_port].assign(local_port)

    def _registerPortAdd(self):
        if self.useRecords:
            self.entity.port.add(self.entity.name+"_i","in",self.entity.name+"_i_t")
            self.entity.port[self.entity.name+"_i"].assign(self.entity.name+"_i")
            self.entity.port.add(self.entity.name+"_o","out",self.entity.name+"_o_t")
            self.entity.port[self.entity.name+"_o"].assign(self.entity.name+"_o")

        else:
            for register_num, register_word in self.reg.items():
                for index, register in register_word.items():
                    if isinstance(register,RegisterBit) or isinstance(register,RegisterSlice):
                        self.entity.port.add(register.vhdlName,register.direction,register.vhdlType)
                        self.entity.port[register.vhdlName].assign(register.vhdlName)


                        if register.regType == "SplitReadWrite":
                            self.entity.port.add(register.inv_vhdlName,register.inv_direction,register.vhdlType)
                            self.entity.port[register.inv_vhdlName].assign(register.inv_vhdlName)

                        if register.externalClear:
                            self.entity.port.add(register.clear.vhdlName, "in", "std_logic")
                            self.entity.port[register.clear.vhdlName].assign(register.clear.vhdlName)

                        if register.activitySignal:
                            self.entity.port.add(register.actionRead.vhdlName,"out","std_logic")
                            self.entity.port[register.actionRead.vhdlName].assign(register.actionRead.vhdlName)
                            self.entity.port.add(register.actionWrite.vhdlName,"out","std_logic")
                            self.entity.port[register.actionWrite.vhdlName].assign(register.actionWrite.vhdlName)


    def _registerConnection(self):
        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "--Register Connection")
        for register_num, register_word in self.reg.items():
            for index, register in register_word.items():
                if isinstance(register, RegisterBit) or isinstance(register, RegisterSlice):
                    if "ReadOnly" in register.regType:
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" % (register_num, register.relativeLocation, register.vhdlName))

                    elif "SplitReadWrite" in register.regType:
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" %
                                                             (register.inv_vhdlName, register_num, register.relativeLocation))
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" %
                                                             (register_num, register.relativeLocation, register.vhdlName))

                    elif "ReadWrite" in register.regType:
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" % (register.vhdlName, register_num, register.relativeLocation))
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= regwrite_s(%d)(%s);" %
                                                             (register_num, register.relativeLocation, register_num, register.relativeLocation))
                    elif "Write2Clear" in register.regType:
                        # self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" % (register_num,register.relativeLocation,register.name))
                        pass

                    elif "Write2Pulse" in register.regType:
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" % (register.vhdlName, register_num, register.relativeLocation))

        self.architecture.bodyCodeFooter.add("")

    def _registerSetConnection(self):
        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "--Set Connection for Write to Clear")
        for reg_num, register_word in self.reg.items():
            for index, register in register_word.items():
                if isinstance(register, RegisterBit) or isinstance(register, RegisterSlice):
                    if register.regType == "Write2Clear":
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regset_s(%d)(%s) <= %s;" % (reg_num, register.relativeLocation, register.vhdlName))
        self.architecture.bodyCodeFooter.add("")


    def _registerClearConnection(self):
        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "--External Clear Connection")
        for register_num, register_word in self.reg.items():
            for index, register in register_word.items():
                if (isinstance(register,RegisterBit) or isinstance(register,RegisterSlice)):

                    if register.size == 1:
                        defaultvalue = "'1'"
                        elsevalue = "'0'"
                    else:
                        defaultvalue = "(%s => '1')" % register.relativeLocation
                        elsevalue = "(%s => '0')" % register.relativeLocation

                    if ( register.regType == "Write2Clear" or register.regType == "Write2Pulse"):
                        elsevalue = "regwrite_s(%d)(%s)" % (register_num, register.relativeLocation)

                    if register.externalClear:
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regclear_s(%d)(%s) <= %s when %s = '1' else %s;" %
                                                            (register_num, register.relativeLocation, defaultvalue, register.clear.vhdlName, elsevalue))

                    elif ( register.regType == "Write2Clear" or register.regType == "Write2Pulse"):
                        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regclear_s(%d)(%s) <= %s;" % (register_num, register.relativeLocation, elsevalue) )

        self.architecture.bodyCodeFooter.add("")

    def _registerActionConnection(self):
            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "--Register Activity Signals")
            for register_num, register_word in self.reg.items():
                for index, register in register_word.items():
                    if (isinstance(register,RegisterBit) or isinstance(register,RegisterSlice)):
                        if register.activitySignal:
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + register.actionRead.vhdlName  + " <= read_activity_s(%d)(%s);" % (register_num, index) )
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + register.actionWrite.vhdlName + " <= write_activity_s(%d)(%s);" % (register_num, index) )

    def _generate(self):
        if (not self.generate_code):
            self._resetPort()
            self._resetArchBodyFooter()
            self._registerPortAdd()
            self._registerConnection()
            self._registerSetConnection()
            self._registerClearConnection()
            self._registerActionConnection()
            self.pkg.packageDeclaration.component.append(self.dec_object())
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
        for reg_num, register_word in self.reg.items():
            for index, register in register_word.items():
                if (isinstance(register,RegisterBit) or isinstance(register,RegisterSlice)):

                    register.convertRecord(self.entity.name)

                    if register.externalClear:
                        self.pkg.packageDeclaration.customTypes[in_record_name].add(register.clear.name,"std_logic")

                    if register.activitySignal:
                        self.pkg.packageDeclaration.customTypes[out_record_name].add(register.actionRead.name,"std_logic")
                        self.pkg.packageDeclaration.customTypes[out_record_name].add(register.actionWrite.name,"std_logic")

                    if "SplitReadWrite" in register.regType:
                        self.pkg.packageDeclaration.customTypes[out_record_name].add(register.name,register.vhdlType)
                        self.pkg.packageDeclaration.customTypes[in_record_name].add(register.name,register.vhdlType)

                    elif "out" in register.direction:
                        self.pkg.packageDeclaration.customTypes[out_record_name].add(register.name,register.vhdlType)
                    else:
                        self.pkg.packageDeclaration.customTypes[in_record_name].add(register.name,register.vhdlType)


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
                    field = register[bit].name
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
                    header_code = header_code + "/*Register %s field %s */\n\r" % (register.name, register[bit].name)
                    fieldName = register.name.upper() + "_" + register[bit].name.upper()
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

        for index, generic in self.entity.generic.items():
            testbench.architecture.constant.add(index,generic.type,generic.value)

        testbench.architecture.constant.add("axi_handle","bus_master_t","new_bus(data_length => C_S_AXI_DATA_WIDTH, address_length => C_S_AXI_ADDR_WIDTH)")
        testbench.architecture.constant.add("addr_increment_c","integer",str(self.addr_increment))

        for port in self.entity.port:
            testbench.architecture.signal.add(port,self.entity.port[port].type)
        # set starting value to clock. All other signals should be handled by reset.
        testbench.architecture.signal["S_AXI_ACLK"].value = "'0'"


        testbench.architecture.instances.add("axi_master_u","entity vunit_lib.axi_lite_master")
        testbench.architecture.instances["axi_master_u"].generic.add("bus_handle","","axi_handle")

        for local_port in list(vunitPort.keys()):
            testbench.architecture.instances["axi_master_u"].port.add(local_port,"","")
            testbench.architecture.instances["axi_master_u"].port[local_port].assign(vunitPort[local_port])

        testbench.architecture.instances.append(self.instanciation("dut_u"))
        read_only = vhdl.GenericCodeBlock()
        read_write = vhdl.GenericCodeBlock()
        split_read_write = vhdl.GenericCodeBlock()
        write_to_clear = vhdl.GenericCodeBlock()
        write_to_pulse = vhdl.GenericCodeBlock()
        external_clear = vhdl.GenericCodeBlock()

        for reg_number, register_word in self.reg.items():
            reg_address = reg_number * self.addr_increment

            for index, register in register_word.items():
                if not (isinstance(register,RegisterBit) or isinstance(register,RegisterSlice)):
                    continue

                if register.size == 1:
                    tb_value = random_bit()
                    vector_location = "(%s)" % index
                    all_one = "'1'"
                    all_zero = "'0'"

                else:
                    tb_value = random_vector(register.size)
                    vector_location = "(%s downto %s)" % (register.size + index - 1, index)
                    all_one = "(others=>'1')"
                    all_zero = "(others=>'0')"

                if register.regType == "ReadOnly":
                    testbench.architecture.bodyCodeFooter.add(vhdl.indent(1) + "--Read Only: %s;" % register.vhdlName)
                    testbench.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= %s;" % (register.vhdlName, tb_value))
                    read_only.add(vhdl.indent(1) + "--Testing %s" % register.vhdlName)
                    read_only.add(vhdl.indent(1) + "read_bus(net,axi_handle,%d,rdata_v);" % reg_address )
                    read_only.add(vhdl.indent(1) + "check_equal(rdata_v%s,%s,result(\"Test Read: %s.\"));" % ( vector_location, register.vhdlName, register.vhdlName ))

                if register.regType == "ReadWrite":
                    tb_value = random_vector(self.datasize)
                    read_write.add(vhdl.indent(1) + "--Testing %s" % register.vhdlName)
                    read_write.add(vhdl.indent(1) + "rdata_v := %s;" % tb_value)
                    read_write.add(vhdl.indent(1) + "write_bus(net,axi_handle,%d,rdata_v,%s);" % (reg_address, register.byte_enable) )
                    read_write.add(vhdl.indent(1) + "read_bus(net,axi_handle,%d,rdata_v);" % reg_address )
                    read_write.add(vhdl.indent(1) + "check_equal(%s,rdata_v%s,result(\"Test Readback and Port value: %s.\"));" % ( register.vhdlName, vector_location, register.vhdlName ))

                if register.regType == "SplitReadWrite":
                    testbench.architecture.bodyCodeFooter.add(vhdl.indent(1) + "--Split Read and Write: %s;" % register.vhdlName)
                    testbench.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= %s;" % (register.vhdlName, tb_value))
                    split_read_write.add(vhdl.indent(1) + "--Testing %s" % register.vhdlName)
                    split_read_write.add(vhdl.indent(1) + "read_bus(net,axi_handle,%d,rdata_v);" % reg_address )
                    split_read_write.add(vhdl.indent(1) + "check_equal(rdata_v%s,%s,result(\"Test Read: %s.\"));" % ( vector_location, register.vhdlName, register.vhdlName ))
                    tb_value = random_vector(self.datasize)
                    split_read_write.add(vhdl.indent(1) + "--Testing %s" % register.inv_vhdlName)
                    split_read_write.add(vhdl.indent(1) + "rdata_v := %s;" % tb_value )
                    split_read_write.add(vhdl.indent(1) + "write_bus(net,axi_handle,%d,rdata_v,%s);" % (reg_address, register.byte_enable) )
                    split_read_write.add(vhdl.indent(1) + "wait for 1 us;")
                    split_read_write.add(vhdl.indent(1) + "check_equal(%s,rdata_v%s,result(\"Test Read: %s.\"));" % ( register.inv_vhdlName, vector_location, register.inv_vhdlName ))

                if register.regType == "Write2Clear":
                    write_to_clear.add(vhdl.indent(1) + "--Testing %s: Set to %s" % (register.vhdlName, all_one) )
                    write_to_clear.add(vhdl.indent(1) + "%s <= %s;" % (register.vhdlName, all_one))
                    write_to_clear.add(vhdl.indent(1) + "wait until rising_edge(S_AXI_ACLK);")
                    write_to_clear.add(vhdl.indent(1) + "%s <= %s;" % (register.vhdlName, all_zero))
                    write_to_clear.add(vhdl.indent(1) + "wait until rising_edge(S_AXI_ACLK);")
                    write_to_clear.add(vhdl.indent(1) + "read_bus(net,axi_handle,%d,rdata_v);" % reg_address )
                    write_to_clear.add(vhdl.indent(1) + "check(rdata_v%s = %s,result(\"Test Read Ones: %s.\"));" % ( vector_location, tb_value.replace('0','1'), register.vhdlName ))
                    write_to_clear.add(vhdl.indent(1) + "rdata_v := (others=>'0');" )
                    write_to_clear.add(vhdl.indent(1) + "rdata_v%s := %s;" % (vector_location, all_one) )
                    write_to_clear.add(vhdl.indent(1) + "write_bus(net,axi_handle,%d,rdata_v,%s);" % (reg_address, register.byte_enable) )
                    write_to_clear.add(vhdl.indent(1) + "read_bus(net,axi_handle,%d,rdata_v);" % reg_address )
                    write_to_clear.add(vhdl.indent(1) + "check(rdata_v%s = %s,result(\"Test Read Zeroes: %s.\"));" % ( vector_location, tb_value.replace('1','0'), register.vhdlName ))

                if register.regType == "Write2Pulse":
                    write_to_pulse.add(vhdl.indent(1) + "--Testing %s" % register.vhdlName)
                    write_to_pulse.add(vhdl.indent(1) + "rdata_v%s := %s;" % (vector_location, all_one) )
                    write_to_pulse.add(vhdl.indent(1) + "write_bus(net,axi_handle,%d,rdata_v,%s);" % (reg_address, register.byte_enable) )
                    write_to_pulse.add(vhdl.indent(1) + "wait until %s = %s;" % (register.vhdlName, tb_value.replace("0","1")) )

        read_only.add(vhdl.indent(1) + "check_passed(result(\"Read Out Test Pass.\"));")
        read_write.add(vhdl.indent(1) + "check_passed(result(\"Read and Write Test Pass.\"));")
        split_read_write.add(vhdl.indent(1) + "check_passed(result(\"Split Read Write Test Pass.\"));")
        write_to_clear.add(vhdl.indent(1) + "check_passed(result(\"Write to Clear Test Pass.\"));")
        write_to_pulse.add(vhdl.indent(1) + "check_passed(result(\"Write to Pulse Test Pass.\"));")
        external_clear.add(vhdl.indent(1) + "check_passed(result(\"External Clear Test Pass.\"));")

        new_tb_code = testBenchCode.replace("--read_only_tag",read_only.code(4))
        new_tb_code = new_tb_code.replace("--read_write_tag",read_write.code(4))
        new_tb_code = new_tb_code.replace("--split_read_write_tag",split_read_write.code(4))
        new_tb_code = new_tb_code.replace("--write_to_clear_tag",write_to_clear.code(4))
        new_tb_code = new_tb_code.replace("--write_to_pulse_tag",write_to_pulse.code(4))
        new_tb_code = new_tb_code.replace("--external_clear_tag",external_clear.code(4))

        testbench.architecture.bodyCodeHeader.add(new_tb_code)

        testbench.write_file()


    def write_script(self):
        tmpScript = templateScript.replace("<name>",self.entity.name)

        if (not os.path.exists("output")):
            os.makedirs("output")
        output_file_name = "output/"+self.entity.name+"_run.py"
        # to do: check if file exists. If so, emit a warning and
        # check if must clear it.
        output_file = open(output_file_name, "w+")
        for line in tmpScript:
            output_file.write(line)

        output_file.close()

    def write_file(self):
        self._generate()
        vhdl.BasicVHDL.write_file(self)
        return True

    def __call__(self):
        self.write_file()
        self.write_package()
        self.write_testbench()
        self.write_script()
        self.write_header()
        self.write_document()
