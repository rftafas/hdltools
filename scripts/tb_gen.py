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
    def __init__(self, entity_name, datasize, registerNumber, useRecords=True):
        vhdl.BasicVHDL.__init__(self, entity_name + "_tb", "bench")
        self.generate_code = False
        self.reg = rb.RegisterList()
        self.datasize = datasize
        self.addrsize = math.ceil(math.log(registerNumber, 2))
        self.version = ""
        self.useRecords = useRecords

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
        self.library["uvvm_util"].context.add("vunit_context")

        # Generics
        self.entity.generic.add("runner_cfg", "string")

        # Architecture
        # declarationHeader
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
        self.architecture.constant.add("axi_aclk_period_c", "time", "10 ns")
        # Custom Type

        self.architecture.customTypes.add("subtype ST_AXILite_32 is t_axilite_if (")
        self.architecture.customTypes.add("write_address_channel (awaddr(31 downto 0)),")
        self.architecture.customTypes.add("write_data_channel (wdata(31 downto 0), wstrb(3 downto 0)),")
        self.architecture.customTypes.add("read_address_channel (araddr(31 downto 0)),")
        self.architecture.customTypes.add("read_data_channel (rdata(31 downto 0)));")

        # Signals
        self.architecture.signal.add("S_AXI_ACLK", "std_logic")
        self.architecture.signal.add("S_AXI_ARESETN", "std_logic")
        self.architecture.signal.add("axilite_if", "ST_AXILite_32")
        if self.useRecords:
            self.architecture.signal.add("reg_i", "reg_i_t", "reg_i_init_c")
            self.architecture.signal.add("reg_o", "reg_o_t", )

        for lines in TemplateHeaderCode.splitlines():
            self.architecture.bodyCodeHeader.add(lines)

        for lines in TemplateFooterCode.splitlines():
            self.architecture.bodyCodeFooter.add(lines)

    def code(self):
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
