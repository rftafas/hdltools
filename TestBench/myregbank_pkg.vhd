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

package MyRegBank_pkg is

  --generic  (
    --Package Generics go here.
  --);

  constant package_version_c : String := "20210102_1801";
  constant golden_offset_c : unsigned(31 downto 0) := to_unsigned(0,32);
  constant golden_golden_i_offset_c : natural := 0;
  constant golden_golden_i_width_c : natural := 32;
  constant myReadWrite1_offset_c : unsigned(31 downto 0) := to_unsigned(1,32);
  constant myReadWrite1_myReadWrite1_o_offset_c : natural := 0;
  constant myReadWrite1_myReadWrite1_o_width_c : natural := 32;
  constant myReadWrite2_offset_c : unsigned(31 downto 0) := to_unsigned(2,32);
  constant myReadWrite2_myReadWrite2_o_offset_c : natural := 0;
  constant myReadWrite2_myReadWrite2_o_width_c : natural := 32;
  constant MyWriteToClear_offset_c : unsigned(31 downto 0) := to_unsigned(3,32);
  constant MyWriteToClear_MyWriteToClear_i_offset_c : natural := 0;
  constant MyWriteToClear_MyWriteToClear_i_width_c : natural := 32;
  constant SlicedReg_offset_c : unsigned(31 downto 0) := to_unsigned(4,32);
  constant SlicedReg_pulse1_o_offset_c : natural := 0;
  constant SlicedReg_pulse1_o_width_c : natural := 16;
  constant SlicedReg_pulse2_o_offset_c : natural := 16;
  constant SlicedReg_pulse2_o_width_c : natural := 16;
  constant MixedRegister_offset_c : unsigned(31 downto 0) := to_unsigned(5,32);
  constant MixedRegister_PulseBit_o_offset_c : natural := 0;
  constant MixedRegister_PulseBit_o_width_c : natural := 1;
  constant MixedRegister_Write2ClearBit_i_offset_c : natural := 1;
  constant MixedRegister_Write2ClearBit_i_width_c : natural := 1;
  constant MixedRegister_ReadOnlyBit_i_offset_c : natural := 2;
  constant MixedRegister_ReadOnlyBit_i_width_c : natural := 1;
  constant MixedRegister_DivByte1_i_offset_c : natural := 8;
  constant MixedRegister_DivByte1_i_width_c : natural := 8;
  constant MixedRegister_DivByte2_o_offset_c : natural := 16;
  constant MixedRegister_DivByte2_o_width_c : natural := 8;
  constant MixedRegister_DivByte3_i_offset_c : natural := 24;
  constant MixedRegister_DivByte3_i_width_c : natural := 8;
  constant ReadAWriteB_offset_c : unsigned(31 downto 0) := to_unsigned(6,32);
  constant ReadAWriteB_ReadAWriteB_i_offset_c : natural := 0;
  constant ReadAWriteB_ReadAWriteB_i_width_c : natural := 32;
type reg_i_t is record
  golden_golden_i : std_logic_vector(31 downto 0);
  set_MyWriteToClear_MyWriteToClear_i : std_logic_vector(31 downto 0);
  set_MixedRegister_Write2ClearBit_i : std_logic;
  clear_MixedRegister_Write2ClearBit_i : std_logic;
  MixedRegister_ReadOnlyBit_i : std_logic;
  set_MixedRegister_DivByte1_i : std_logic_vector(7 downto 0);
  MixedRegister_DivByte3_i : std_logic_vector(7 downto 0);
  ReadAWriteB_ReadAWriteB_i : std_logic_vector(31 downto 0);
  clear_MixedRegister_PulseBit_i : std_logic;
  clear_MixedRegister_ReadOnlyBit_i : std_logic;
end record reg_i_t;

type reg_o_t is record
  myReadWrite1_myReadWrite1_o : std_logic_vector(31 downto 0);
  myReadWrite2_myReadWrite2_o : std_logic_vector(31 downto 0);
  SlicedReg_pulse1_o : std_logic_vector(15 downto 0);
  SlicedReg_pulse2_o : std_logic_vector(15 downto 0);
  MixedRegister_PulseBit_o : std_logic;
  MixedRegister_DivByte2_o : std_logic_vector(7 downto 0);
  ReadAWriteB_ReadAWriteB_o : std_logic_vector(31 downto 0);
end record reg_o_t;

constant reg_i_init_c : reg_i_t := (
  golden_golden_i => (others => '0'),
  set_MyWriteToClear_MyWriteToClear_i => (others => '0'),
  set_MixedRegister_Write2ClearBit_i => '0',
  clear_MixedRegister_Write2ClearBit_i => '0',
  MixedRegister_ReadOnlyBit_i => '1',
  set_MixedRegister_DivByte1_i => (others => '0'),
  MixedRegister_DivByte3_i => (others => '0'),
  ReadAWriteB_ReadAWriteB_i => (others => '0'),
  clear_MixedRegister_PulseBit_i => '0',
  clear_MixedRegister_ReadOnlyBit_i => '0'
);

constant reg_o_init_c : reg_o_t := (
  myReadWrite1_myReadWrite1_o => (others => '0'),
  myReadWrite2_myReadWrite2_o => x"00000023",
  SlicedReg_pulse1_o => (others => '0'),
  SlicedReg_pulse2_o => (others => '0'),
  MixedRegister_PulseBit_o => '0',
  MixedRegister_DivByte2_o => (others => '0'),
  ReadAWriteB_ReadAWriteB_o => (others => '0')
);

end MyRegBank_pkg;

package body MyRegBank_pkg is


  -- Functions & Procedures
    -- subprograms_declaration_tag

end package body;

