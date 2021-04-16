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

import hdltools

ram = hdltools.BasicVHDL("ram","behavioral")
ram.library.add("IEEE")
ram.library["IEEE"].package.add("numeric_std")
ram.library.add("stdexpert")
ram.library["stdexpert"].package.add("std_logic_expert")

if len(sys.argv) > 1:
    addr_size = str(sys.argv[1] - 1)
    mem_size = str(2**addr_size - 1)
    print("Adress Size is %s", addr_size)
else:
    addr_size = "addr_size - 1"
    mem_size = "2**addr_size - 1"
    ram.entity.generic.add("addr_size", "integer", "8")

if len(sys.argv) > 2:
    data_size = str(sys.argv[2] - 1)
    print("Data Size is %s", data_size)
else:
    data_size = "data_size - 1"
    ram.entity.generic.add("data_size", "integer", "8")

ram.entity.port.add("rst_i", "in", "std_logic")
ram.entity.port.add("clk_i", "in", "std_logic")
ram.entity.port.add("we_i", "in", "std_logic")
ram.entity.port.add("data_i", "in", ("std_logic_vector(%s downto 0)" , data_size))
ram.entity.port.add("data_o", "out", ("std_logic_vector(%s downto 0)" , data_size))
ram.entity.port.add("addr_i", "in", ("std_logic_vector(%s downto 0)" , addr_size))
ram.entity.port.add("addr_o", "in", ("std_logic_vector(%s downto 0)" , addr_size))

ram.architecture.declarationHeader.add(("type ram_t is array (%s downto 0) of std_logic_vector(%s downto 0)" % (mem_size,data_size)))

ram.architecture.signal.add("ram_s", "ram_t")
ram.architecture.declarationFooter.add("--Test adding custom declarative code.")
ram.architecture.bodyCodeFooter.add("ram_p : process(all)")
ram.architecture.bodyCodeFooter.add("begin")
ram.architecture.bodyCodeFooter.add("  if rising_edge(clk_i) then")
ram.architecture.bodyCodeFooter.add("    if we_i = '1' then")
ram.architecture.bodyCodeFooter.add("      ram_s(to_integer(addr_i)) <= data_i;")
ram.architecture.bodyCodeFooter.add("    end if;")
ram.architecture.bodyCodeFooter.add("    data_o <= ram_s(to_integer(addr_o));")
ram.architecture.bodyCodeFooter.add("  end if;")
ram.architecture.bodyCodeFooter.add("end process;")

print ("----------------file starts--------------------")
print (ram.code())
print ("----------------file ends--------------------")
ram.write_file()
