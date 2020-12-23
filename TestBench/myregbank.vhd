library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
library expert;
use expert.std_logic_expert.all;
library work;
use work.myregbank_pkg.all;

entity myregbank is
  generic (
    C_S_AXI_ADDR_WIDTH : integer := 3;
    C_S_AXI_DATA_WIDTH : integer := 32
    );
  port (
    S_AXI_ACLK    : in  std_logic;
    S_AXI_ARESETN : in  std_logic;
    S_AXI_AWADDR  : in  std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0);
    S_AXI_AWPROT  : in  std_logic_vector(2 downto 0);
    S_AXI_AWVALID : in  std_logic;
    S_AXI_AWREADY : out std_logic;
    S_AXI_WDATA   : in  std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);
    S_AXI_WSTRB   : in  std_logic_vector((C_S_AXI_DATA_WIDTH/8)-1 downto 0);
    S_AXI_WVALID  : in  std_logic;
    S_AXI_WREADY  : out std_logic;
    S_AXI_BRESP   : out std_logic_vector(1 downto 0);
    S_AXI_BVALID  : out std_logic;
    S_AXI_BREADY  : in  std_logic;
    S_AXI_ARADDR  : in  std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0);
    S_AXI_ARPROT  : in  std_logic_vector(2 downto 0);
    S_AXI_ARVALID : in  std_logic;
    S_AXI_ARREADY : out std_logic;
    S_AXI_RDATA   : out std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);
    S_AXI_RRESP   : out std_logic_vector(1 downto 0);
    S_AXI_RVALID  : out std_logic;
    S_AXI_RREADY  : in  std_logic;
    reg_i         : in  reg_i_t;
    reg_o         : out reg_o_t := reg_o_init_c
    );
end myregbank;

architecture rtl of myregbank is


  constant C_S_AXI_ADDR_BYTE : integer := (C_S_AXI_DATA_WIDTH/8) + (C_S_AXI_DATA_WIDTH mod 8);
  constant C_S_AXI_ADDR_LSB  : integer := size_of(C_S_AXI_ADDR_BYTE);
  constant REG_NUM           : integer := 2**C_S_AXI_ADDR_BYTE;

  type reg_t is array (REG_NUM-1 downto 0) of std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);

  signal awaddr_s       : std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0);
  signal awready_s      : std_logic;
  signal wready_s       : std_logic;
  signal wtimeout_sr    : std_logic_vector(15 downto 0);
  signal wtimeout_s     : std_logic;
  signal bresp_s        : std_logic_vector(1 downto 0);
  signal bvalid_s       : std_logic;
  signal bresp_timer_sr : std_logic_vector(15 downto 0);
  signal araddr_s       : std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0);
  signal arready_s      : std_logic;
  signal rdata_s        : std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);
  signal rready_s       : std_logic;
  signal rresp_s        : std_logic_vector(1 downto 0);
  signal rvalid_s       : std_logic;
  signal rtimeout_sr    : std_logic_vector(15 downto 0);
  signal rtimeout_s     : std_logic;
  signal regwrite_s     : reg_t := (others => (others => '0'));
  signal regread_s      : reg_t := (others => (others => '0'));
  signal regclear_s     : reg_t := (others => (others => '0'));
  signal regset_s       : reg_t := (others => (others => '0'));
  signal regread_en     : std_logic;
  signal regwrite_en    : std_logic;

  --architecture_declaration_tag

begin


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
      if (awready_s = '1' and S_AXI_AWVALID = '1') then
        awready_s <= '0';
        awaddr_s  <= S_AXI_AWADDR;
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
      bvalid_s <= '0';
      bresp_s  <= "00";
    elsif rising_edge(S_AXI_ACLK) then
      if (wready_s = '1' and awready_s = '1') then
        bvalid_s       <= '1';
        bresp_s        <= "00";
        bresp_timer_sr <= (0 => '1', others => '0');
      elsif wtimeout_s = '1' then
        bvalid_s       <= '1';
        bresp_s        <= "10";
        bresp_timer_sr <= (0 => '1', others => '0');
      elsif bvalid_s = '1' then
        bresp_timer_sr <= bresp_timer_sr(14 downto 0) & bresp_timer_sr(15);
        if S_AXI_BREADY = '1' or bresp_timer_sr(15) = '0' then
          bvalid_s       <= '0';
          bresp_s        <= "00";
          bresp_timer_sr <= (others => '0');
        end if;
      end if;
    end if;
  end process;

  wtimer_p : process (S_AXI_ACLK)
  begin
    if S_AXI_ARESETN = '0' then
      wtimeout_s <= '0';
    elsif rising_edge(S_AXI_ACLK) then
      wtimeout_s <= wtimeout_sr(15);
      if wready_s = '1' or awready_s = '1' then
        wtimeout_sr <= (0 => '1', others => '0');
      elsif wready_s = '1' and awready_s = '1' then
        wtimeout_sr <= (others => '0');
      else
        wtimeout_sr <= wtimeout_sr(14 downto 0) & wtimeout_sr(15);
      end if;
    end if;
  end process;

  regwrite_en <= wready_s and awready_s;

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
      if arready_s = '0' then           --there is an address waiting for us.
        rvalid_s <= '1';
        rresp_s  <= "00";               -- 'OKAY' response
      elsif S_AXI_RREADY = '1' then
        --Read data is accepted by the master
        rvalid_s <= '0';
      elsif rtimeout_s = '1' then
        --when it times out? when after doing my part, master does not respond
        --with the RREADY, meaning he havent read my data.
        rvalid_s <= '0';
        rresp_s  <= "10";      -- No one is expected to read this. Debug only.
      else
        rvalid_s <= '0';
        rresp_s  <= "00";      -- No one is expected to read this. Debug only.
      end if;
    end if;
  end process;

  rtimer_p : process (S_AXI_ACLK)
  begin
    if S_AXI_ARESETN = '0' then
      rtimeout_s <= '0';
    elsif rising_edge(S_AXI_ACLK) then
      rtimeout_s <= wtimeout_sr(15);
      if rready_s = '0' then
        rtimeout_sr <= (0 => '1', others => '0');
      else
        rtimeout_sr <= rtimeout_sr(14 downto 0) & rtimeout_sr(15);
      end if;
    end if;
  end process;

  --we only act if there is no pending read.
  regread_en <= arready_s nand rvalid_s;

  --get data from ports to bus
  read_reg_p : process(S_AXI_ACLK) is
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
        S_AXI_RDATA <= reg_tmp(loc_addr);
      end if;
    end if;
  end process;

  --architecture_body_tag.

  --Register Connection
  regread_s(0)(31 downto 0)              <= reg_i.Golden_g1_i(31 downto 0);
  reg_o.ReadWrite1_rw1_o(31 downto 0)    <= regwrite_s(1)(31 downto 0);
  regread_s(1)(31 downto 0)              <= regwrite_s(1)(31 downto 0);
  reg_o.ReadWrite2_rw2_o(31 downto 0)    <= regwrite_s(2)(31 downto 0);
  regread_s(2)(31 downto 0)              <= regwrite_s(2)(31 downto 0);
  reg_o.SlicedReg_pulse1_o(15 downto 0)  <= regwrite_s(4)(15 downto 0);
  reg_o.SlicedReg_pulse2_o(15 downto 0)  <= regwrite_s(4)(31 downto 16);
  reg_o.MixedRegister_pulse1_o           <= regwrite_s(5)(0);
  regread_s(5)(2)                        <= reg_i.MixedRegister_ro1_i;
  reg_o.MixedRegister_div2_o(7 downto 0) <= regwrite_s(5)(23 downto 16);
  regread_s(5)(23 downto 16)             <= regwrite_s(5)(23 downto 16);
  regread_s(5)(31 downto 24)             <= reg_i.MixedRegister_div3_i(7 downto 0);
  reg_o.ReadAWriteB_rAwB_o               <= regwrite_s(6)(31 downto 0);
  regread_s(6)(31 downto 0)              <= reg_i.ReadAWriteB_rAwB_i;

  --Set Connection for Write to Clear
  regset_s(3)(31 downto 0) <= reg_i.set_WriteToClear_w2c1_i(31 downto 0);
  regset_s(5)(1)           <= reg_i.set_MixedRegister_w2c1_i;
  regset_s(5)(15 downto 8) <= reg_i.set_MixedRegister_div1_i(7 downto 0);

  --External Clear Connection
  regclear_s(5)(0) <= '1' when reg_i.clear_MixedRegister_pulse1_i = '1' else '0';
  regclear_s(5)(1) <= '1' when reg_i.clear_MixedRegister_w2c1_i = '1'   else regwrite_s(5)(1);
  regclear_s(5)(2) <= '1' when reg_i.clear_MixedRegister_ro1_i = '1'    else '0';


end rtl;
