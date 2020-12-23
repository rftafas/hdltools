library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
package myregbank_pkg is
  -- constants  (
  constant Golden_offset_c                 : unsigned(31 downto 0) := to_unsigned(0, 32);
  constant Golden_g1_i_offset_c            : natural               := 0;
  constant Golden_g1_i_width_c             : natural               := 32;
  constant ReadWrite1_offset_c             : unsigned(31 downto 0) := to_unsigned(1, 32);
  constant ReadWrite1_rw1_o_offset_c       : natural               := 0;
  constant ReadWrite1_rw1_o_width_c        : natural               := 32;
  constant ReadWrite2_offset_c             : unsigned(31 downto 0) := to_unsigned(2, 32);
  constant ReadWrite2_rw2_o_offset_c       : natural               := 0;
  constant ReadWrite2_rw2_o_width_c        : natural               := 32;
  constant WriteToClear_offset_c           : unsigned(31 downto 0) := to_unsigned(3, 32);
  constant WriteToClear_w2c1_i_offset_c    : natural               := 0;
  constant WriteToClear_w2c1_i_width_c     : natural               := 32;
  constant SlicedReg_offset_c              : unsigned(31 downto 0) := to_unsigned(4, 32);
  constant SlicedReg_pulse1_o_offset_c     : natural               := 0;
  constant SlicedReg_pulse1_o_width_c      : natural               := 16;
  constant SlicedReg_pulse2_o_offset_c     : natural               := 16;
  constant SlicedReg_pulse2_o_width_c      : natural               := 16;
  constant MixedRegister_offset_c          : unsigned(31 downto 0) := to_unsigned(5, 32);
  constant MixedRegister_pulse1_o_offset_c : natural               := 0;
  constant MixedRegister_pulse1_o_width_c  : natural               := 1;
  constant MixedRegister_w2c1_i_offset_c   : natural               := 1;
  constant MixedRegister_w2c1_i_width_c    : natural               := 1;
  constant MixedRegister_ro1_i_offset_c    : natural               := 2;
  constant MixedRegister_ro1_i_width_c     : natural               := 1;
  constant MixedRegister_div1_i_offset_c   : natural               := 8;
  constant MixedRegister_div1_i_width_c    : natural               := 8;
  constant MixedRegister_div2_o_offset_c   : natural               := 16;
  constant MixedRegister_div2_o_width_c    : natural               := 8;
  constant MixedRegister_div3_i_offset_c   : natural               := 24;
  constant MixedRegister_div3_i_width_c    : natural               := 8;
  constant ReadAWriteB_offset_c            : unsigned(31 downto 0) := to_unsigned(6, 32);
  constant ReadAWriteB_rAwB_i_offset_c     : natural               := 0;
  constant ReadAWriteB_rAwB_i_width_c      : natural               := 32;

  -- records (
  type reg_i_t is record
    Golden_g1_i                  : std_logic_vector(31 downto 0);
    set_WriteToClear_w2c1_i      : std_logic_vector(31 downto 0);
    set_MixedRegister_w2c1_i     : std_logic;
    clear_MixedRegister_w2c1_i   : std_logic;
    MixedRegister_ro1_i          : std_logic;
    set_MixedRegister_div1_i     : std_logic_vector(7 downto 0);
    MixedRegister_div3_i         : std_logic_vector(7 downto 0);
    ReadAWriteB_rAwB_i           : std_logic_vector(31 downto 0);
    clear_MixedRegister_pulse1_i : std_logic;
    clear_MixedRegister_ro1_i    : std_logic;
  end record reg_i_t;

  -- records (
  type reg_o_t is record
    ReadWrite1_rw1_o       : std_logic_vector(31 downto 0);
    ReadWrite2_rw2_o       : std_logic_vector(31 downto 0);
    SlicedReg_pulse1_o     : std_logic_vector(15 downto 0);
    SlicedReg_pulse2_o     : std_logic_vector(15 downto 0);
    MixedRegister_pulse1_o : std_logic;
    MixedRegister_div2_o   : std_logic_vector(7 downto 0);
    ReadAWriteB_rAwB_o     : std_logic_vector(31 downto 0);
  end record reg_o_t;

  -- records initialization constants (
  constant reg_i_init_c : reg_i_t := (
    Golden_g1_i                  => (others => '0'),
    set_WriteToClear_w2c1_i      => (others => '0'),
    set_MixedRegister_w2c1_i     => '0',
    clear_MixedRegister_w2c1_i   => '0',
    MixedRegister_ro1_i          => '0',
    set_MixedRegister_div1_i     => (others => '0'),
    MixedRegister_div3_i         => (others => '0'),
    ReadAWriteB_rAwB_i           => (others => '0'),
    clear_MixedRegister_pulse1_i => '0',
    clear_MixedRegister_ro1_i    => '0'
    );

  constant reg_o_init_c : reg_o_t := (
    ReadWrite1_rw1_o       => (others => '0'),
    ReadWrite2_rw2_o       => (others => '0'),
    SlicedReg_pulse1_o     => (others => '0'),
    SlicedReg_pulse2_o     => (others => '0'),
    MixedRegister_pulse1_o => '0',
    MixedRegister_div2_o   => (others => '0'),
    ReadAWriteB_rAwB_o     => (others => '0')
    );

end myregbank_pkg;
