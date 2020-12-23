library ieee;
--! Logic elements.
use ieee.std_logic_1164.all;
--! Arithmetic functions.
use ieee.numeric_std.all;
--
library std;
use std.textio.all;
--
library src_lib;
use src_lib.myregbank_pkg.all;
--use src_lib.types_declaration_ssvectors_wrapper_pkg.all;

-- library tb_lib;
-- use tb_lib.ssvectors_sim_pkg.all;

-- UVVM version: v2019.06.06
library bitvis_vip_axilite;
use bitvis_vip_axilite.axilite_bfm_pkg.all;

library uvvm_util;
context uvvm_util.uvvm_util_context;
use uvvm_util.methods_pkg.all;

-- vunit
library vunit_lib;
context vunit_lib.vunit_context;

entity myregbank_tb is
  --vunit
  generic (runner_cfg : string);
end;

architecture bench of myregbank_tb is

  -- Generics
  constant C_S_AXI_ADDR_WIDTH : integer := 3;
  constant C_S_AXI_DATA_WIDTH : integer := 32;
                                        -- clock period
  constant axi_aclk_period_c  : time    := 10 ns;
  -- axi lite BFM config
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
    id_for_bfm_poll            => ID_BFM_POLL
    );

-- type definition
  subtype ST_AXILite_32 is t_axilite_if (
    write_address_channel (
      awaddr(31 downto 0)),
    write_data_channel (
      wdata(31 downto 0),
      wstrb(3 downto 0)),
    read_address_channel (
      araddr(31 downto 0)),
    read_data_channel (
      rdata(31 downto 0))
    );

  -- Signal ports
  signal S_AXI_ACLK    : std_logic := '0';
  signal S_AXI_ARESETN : std_logic := '0';
  signal reg_i         : reg_i_t   := reg_i_init_c;
  signal reg_o         : reg_o_t;

  signal axilite_if : ST_AXILite_32;


begin
  -- Instance
  myregbank_i : entity src_lib.myregbank
    generic map (
      C_S_AXI_ADDR_WIDTH => C_S_AXI_ADDR_WIDTH,
      C_S_AXI_DATA_WIDTH => C_S_AXI_DATA_WIDTH
      )
    port map (
      S_AXI_ACLK    => S_AXI_ACLK,
      S_AXI_ARESETN => S_AXI_ARESETN,
      S_AXI_AWADDR  => axilite_if.write_address_channel.awaddr(C_S_AXI_ADDR_WIDTH-1 downto 0),
      S_AXI_AWPROT  => axilite_if.write_address_channel.awprot,
      S_AXI_AWVALID => axilite_if.write_address_channel.awvalid,
      S_AXI_AWREADY => axilite_if.write_address_channel.awready,
      S_AXI_WDATA   => axilite_if.write_data_channel.wdata,
      S_AXI_WSTRB   => axilite_if.write_data_channel.wstrb,
      S_AXI_WVALID  => axilite_if.write_data_channel.wvalid,
      S_AXI_WREADY  => axilite_if.write_data_channel.wready,
      S_AXI_BRESP   => axilite_if.write_response_channel.bresp,
      S_AXI_BVALID  => axilite_if.write_response_channel.bvalid,
      S_AXI_BREADY  => axilite_if.write_response_channel.bready,
      S_AXI_ARADDR  => axilite_if.read_address_channel.araddr(C_S_AXI_ADDR_WIDTH-1 downto 0),
      S_AXI_ARPROT  => axilite_if.read_address_channel.arprot,
      S_AXI_ARVALID => axilite_if.read_address_channel.arvalid,
      S_AXI_ARREADY => axilite_if.read_address_channel.arready,
      S_AXI_RDATA   => axilite_if.read_data_channel.rdata,
      S_AXI_RRESP   => axilite_if.read_data_channel.rresp,
      S_AXI_RVALID  => axilite_if.read_data_channel.rvalid,
      S_AXI_RREADY  => axilite_if.read_data_channel.rready,
      reg_i         => reg_i,
      reg_o         => reg_o
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
        for i in 1 to 5 loop
          wait_num_rising_edge(S_AXI_ACLK, 1);
          test_case := random(1, 2);
          uvvm_util.methods_pkg.log("Test case number: " & to_string(test_case));
          case test_case is
            when 1 =>
              data_before_write := reg_i.Golden_g1_i;
              axilite_write(Golden_offset_c, random(C_S_AXI_DATA_WIDTH), "Write to read only register");
              wait_num_rising_edge(S_AXI_ACLK, 1);
              axilite_read(Golden_offset_c, data_output, "Reading");
            -- axilite_check(Golden_offset_c, data_before_write, "Check no change");
            when 2 =>
              reg_i.Golden_g1_i <= random(reg_i.Golden_g1_i'length);
              wait_num_rising_edge(S_AXI_ACLK, 1);
              axilite_read(Golden_offset_c, data_output, "Reading");
            -- axilite_check(Golden_offset_c, reg_i.Golden_g1_i, "Check no change");
            when others =>
          end case;
          wait for random(1 ns, 500 ns);
        end loop;

        wait for 100 ns;
        test_runner_cleanup(runner);

      end if;
    end loop;
  end process;

  clock_generator(S_AXI_ACLK, axi_aclk_period_c);


end;
