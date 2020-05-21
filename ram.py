import sys
import os
import vhdl_gen

ram = vhdl_gen.vhdl_file("ram","behavioral")
ram.library.add("IEEE")
ram.library.list[0].package.add("numeric_std")
ram.entity.generic.add("addr_size", "integer", "8")
ram.entity.generic.add("data_size", "integer", "8")
ram.entity.port.add("data", "in", "std_logic_vector(data_size-1 downto 0)")
ram.entity.port.add("addr", "in", "std_logic_vector(addr_size-1 downto 0)")
ram.architecture.constant.add("delay", "integer", "0")
ram.architecture.signal.add("dout_s", "std_logic_vector(addr_size-1 downto 0)", "")
ram.architecture.signal.add("ram_s", "ram_t", "")
ram.architecture.declaration_code = "  --Test adding custom declarative code."
ram.architecture.body_code = "  --Test adding custom body code."

print "----------------file starts--------------------"
print ram.code()
ram.write_file()
