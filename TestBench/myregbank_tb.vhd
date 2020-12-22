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
  constant C_S_AXI_ADDR_WIDTH : integer := 0;
  constant C_S_AXI_DATA_WIDTH : integer := 0;
  -- clock period
  constant clk_period         : time    := 5 ns;
  -- Signal ports
  signal S_AXI_ACLK           : std_logic;
  signal S_AXI_ARESETN        : std_logic;
  signal S_AXI_AWADDR         : std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0);
  signal S_AXI_AWPROT         : std_logic_vector(2 downto 0);
  signal S_AXI_AWVALID        : std_logic;
  signal S_AXI_AWREADY        : std_logic;
  signal S_AXI_WDATA          : std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);
  signal S_AXI_WSTRB          : std_logic_vector((C_S_AXI_DATA_WIDTH/8)-1 downto 0);
  signal S_AXI_WVALID         : std_logic;
  signal S_AXI_WREADY         : std_logic;
  signal S_AXI_BRESP          : std_logic_vector(1 downto 0);
  signal S_AXI_BVALID         : std_logic;
  signal S_AXI_BREADY         : std_logic;
  signal S_AXI_ARADDR         : std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0);
  signal S_AXI_ARPROT         : std_logic_vector(2 downto 0);
  signal S_AXI_ARVALID        : std_logic;
  signal S_AXI_ARREADY        : std_logic;
  signal S_AXI_RDATA          : std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);
  signal S_AXI_RRESP          : std_logic_vector(1 downto 0);
  signal S_AXI_RVALID         : std_logic;
  signal S_AXI_RREADY         : std_logic;
  signal reg_i                : reg_i_t;
  signal reg_o                : reg_o_t;

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
      S_AXI_AWADDR  => S_AXI_AWADDR,
      S_AXI_AWPROT  => S_AXI_AWPROT,
      S_AXI_AWVALID => S_AXI_AWVALID,
      S_AXI_AWREADY => S_AXI_AWREADY,
      S_AXI_WDATA   => S_AXI_WDATA,
      S_AXI_WSTRB   => S_AXI_WSTRB,
      S_AXI_WVALID  => S_AXI_WVALID,
      S_AXI_WREADY  => S_AXI_WREADY,
      S_AXI_BRESP   => S_AXI_BRESP,
      S_AXI_BVALID  => S_AXI_BVALID,
      S_AXI_BREADY  => S_AXI_BREADY,
      S_AXI_ARADDR  => S_AXI_ARADDR,
      S_AXI_ARPROT  => S_AXI_ARPROT,
      S_AXI_ARVALID => S_AXI_ARVALID,
      S_AXI_ARREADY => S_AXI_ARREADY,
      S_AXI_RDATA   => S_AXI_RDATA,
      S_AXI_RRESP   => S_AXI_RRESP,
      S_AXI_RVALID  => S_AXI_RVALID,
      S_AXI_RREADY  => S_AXI_RREADY,
      reg_i         => reg_i,
      reg_o         => reg_o
      );

  main : process
  begin
    test_runner_setup(runner, runner_cfg);
    while test_suite loop
      if run("test_alive") then
        info("Hello world test_alive");
        wait for 100 ns;
        test_runner_cleanup(runner);

      elsif run("test_0") then
        info("Hello world test_0");
        wait for 100 ns;
        test_runner_cleanup(runner);
      end if;
    end loop;
  end process;

  -- clk_process :process
  -- begin
  --   clk <= '1';
  --   wait for clk_period/2;
  --   clk <= '0';
  --   wait for clk_period/2;
  -- end process;

end;
