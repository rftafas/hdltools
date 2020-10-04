#################################################################################
# Copyright 2020 Ricardo F Tafas Jr

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
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from ...scripts import vhdl_gen

ram = vhdl_gen.BasicVHDL("ram","behavioral")
ram.Library.add("IEEE")
ram.Library["IEEE"].package.add("numeric_std")
ram.Library.add("stdexpert")
ram.Library["stdexpert"].package.add("std_logic_expert")

if len(sys.argv) > 1:
    addr_size = str(sys.argv[1] - 1)
    mem_size = str(2**addr_size - 1)
    print("Adress Size is %s", addr_size)
else:
    addr_size = "addr_size - 1"
    mem_size = "2**addr_size - 1"
    ram.Entity.generic.add("addr_size", "integer", "8")

if len(sys.argv) > 2:
    data_size = str(sys.argv[2] - 1)
    print("Data Size is %s", data_size)
else:
    data_size = "data_size - 1"
    ram.Entity.generic.add("data_size", "integer", "8")

ram.Entity.port.add("rst_i", "in", "std_logic")
ram.Entity.port.add("clk_i", "in", "std_logic")
ram.Entity.port.add("we_i", "in", "std_logic")
ram.Entity.port.add("data_i", "in", ("std_logic_vector(%s downto 0)" , data_size))
ram.Entity.port.add("data_o", "out", ("std_logic_vector(%s downto 0)" , data_size))
ram.Entity.port.add("addr_i", "in", ("std_logic_vector(%s downto 0)" , addr_size))
ram.Entity.port.add("addr_o", "in", ("std_logic_vector(%s downto 0)" , addr_size))

ram.Architecture.DeclarationHeader.add(("type ram_t is array (%s downto 0) of std_logic_vector(%s downto 0)" % (mem_size,data_size)))

ram.Architecture.Signal.add("ram_s", "ram_t")
ram.Architecture.DeclarationFooter.add("--Test adding custom declarative code.")
ram.Architecture.BodyCodeFooter.add("ram_p : process(all)")
ram.Architecture.BodyCodeFooter.add("begin")
ram.Architecture.BodyCodeFooter.add("  if rising_edge(clk_i) then")
ram.Architecture.BodyCodeFooter.add("    if we_i = '1' then")
ram.Architecture.BodyCodeFooter.add("      ram_s(to_integer(addr_i)) <= data_i;")
ram.Architecture.BodyCodeFooter.add("    end if;")
ram.Architecture.BodyCodeFooter.add("    data_o <= ram_s(to_integer(addr_o));")
ram.Architecture.BodyCodeFooter.add("  end if;")
ram.Architecture.BodyCodeFooter.add("end process;")

print ("----------------file starts--------------------")
print (ram.code())
print ("----------------file ends--------------------")
ram.write_file()
