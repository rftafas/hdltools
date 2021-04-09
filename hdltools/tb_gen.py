#################################################################################
# Copyright 2020 T.P. Correa

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.
#################################################################################
import os
import vhdl_gen as vhdl
import regbank_gen as rb
import math

TemplateHeaderCode = """
  S_AXI_ARESETN <= '0', '1' after 4.0 * axi_aclk_period_c;

  main : process

    --********************************* BFM PROCEDURE OVERLOAD ****************************************
    procedure axilite_write(
      constant addr_value : in unsigned;
      constant data_value : in std_logic_vector;
      constant msg        : in string) is
    begin
      axilite_write(addr_value,         -- keep as is
                    data_value,         -- keep as is
                    msg,                -- keep as is
                    S_AXI_ACLK,         -- Clock signal
                    axilite_if);  -- Signal must be visible in local process scope
    end;

    procedure axilite_read(
      constant addr_value : in  unsigned;
      variable data_value : out std_logic_vector;
      constant msg        : in  string) is
    begin
      axilite_read(addr_value,          -- keep as is
                   data_value,          -- keep as is
                   msg,                 -- keep as is
                   S_AXI_ACLK,          -- Clock signal
                   axilite_if);  -- Signal must be visible in local process scope
    end;

    procedure axilite_check(
      constant addr_value : in unsigned;
      constant data_value : in std_logic_vector;
      constant msg        : in string) is
    begin
      axilite_check(addr_value,         -- keep as is
                    data_value,         -- keep as is
                    msg,                -- keep as is
                    S_AXI_ACLK,         -- Clock signal
                    axilite_if);  -- Signal must be visible in local process scope
    end;

    -- Begin procedures to test registers
    -- Read Only
    procedure test_ReadOnly_user_side(
      addr_value : in unsigned;
      data_value : in std_logic_vector;
      reg : in std_logic_vector)
    is
    begin
    end;

    procedure test_ReadOnly_axi_side(
      addr_value : in unsigned;
      data_value : in std_logic_vector;
      reg : in std_logic_vector)
    is
    begin
    end;

    -- Read Write
    procedure test_ReadWrite_user_side(
      addr_value : in unsigned;
      data_value : in std_logic_vector;
      reg : in std_logic_vector)
    is
    begin
    end;

    procedure test_ReadWrite_axi_side(
      addr_value : in unsigned;
      data_value : in std_logic_vector;
      reg : in std_logic_vector)
    is
    begin
    end;

    -- Write2Clear
    procedure test_Write2Clear_user_side(
      addr_value : in unsigned;
      data_value : in std_logic_vector;
      reg : in std_logic_vector)
    is
    begin
    end;

    procedure test_Write2Clear_axi_side(
      addr_value : in unsigned;
      data_value : in std_logic_vector;
      reg : in std_logic_vector)
    is
    begin
    end;

    -- Write2Pulse
    procedure test_Write2Pulse_user_side(
      addr_value : in unsigned;
      data_value : in std_logic_vector;
      reg : in std_logic_vector)
    is
    begin
    end;

    procedure test_Write2Pulse_axi_side(
      addr_value : in unsigned;
      data_value : in std_logic_vector;
      reg : in std_logic_vector)
    is
    begin
    end;

    variable data_output       : std_logic_vector(31 downto 0) := (others => '0');
    variable data_before_write : std_logic_vector(31 downto 0) := (others => '0');
    variable test_case         : natural                       := 0;
  begin

    test_runner_setup(runner, runner_cfg);
    disable_log_msg(ID_POS_ACK);

    while test_suite loop
      if run("test_all_registers") then
        uvvm_util.methods_pkg.log("Starting Simulation to test auto-genered regbank.");

        wait until s_axi_aresetn = '1';
        uvvm_util.methods_pkg.log("s_axi_aresetn = 1.");
        wait for 5*axi_aclk_period_c;
        -- AXI bus reset.
        axilite_if <= init_axilite_if_signals(32, 32);
        uvvm_util.methods_pkg.log("axilite_if reset.");
        wait for 5*axi_aclk_period_c;
"""

TemplateFooterCode = """
        wait for 100 ns;
        test_runner_cleanup(runner);

      end if;
    end loop;
  end process;

  clock_generator(S_AXI_ACLK, axi_aclk_period_c);
"""


class TestBench(vhdl.BasicVHDL):
    def __init__(self, entity_name, regBank):
        vhdl.BasicVHDL.__init__(self, entity_name + "_tb", "bench")
        self.generate_code = False
        self.regBank = regBank
        self.reg = regBank.reg
        self.datasize = regBank.datasize
        self.addrsize = regBank.addrsize
        self.version = regBank.version
        self.useRecords = regBank.useRecords

        # Libraries
        self.library.add("IEEE")
        self.library["IEEE"].package.add("std_logic_1164")
        self.library["IEEE"].package.add("numeric_std")
        self.library.add("std")
        self.library["std"].package.add("textio")
        if self.useRecords:
            self.library.add("src_lib")
            self.library["src_lib"].package.add(entity_name + "_pkg")
        self.library.add("bitvis_vip_axilite")
        self.library["bitvis_vip_axilite"].package.add("axilite_bfm_pkg")
        self.library.add("uvvm_util")
        self.library["uvvm_util"].context.add("uvvm_util_context")
        self.library["uvvm_util"].package.add("methods_pkg")
        self.library.add("vunit_lib")
        self.library["vunit_lib"].context.add("vunit_context")

        # Generics
        self.entity.generic.add("runner_cfg", "string", "")

        # Architecture
        # declarationHeader
        self.architecture.declarationHeader.add("constant axi_aclk_period_c : time := 10 ns;")
        self.architecture.declarationHeader.add("constant C_AXILITE_BFM_CONFIG : t_axilite_bfm_config := (")
        self.architecture.declarationHeader.add("max_wait_cycles            => 10,")
        self.architecture.declarationHeader.add("max_wait_cycles_severity   => TB_FAILURE,")
        self.architecture.declarationHeader.add("clock_period               => axi_aclk_period_c,")
        self.architecture.declarationHeader.add("clock_period_margin        => 0 ns,")
        self.architecture.declarationHeader.add("clock_margin_severity      => TB_ERROR,")
        self.architecture.declarationHeader.add("setup_time                 => 2.5 ns,")
        self.architecture.declarationHeader.add("hold_time                  => 2.5 ns,")
        self.architecture.declarationHeader.add("expected_response          => OKAY,")
        self.architecture.declarationHeader.add("expected_response_severity => TB_FAILURE,")
        self.architecture.declarationHeader.add("protection_setting         => UNPRIVILIGED_UNSECURE_DATA,")
        self.architecture.declarationHeader.add("num_aw_pipe_stages         => 1,")
        self.architecture.declarationHeader.add("num_w_pipe_stages          => 1,")
        self.architecture.declarationHeader.add("num_ar_pipe_stages         => 1,")
        self.architecture.declarationHeader.add("num_r_pipe_stages          => 1,")
        self.architecture.declarationHeader.add("num_b_pipe_stages          => 1,")
        self.architecture.declarationHeader.add("id_for_bfm                 => ID_BFM,")
        self.architecture.declarationHeader.add("id_for_bfm_wait            => ID_BFM_WAIT,")
        self.architecture.declarationHeader.add("id_for_bfm_poll            => ID_BFM_POLL);")

        # Constant
        self.architecture.constant.add("C_S_AXI_ADDR_WIDTH", "integer", str(self.addrsize))
        self.architecture.constant.add("C_S_AXI_DATA_WIDTH", "integer", str(self.datasize))

        # Custom Type
        self.architecture.customTypes.add("AXILite_32", "SubType", "t_axilite_if")
        self.architecture.customTypes["AXILite_32"].add("write_address_channel", "awaddr(%d downto 0)" % (self.datasize - 1))
        self.architecture.customTypes["AXILite_32"].add("write_data_channel", "wdata(%d downto 0), wstrb(%d downto 0)" %
                                                        (self.datasize - 1, int(self.datasize/8) - 1))
        self.architecture.customTypes["AXILite_32"].add("read_address_channel", "araddr(%d downto 0)" % (self.datasize - 1))
        self.architecture.customTypes["AXILite_32"].add("read_data_channel", "rdata(%d downto 0)" % (self.datasize - 1))

        # Signals
        self.architecture.signal.add("S_AXI_ACLK", "std_logic")
        self.architecture.signal.add("S_AXI_ARESETN", "std_logic")
        self.architecture.signal.add("axilite_if", "AXILite_32_t")

    def instantiate_regbank(self, indent_level=2):
        hdl_code = ""
        hdl_code += "%s_i : entity src_lib.%s\n\r" % (self.regBank.entity.name, self.regBank.entity.name)
        if (self.regBank.entity.generic):
            hdl_code = hdl_code + vhdl.indent(indent_level) + ("generic map (\r\n")
            i = 0
            list = self.regBank.entity.generic
            for j in list:
                i = i+1
                if (i == len(list)):
                    hdl_code += vhdl.indent(indent_level + 1) + "%s => %s\n\r" % (list[j].name, list[j].name)
                    hdl_code += vhdl.indent(indent_level + 1) + ")\n\r"
                else:
                    hdl_code += vhdl.indent(indent_level + 1) + "%s => %s,\n\r" % (list[j].name, list[j].name)
        if (self.regBank.entity.port):
            hdl_code = hdl_code + vhdl.indent(indent_level) + ("port map (\r\n")
            i = 0
            list = self.regBank.entity.port
            for j in list:
                i = i+1
                if "std_logic_vector" in list[j].type:
                    range = list[j].type.replace("std_logic_vector", "")
                else:
                    range = ""
                if(list[j].name == "S_AXI_ACLK" or list[j].name == "S_AXI_ARESETN"):
                    hdl_code += vhdl.indent(indent_level + 1) + "%s => %s" % (list[j].name, list[j].name)
                elif "S_AXI_AW" in list[j].name:
                    hdl_code += vhdl.indent(indent_level + 1) + "%s => %s%s" % (list[j].name,
                                                                                list[j].name.replace("S_AXI_", "axilite_if.write_address_channel."),
                                                                                range)
                elif "S_AXI_W" in list[j].name:
                    hdl_code += vhdl.indent(indent_level + 1) + "%s => %s%s" % (list[j].name,
                                                                                list[j].name.replace("S_AXI_", "axilite_if.write_data_channel."),
                                                                                range)
                elif "S_AXI_B" in list[j].name:
                    hdl_code += vhdl.indent(indent_level + 1) + "%s => %s%s" % (list[j].name,
                                                                                list[j].name.replace("S_AXI_", "axilite_if.write_response_channel."),
                                                                                range)
                elif "S_AXI_AR" in list[j].name:
                    hdl_code += vhdl.indent(indent_level + 1) + "%s => %s%s" % (list[j].name,
                                                                                list[j].name.replace("S_AXI_", "axilite_if.read_address_channel."),
                                                                                range)
                elif "S_AXI_R" in list[j].name:
                    hdl_code += vhdl.indent(indent_level + 1) + "%s => %s%s" % (list[j].name,
                                                                                list[j].name.replace("S_AXI_", "axilite_if.read_data_channel."),
                                                                                range)
                else:
                    hdl_code += vhdl.indent(indent_level + 1) + "%s => %s" % (list[j].name, list[j].name)
                    self.architecture.signal.add(list[j].name, list[j].type)

                if (i == len(list)):
                    hdl_code += "\n\r" + vhdl.indent(indent_level + 1) + ");\n\r"
                else:
                    hdl_code += ",\n\r"
        self.architecture.bodyCodeHeader.add(hdl_code)

    def build_tests(self, indent_level=3):
        case_code = ""
        i = 0
        for reg in self.reg:
            for bit in self.reg[reg]:
                if self.reg[reg][bit] != ["empty"]:
                    # add register field to record
                    if self.reg[reg][bit].regType == "ReadOnly":
                        case_code = case_code + vhdl.indent(indent_level + 3) + "when %d =>\n\r" % i
                        case_code = case_code + vhdl.indent(indent_level + 4) + "test_ReadOnly_user_side(%s, %s, %s);\n\r"
                        i = i + 1
                        case_code = case_code + vhdl.indent(indent_level + 3) + "when %d =>\n\r" % i
                        case_code = case_code + vhdl.indent(indent_level + 4) + "test_ReadOnly_axi_side(%s, %s, %s);\n\r"
                    elif self.reg[reg][bit].regType == "ReadWrite":
                        case_code = case_code + vhdl.indent(indent_level + 3) + "when %d =>\n\r" % i
                        case_code = case_code + vhdl.indent(indent_level + 4) + "test_ReadWrite_user_side(%s, %s, %s);\n\r"
                        i = i + 1
                        case_code = case_code + vhdl.indent(indent_level + 3) + "when %d =>\n\r" % i
                        case_code = case_code + vhdl.indent(indent_level + 4) + "test_ReadWrite_axi_side(%s, %s, %s);\n\r"
                    elif self.reg[reg][bit].regType == "SplitReadWrite":
                        # case_code = case_code + vhdl.indent(indent_level + 2) + "when %d =>\n\r" % i
                        # case_code = case_code + vhdl.indent(indent_level + 3) + "test_ReadOnly_user_side(%s, %s, %s);\n\r"
                        # i = i + 1
                        # case_code = case_code + "when %d =>\n\r" % i
                        # case_code = case_code + "test_ReadOnly_axi_side(%s, %s, %s);\n\r"
                        pass
                    elif self.reg[reg][bit].regType == "Write2Clear":
                        case_code = case_code + vhdl.indent(indent_level + 3) + "when %d =>\n\r" % i
                        case_code = case_code + vhdl.indent(indent_level + 4) + "test_Write2Clear_user_side(%s, %s, %s);\n\r"
                        i = i + 1
                        case_code = case_code + vhdl.indent(indent_level + 3) + "when %d =>\n\r" % i
                        case_code = case_code + vhdl.indent(indent_level + 4) + "test_Write2Clear_axi_side(%s, %s, %s);\n\r"
                    elif self.reg[reg][bit].regType == "Write2Pulse":
                        case_code = case_code + vhdl.indent(indent_level + 3) + "when %d =>\n\r" % i
                        case_code = case_code + vhdl.indent(indent_level + 4) + "test_Write2Pulse_user_side(%s, %s, %s);\n\r"
                        i = i + 1
                        case_code = case_code + vhdl.indent(indent_level + 3) + "when %d =>\n\r" % i
                        case_code = case_code + vhdl.indent(indent_level + 4) + "test_Write2Pulse_axi_side(%s, %s, %s);\n\r"
                    i = i + 1
        hdl_code = vhdl.indent(indent_level) + "for i in 0 to 100 loop\n\r"
        hdl_code += vhdl.indent(indent_level + 1) + "wait_num_rising_edge(S_AXI_ACLK, 1);\n\r"
        hdl_code += vhdl.indent(indent_level + 1) + "test_case := random(0, %d);\n\r" % (i - 1)
        hdl_code += vhdl.indent(indent_level + 1) + "uvvm_util.methods_pkg.log(\"Test case number: \" & to_string(test_case));\n\r"
        # hdl_code += vhdl.indent(indent_level + 1) + "case test_case is\n\r"
        # hdl_code += case_code
        # hdl_code += vhdl.indent(indent_level) + "when others=>\n\r"
        # hdl_code += vhdl.indent(indent_level) + "end case;\n\r"
        hdl_code += vhdl.indent(indent_level) + "wait for random(1 ns, 500 ns);"
        hdl_code += vhdl.indent(indent_level) + "end loop;"
        self.architecture.bodyCodeHeader.add(hdl_code)

    def code(self):
        if self.generate_code is False:
            self.instantiate_regbank()
            for lines in TemplateHeaderCode.splitlines():
                self.architecture.bodyCodeHeader.add(lines)

            self.build_tests()

            for lines in TemplateFooterCode.splitlines():
                self.architecture.bodyCodeFooter.add(lines)

            self.generate_code = True

        hdl_code = vhdl.BasicVHDL.code(self)
        return hdl_code

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
