---------------------------------------------------------------------------------
-- This is free and unencumbered software released into the public domain.
--
-- Anyone is free to copy, modify, publish, use, compile, sell, or
-- distribute this software, either in source code form or as a compiled
-- binary, for any purpose, commercial or non-commercial, and by any
-- means.
--
-- In jurisdictions that recognize copyright laws, the author or authors
-- of this software dedicate any and all copyright interest in the
-- software to the public domain. We make this dedication for the benefit
-- of the public at large and to the detriment of our heirs and
-- successors. We intend this dedication to be an overt act of
-- relinquishment in perpetuity of all present and future rights to this
-- software under copyright law.
--
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
-- EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
-- MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
-- IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
-- OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
-- ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
-- OTHER DEALINGS IN THE SOFTWARE.
--
-- For more information, please refer to <http://unlicense.org/>
---------------------------------------------------------------------------------

library IEEE;
  use IEEE.std_logic_1164.all;
  use IEEE.numeric_std.all;
library std;
  use std.textio.all;
library src_lib;
  use src_lib.MyRegBank_pkg.all;
library bitvis_vip_axilite;
  use bitvis_vip_axilite.axilite_bfm_pkg.all;
library uvvm_util;
  context uvvm_util.uvvm_util_context;
  use uvvm_util.methods_pkg.all;
library vunit_lib;
  context vunit_lib.vunit_context;

entity MyRegBank_tb is
  generic (
    runner_cfg : string
  );
  --port (
    --port_declaration_tag
  --);
end MyRegBank_tb;

architecture bench of MyRegBank_tb is

  constant axi_aclk_period_c : time := 10 ns;
  constant C_AXILITE_BFM_CONFIG : t_axilite_bfm_config := (
  max_wait_cycles            => 10,
  max_wait_cycles_severity   => TB_FAILURE,
  clock_period               => axi_aclk_period_c,
  clock_period_margin        => 0 ns,
  clock_margin_severity      => TB_ERROR,
  setup_time                 => 2.5 ns,
  hold_time                  => 2.5 ns,
  expected_response          => OKAY,
  expected_response_severity => TB_FAILURE,
  protection_setting         => UNPRIVILIGED_UNSECURE_DATA,
  num_aw_pipe_stages         => 1,
  num_w_pipe_stages          => 1,
  num_ar_pipe_stages         => 1,
  num_r_pipe_stages          => 1,
  num_b_pipe_stages          => 1,
  id_for_bfm                 => ID_BFM,
  id_for_bfm_wait            => ID_BFM_WAIT,
  id_for_bfm_poll            => ID_BFM_POLL);

  constant C_S_AXI_ADDR_WIDTH : integer := 3;
  constant C_S_AXI_DATA_WIDTH : integer := 32;

subtype AXILite_32_t is t_axilite_if (
  write_address_channel (awaddr(31 downto 0)),
  write_data_channel (wdata(31 downto 0), wstrb(3 downto 0)),
  read_address_channel (araddr(31 downto 0)),
  read_data_channel (rdata(31 downto 0))); 


  signal S_AXI_ACLK : std_logic;
  signal S_AXI_ARESETN : std_logic;
  signal axilite_if : AXILite_32_t;
  signal reg_i : reg_i_t;
  signal reg_o : reg_o_t;

  --architecture_declaration_tag

begin

  MyRegBank_i : entity src_lib.MyRegBank
    generic map (
      C_S_AXI_ADDR_WIDTH => C_S_AXI_ADDR_WIDTH,
      C_S_AXI_DATA_WIDTH => C_S_AXI_DATA_WIDTH
      )
    port map (
      S_AXI_ACLK => S_AXI_ACLK,
      S_AXI_ARESETN => S_AXI_ARESETN,
      S_AXI_AWADDR => axilite_if.write_address_channel.AWADDR(C_S_AXI_ADDR_WIDTH-1 downto 0),
      S_AXI_AWPROT => axilite_if.write_address_channel.AWPROT(2 downto 0),
      S_AXI_AWVALID => axilite_if.write_address_channel.AWVALID,
      S_AXI_AWREADY => axilite_if.write_address_channel.AWREADY,
      S_AXI_WDATA => axilite_if.write_data_channel.WDATA(C_S_AXI_DATA_WIDTH-1 downto 0),
      S_AXI_WSTRB => axilite_if.write_data_channel.WSTRB((C_S_AXI_DATA_WIDTH/8)-1 downto 0),
      S_AXI_WVALID => axilite_if.write_data_channel.WVALID,
      S_AXI_WREADY => axilite_if.write_data_channel.WREADY,
      S_AXI_BRESP => axilite_if.write_response_channel.BRESP(1 downto 0),
      S_AXI_BVALID => axilite_if.write_response_channel.BVALID,
      S_AXI_BREADY => axilite_if.write_response_channel.BREADY,
      S_AXI_ARADDR => axilite_if.read_address_channel.ARADDR(C_S_AXI_ADDR_WIDTH-1 downto 0),
      S_AXI_ARPROT => axilite_if.read_address_channel.ARPROT(2 downto 0),
      S_AXI_ARVALID => axilite_if.read_address_channel.ARVALID,
      S_AXI_ARREADY => axilite_if.read_address_channel.ARREADY,
      S_AXI_RDATA => axilite_if.read_data_channel.RDATA(C_S_AXI_DATA_WIDTH-1 downto 0),
      S_AXI_RRESP => axilite_if.read_data_channel.RRESP(1 downto 0),
      S_AXI_RVALID => axilite_if.read_data_channel.RVALID,
      S_AXI_RREADY => axilite_if.read_data_channel.RREADY,
      reg_i => reg_i,
      reg_o => reg_o
      );

  
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
        for i in 0 to 100 loop
        wait_num_rising_edge(S_AXI_ACLK, 1);
        test_case := random(0, 24);
        uvvm_util.methods_pkg.log("Test case number: " & to_string(test_case));
      wait for random(1 ns, 500 ns);      end loop;

  --architecture_body_tag.

  
          wait for 100 ns;
          test_runner_cleanup(runner);
  
        end if;
      end loop;
    end process;
  
    clock_generator(S_AXI_ACLK, axi_aclk_period_c);

end bench;

