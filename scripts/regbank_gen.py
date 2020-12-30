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
import sys
import os
from datetime import datetime
import vhdl_gen as vhdl
import pkgvhdl_gen as pkgvhdl
import tb_gen as tbvhdl
import math
from mdutils.mdutils import MdUtils

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
    S_AXI_RDATA   <= rdata_s;
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
            if (wready_s = '1' and S_AXI_WVALID = '1') then
                wready_s <= '0';
            elsif (S_AXI_BREADY = '1' and bvalid_s = '1') then
                wready_s <= '1';
            elsif wtimeout_s = '1' then
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
            elsif bvalid_s = '1' then
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
                wtimeout_sr <= (others=>'0');
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
            loc_addr := to_integer(unsigned(awaddr_s(C_S_AXI_ADDR_WIDTH-1 downto C_S_AXI_ADDR_LSB)));
            for j in regwrite_s'range loop
                for k in C_S_AXI_ADDR_BYTE-1 downto 0 loop
                    for m in 7 downto 0 loop
                        if regclear_s(j)(k*8+m) = '1' then
                            regwrite_s(j)(k*8+m) <= '0';
                        elsif regwrite_en = '1' then
                            if S_AXI_WSTRB(k) = '1' then
                                if regclear_s(j)(k*8+m) = '1' then
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
        variable reg_tmp  : reg_t := (others => (others => '0'));
        variable reg_lock : reg_t := (others => (others => '0'));
    begin
        if (S_AXI_ARESETN = '0') then
            reg_tmp  := (others => (others => '0'));
            reg_lock := (others => (others => '0'));
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


def getDirection(type):
    if type in ("ReadOnly", "Write2Clear", "SplitReadWrite"):
        return "in"
    else:
        return "out"


def getSuffix(direction):
    if direction in ("in"):
        return "_i"
    else:
        return "_o"


class RegisterBit:
    def __init__(self, name, type, init):
        if type in RegisterTypeSet:
            self.regType = type
        else:
            self.regType = "ReadOnly"
            print("Register Type not known. Using ReadOnly")
            print(RegisterTypeSet)
        self.externalClear = False
        self.direction = getDirection(type)
        self.vhdlType = "std_logic"
        self.name = name+getSuffix(self.direction)
        self.radix = name
        self.size = 1
        self.description = ""
        if init is None:
            self.init = "'0'"
        else:
            self.init = init

    def addDescription(self, str):
        self.description = str


class RegisterSlice(RegisterBit):
    def __init__(self, name, type, size, init):
        RegisterBit.__init__(self, name, type, init)
        self.size = size
        self.vhdlrange = "(%d downto 0)" % size
        self.vhdlType = "std_logic_vector(%d downto 0)" % (size-1)
        self.description = ""
        if init is None:
            self.init = "(others => '0')"
        else:
            self.init = init

    def addDescription(self, str):
        self.description = str


class RegisterWord(dict):
    def __init__(self, name, size, init=None):
        dict.__init__(self)
        self.name = name
        self.description = ""
        for j in range(size):
            self[j] = ["empty"]
        if init is None:
            self.init = "(others => '0')"
        else:
            self.init = init

    def add(self, name, type, start, size, init=None):
        if "empty" in self[start]:
            if size > 1:
                self[start] = RegisterSlice(name, type, size, init)
            else:
                self[start] = RegisterBit(name, type, init)
                for j in range(start+1, start+size):
                    if "empty" in self[j]:
                        self[j] = name+"(%d)" % j
                    else:
                        print("Reg is already occupied by %s" % self[j].name)
        else:
            print("This reg is already occupied by %s" % self[start].name)

    def addDescription(self, str):
        self.description = str


class RegisterList(dict):
    def add(self, number, Register):
        self[number] = Register
        self.description = ""

    def addDescription(self, str):
        self.description = str


class RegisterBank(vhdl.BasicVHDL):
    def __init__(self, entity_name, architecture_name, datasize, registerNumber, useRecords=True):
        vhdl.BasicVHDL.__init__(self, entity_name, architecture_name)
        self.generate_code = False
        self.reg = RegisterList()
        self.datasize = datasize
        self.addrsize = math.ceil(math.log(registerNumber, 2))
        self.document = MdUtils(file_name=entity_name, title='Register Bank: %s' % entity_name)
        self.version = datetime.now().strftime("%Y%m%d_%H%m")

        self.useRecords = useRecords
        if self.useRecords:
            self.pkg = pkgvhdl.PkgVHDL(entity_name + "_pkg", self.version)
            self.pkg.addRecord("reg_i")
            self.pkg.addRecord("reg_o")
            self.pkg.library.add("IEEE")
            self.pkg.library["IEEE"].package.add("std_logic_1164")
            self.pkg.library["IEEE"].package.add("numeric_std")

        # Libraries
        self.library.add("IEEE")
        self.library["IEEE"].package.add("std_logic_1164")
        self.library["IEEE"].package.add("numeric_std")
        self.library.add("expert")
        self.library["expert"].package.add("std_logic_expert")
        if self.useRecords:
            self.library.add("work")
            self.library["work"].package.add(self.pkg.declaration.name)
        # Generics
        self.entity.generic.add("C_S_AXI_ADDR_WIDTH", "integer", str(self.addrsize))
        self.entity.generic.add("C_S_AXI_DATA_WIDTH", "integer", str(self.datasize))
        # Ports
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
        if self.useRecords:
            self.entity.port.add("reg_i", "in", "reg_i_t")
            self.entity.port.add("reg_o", "out", "reg_o_t", "reg_o_init_c")

        # Architecture
        # Constant
        self.architecture.constant.add("register_bank_version_c", "String", "\"%s\"" % self.version)
        self.architecture.constant.add("C_S_AXI_ADDR_BYTE", "integer", "(C_S_AXI_DATA_WIDTH/8) + (C_S_AXI_DATA_WIDTH MOD 8)")
        self.architecture.constant.add("C_S_AXI_ADDR_LSB", "integer", "size_of(C_S_AXI_ADDR_BYTE)")
        self.architecture.constant.add("REG_NUM", "integer", "2**C_S_AXI_ADDR_BYTE")
        # Custom type
        self.architecture.customTypes.add("type reg_t is array (REG_NUM-1 downto 0) of std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);")
        # Signals
        self.architecture.signal.add("awaddr_s", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.architecture.signal.add("awready_s", "std_logic")
        self.architecture.signal.add("wready_s", "std_logic")
        self.architecture.signal.add("wtimeout_sr", "std_logic_vector(15 downto 0)")
        self.architecture.signal.add("wtimeout_s", "std_logic")

        self.architecture.signal.add("bresp_s", "std_logic_vector(1 downto 0)")
        self.architecture.signal.add("bvalid_s", "std_logic")
        self.architecture.signal.add("bresp_timer_sr", "std_logic_vector(15 downto 0)")
        self.architecture.signal.add("wtimeout_s", "std_logic")

        self.architecture.signal.add("araddr_s", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.architecture.signal.add("arready_s", "std_logic")
        self.architecture.signal.add("rdata_s", "std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0)")

        self.architecture.signal.add("rready_s", "std_logic")
        self.architecture.signal.add("rresp_s", "std_logic_vector(1 downto 0)")
        self.architecture.signal.add("rvalid_s", "std_logic")
        self.architecture.signal.add("rtimeout_sr", "std_logic_vector(15 downto 0)")
        self.architecture.signal.add("rtimeout_s", "std_logic")

        self.architecture.signal.add("regwrite_s", "reg_t", "(others=>(others=>'0'))")
        self.architecture.signal.add("regread_s", "reg_t", "(others=>(others=>'0'))")
        self.architecture.signal.add("regclear_s", "reg_t", "(others=>(others=>'0'))")
        self.architecture.signal.add("regset_s", "reg_t", "(others=>(others=>'0'))")

        self.architecture.signal.add("regread_en", "std_logic")
        self.architecture.signal.add("regwrite_en", "std_logic")

        if self.useRecords:
            self.architecture.bodyCodeHeader.add(
                "assert register_bank_version_c = package_version_c report \"Package and Register Bank version mismatch\" severity warning;")

        for lines in TemplateCode.splitlines():
            self.architecture.bodyCodeHeader.add(lines)

    def add(self, number, name):
        self.reg.add(number, RegisterWord(name, self.datasize))

    def registerPortAdd(self):
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                try:
                    if "SplitReadWrite" in register[bit].regType:
                        self.entity.port.add(register[bit].radix+getSuffix("in"), "in", register[bit].vhdlType)
                        self.entity.port.add(register[bit].radix+getSuffix("out"), "out", register[bit].vhdlType)
                    else:
                        self.entity.port.add(register[bit].name, register[bit].direction, register[bit].vhdlType)
                except:
                    pass

    def registerClearAdd(self):
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                try:
                    if register[bit].externalClear:
                        if self.useRecords:
                            self.pkg.declaration.record["reg_i"].add(
                                "clear_" + register.name + "_" + register[bit].radix+"_i", register[bit].vhdlType)
                        else:
                            self.entity.port.add(register[bit].radix+"_clear_i", "in", register[bit].vhdlType)
                except:
                    pass

    def registerConnection(self):
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
                        if self.useRecords:
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" %
                                                                 (index, vectorRange, "reg_i." + register.name + "_" + register[bit].name))
                        else:
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" %
                                                                 (index, vectorRange, register[bit].name))
                    elif "SplitReadWrite" in register[bit].regType:
                        if self.useRecords:
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" %
                                                                 ("reg_o." + register.name + "_" + register[bit].radix+getSuffix("out"), index, vectorRange))
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" %
                                                                 (index, vectorRange, "reg_i." + register.name + "_" + register[bit].radix+getSuffix("in")))
                        else:
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" %
                                                                 (register[bit].radix+getSuffix("out"), index, vectorRange))
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" %
                                                                 (index, vectorRange, register[bit].radix+getSuffix("in")))
                    elif "ReadWrite" in register[bit].regType:
                        if self.useRecords:
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" %
                                                                 ("reg_o." + register.name + "_" + register[bit].name, index, vectorRange))
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= regwrite_s(%d)(%s);" %
                                                                 (index, vectorRange, index, vectorRange))
                        else:
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" %
                                                                 (register[bit].name, index, vectorRange))
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= regwrite_s(%d)(%s);" %
                                                                 (index, vectorRange, index, vectorRange))
                    elif "Write2Clear" in register[bit].regType:
                        pass
                    elif "Write2Pulse" in register[bit].regType:
                        if self.useRecords:
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" %
                                                                 ("reg_o." + register.name + "_" + register[bit].name, index, vectorRange))
                        else:
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" %
                                                                 (register[bit].name, index, vectorRange))
        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "")

    def registerSetConnection(self):
        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "--Set Connection for Write to Clear")
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                if isinstance(register[bit], RegisterBit):
                    vectorRange = str(bit)
                    if isinstance(register[bit], RegisterSlice):
                        vectorRange = "%d downto %d" % (bit+register[bit].size-1, bit)
                    if "Write2Clear" in register[bit].regType:
                        if self.useRecords:
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regset_s(%d)(%s) <= %s;" %
                                                                 (index, vectorRange, "reg_i.set_" + register.name + "_" + register[bit].name))
                        else:
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regset_s(%d)(%s) <= %s;" %
                                                                 (index, vectorRange, register[bit].name))
        self.architecture.bodyCodeFooter.add("")

    def registerClearConnection(self):
        self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "--External Clear Connection")
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                if isinstance(register[bit], RegisterBit):
                    clearname = register[bit].radix+"_clear_i"
                    defaultvalue = "'1'"
                    elsevalue = "'0'"
                    vectorRange = str(bit)
                    if isinstance(register[bit], RegisterSlice):
                        vectorRange = "%d downto %d" % (bit+register[bit].size-1, bit)
                        defaultvalue = "(others=>'1')"
                    if "Write2Clear" in register[bit].regType:
                        elsevalue = "regwrite_s(%d)(%s)" % (index, vectorRange)
                    if register[bit].externalClear:
                        if self.useRecords:
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1) + "regclear_s(%d)(%s) <= %s when %s = '1' else %s;" %
                                                                 (index, vectorRange, defaultvalue,
                                                                  "reg_i.clear_" + register.name + "_" + register[bit].radix + "_i",
                                                                  elsevalue))
                        else:
                            self.architecture.bodyCodeFooter.add(vhdl.indent(1)
                                                                 + "regclear_s(%d)(%s) <= %s when %s = '1' else %s;"
                                                                 % (index, vectorRange, defaultvalue, clearname, elsevalue))

        self.architecture.bodyCodeFooter.add("")

    def createRecordsFromRegisters(self):
        for reg in self.reg:
            # add constant with register offset
            self.pkg.declaration.constant.add(self.reg[reg].name + "_offset_c", "unsigned(%d downto 0)"
                                              % (self.datasize - 1), "to_unsigned(%d,%d)" % (reg, self.datasize))
            for bit in self.reg[reg]:
                if self.reg[reg][bit] != ["empty"]:
                    # add constant with bit offset and width
                    self.pkg.declaration.constant.add(self.reg[reg].name + "_" + self.reg[reg][bit].name + "_offset_c", "natural",
                                                      "%d" % bit)
                    self.pkg.declaration.constant.add(self.reg[reg].name + "_" + self.reg[reg][bit].name + "_width_c", "natural",
                                                      "%d" % self.reg[reg][bit].size)
                    # add register field to record
                    if self.reg[reg][bit].regType == "ReadOnly":
                        self.pkg.declaration.record["reg_i"].add(
                            self.reg[reg].name + "_" + self.reg[reg][bit].name,
                            self.reg[reg][bit].vhdlType, self.reg[reg][bit].init)
                    elif self.reg[reg][bit].regType == "ReadWrite":
                        self.pkg.declaration.record["reg_o"].add(
                            self.reg[reg].name + "_" + self.reg[reg][bit].name,
                            self.reg[reg][bit].vhdlType, self.reg[reg][bit].init)
                    elif self.reg[reg][bit].regType == "SplitReadWrite":
                        self.pkg.declaration.record["reg_i"].add(
                            self.reg[reg].name + "_" + self.reg[reg][bit].radix + getSuffix("in"),
                            self.reg[reg][bit].vhdlType, self.reg[reg][bit].init)
                        self.pkg.declaration.record["reg_o"].add(
                            self.reg[reg].name + "_" + self.reg[reg][bit].radix + getSuffix("out"),
                            self.reg[reg][bit].vhdlType, self.reg[reg][bit].init)
                    elif self.reg[reg][bit].regType == "Write2Clear":
                        self.pkg.declaration.record["reg_i"].add(
                            "set_" + self.reg[reg].name + "_" + self.reg[reg][bit].name,
                            self.reg[reg][bit].vhdlType, self.reg[reg][bit].init)
                        if self.reg[reg][bit].externalClear:
                            self.pkg.declaration.record["reg_i"].add(
                                "clear_" + self.reg[reg].name + "_" + self.reg[reg][bit].name,
                                self.reg[reg][bit].vhdlType, self.reg[reg][bit].init)
                    elif self.reg[reg][bit].regType == "Write2Pulse":
                        self.pkg.declaration.record["reg_o"].add(
                            self.reg[reg].name + "_" + self.reg[reg][bit].name,
                            self.reg[reg][bit].vhdlType, self.reg[reg][bit].init)

    def code(self):
        if (not self.generate_code):
            # commented out when using Records + Package
            if self.useRecords:
                self.createRecordsFromRegisters()
            else:
                self.registerPortAdd()
            self.generate_code = True

        hdl_code = vhdl.BasicVHDL.code(self)
        return hdl_code

    def write_document(self):
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

    def write_file(self):
        if (not os.path.exists("output")):
            os.makedirs("output")

        hdl_code = self.code()
        output_file_name = "output/"+self.entity.name+".vhd"
        # to do: check if file exists. If so, emit a warning and
        # check if must clear it.
        output_file = open(output_file_name, "w+")
        for line in hdl_code:
            output_file.write(line)

        output_file.close()

        # call also Package.write_file(). It must be called after RegisterBank code()
        # because the method createRecordsFromRegisters is called inside it
        if self.useRecords:
            self.pkg.write_file()
        return True


if __name__ == '__main__':

    # first we declare a register bank.
    # It is a 32 bit register with 8 possible positions.
    # we named the architecture "RTL".
    dataSize = 32
    registerNumber = 8
    myregbank = RegisterBank("MyRegBank", "rtl", dataSize, registerNumber)

    # this is an axample of a read only register for ID, Golden number, Inputs
    # we add a position (address) and name it. Also, it is a 32bit, it must start at 0.
    # myregbank.add(REG_ADDRESS,"golden")
    # myregbank.reg[REG_ADDRESS].add(NAME,TYPE,START BIT POSITION,SIZE)
    myregbank.add(0, "golden")
    myregbank.reg[0].add("golden", "ReadOnly", 0, 32)
    # this is an example for a read/write generic register.
    myregbank.add(1, "myReadWrite1")
    myregbank.reg[1].add("myReadWrite1", "ReadWrite", 0, 32)
    # this is an example for a read/write generic register with external clear. It is possible
    # to choose an init value for any field
    myregbank.add(2, "myReadWrite2")
    myregbank.reg[2].addDescription("To improve the documentation you can add a description to any \
                                       register or register field using the * addDescription() * method.")
    myregbank.reg[2].add("myReadWrite2", "ReadWrite", 0, 32, "x\"00000023\"")
    myregbank.reg[2][0].addDescription("Example of ReadWrite register.")
    myregbank.reg[2].externalClear = True
    # this is an example of a write to clear register
    myregbank.add(3, "MyWriteToClear")
    myregbank.reg[3].add("MyWriteToClear", "Write2Clear", 0, 32)
    # wee can use just a slice on any type. Lets create a slice.
    # we will use 2 16bit register.
    myregbank.add(4, "SlicedReg")
    myregbank.reg[4].add("pulse1", "Write2Pulse", 0, 16)
    myregbank.reg[4].add("pulse2", "Write2Pulse", 16, 16)

    # And we can create a very mixed register:
    # Bit 0 is goint to be a pulsed register. Write one, it pulses output.
    myregbank.add(5, "MixedRegister")
    myregbank.reg[5].add("PulseBit", "Write2Pulse", 0, 1)
    myregbank.reg[5][0].externalClear = True  # for example, we want to kill the pulse.
    myregbank.reg[5].add("Write2ClearBit", "Write2Clear", 1, 1)
    myregbank.reg[5][1].externalClear = True  # either my write or the external can clear it.
    myregbank.reg[5].add("ReadOnlyBit", "ReadOnly", 2, 1, "'1'")
    myregbank.reg[5][2].externalClear = True  # I can force a '0' read.
    myregbank.reg[5].add("DivByte1", "Write2Clear", 8, 8)
    myregbank.reg[5].add("DivByte2", "ReadWrite", 16, 8)
    myregbank.reg[5].add("DivByte3", "ReadOnly", 24, 8)

    # And we can create a very mixed register:
    # Bit 0 is goint to be a pulsed register. Write one, it pulses output.
    myregbank.add(6, "ReadAWriteB")
    myregbank.reg[6].add("ReadAWriteB", "SplitReadWrite", 0, 32)

    tb = tbvhdl.TestBench(myregbank.entity.name, dataSize, registerNumber)
    tb = tbvhdl.TestBench(myregbank.entity.name, myregbank)
    print(myregbank.code())
    print(tb.code())

    myregbank.write_file()
    myregbank.write_document()
    myregbank.write_header()
    tb.write_file()
    print("-------------------------------------------------------------")
    print("The example will be stored at ./output/myregbank.vhd")
