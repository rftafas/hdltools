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
import copy
import hdltools.vhdl_gen as vhdl

tabsize = 2

class axiInfra(vhdl.BasicVHDL):
    def __init__(self, entity_name, master_num,m_tdata_byte,m_tdest_size,m_tuser_size,slave_num,s_tdata_byte,s_tdest_size,s_tuser_size):
        vhdl.BasicVHDL.__init__(self, entity_name, "axi_structural")
        self.master_num   = master_num
        self.m_tdata_byte = m_tdata_byte
        self.m_tdest_size = m_tdest_size
        self.m_tuser_size = m_tuser_size
        self.slave_num    = slave_num
        self.s_tdata_byte = s_tdata_byte
        self.s_tdest_size = s_tdest_size
        self.s_tuser_size = s_tuser_size

        self.library.add("IEEE")
        self.library["IEEE"].package.add("numeric_std")
        self.library.add("stdexpert")
        self.library["stdexpert"].package.add("std_logic_expert")

        self.entity.port.add("rst_i", "in", "std_logic")
        self.entity.port.add("mclk_i", "in", "std_logic")
        self._create_master_ports()
        self._create_slave_ports()

    def _create_master_ports(self):
        for j in range(self.master_num):
            self.entity.port.add("m%d_tdata_o " % j,"out","std_logic_vector(8*tdata_byte-1 downto 0)")
            self.entity.port.add("m%d_tstrb_o " % j,"out","std_logic_vector(tdata_byte-1   downto 0)")
            self.entity.port.add("m%d_tuser_o " % j,"out","std_logic_vector(tuser_size-1   downto 0)")
            self.entity.port.add("m%d_tdest_o " % j,"out","std_logic_vector(tdest_size-1   downto 0)")
            self.entity.port.add("m%d_tready_i" % j,"in ","std_logic)")
            self.entity.port.add("m%d_tvalid_o" % j,"out","std_logic)")
            self.entity.port.add("m%d_tlast_o " % j,"out","std_logic)")

        self.architecture.signal.add("m_tdata_s ","out","std_logic_matrix(%d downto 0)(%d downto 0)" % (self.master_num,8*self.m_tdata_byte-1) )
        self.architecture.signal.add("m_tstrb_s ","out","std_logic_matrix(%d downto 0)(%d downto 0)" % (self.master_num,self.m_tdata_byte-1) )
        self.architecture.signal.add("m_tuser_s ","out","std_logic_matrix(%d downto 0)(%d downto 0)" % (self.master_num,self.m_tuser_size-1) )
        self.architecture.signal.add("m_tdest_s ","out","std_logic_matrix(%d downto 0)(%d downto 0)" % (self.master_num,self.m_tdest_size-1) )
        self.architecture.signal.add("m_tready_s","in ","std_logic_vector(%d downto 0)" % self.master_num )
        self.architecture.signal.add("m_tvalid_s","out","std_logic_vector(%d downto 0)" % self.master_num )
        self.architecture.signal.add("m_tlast_s ","out","std_logic_vector(%d downto 0)" % self.master_num )

        for j in range(self.master_num):
            self.architecture.bodyCodeHeader.add("--Master %d" % j)
            self.architecture.bodyCodeHeader.add("m%d_tvalid_o <= m_tvalid_s(%d);"  % (j, j) )
            self.architecture.bodyCodeHeader.add("m%d_tlast_o  <= m_tlast_s(%d);"   % (j, j) )
            self.architecture.bodyCodeHeader.add("m_tready_s(%d) <= m%d_tready_i;" % (j, j) )
            self.architecture.bodyCodeHeader.add("m%d_tdata_o  <= m_tdata_s(%d);"   % (j, j) )
            self.architecture.bodyCodeHeader.add("m%d_tstrb_o  <= m_tstrb_s(%d);"   % (j, j) )
            self.architecture.bodyCodeHeader.add("m%d_tuser_o  <= m_tuser_s(%d);"   % (j, j) )
            self.architecture.bodyCodeHeader.add("m%d_tdest_o  <= m_tdest_s(%d);"   % (j, j) )
            self.architecture.bodyCodeHeader.add("")


    def _create_slave_ports(self):
        for j in range(self.slave_num):
            self.entity.port.add("s%d_tdata_i " % j,"in ","std_logic_vector(8*tdata_byte-1 downto 0)")
            self.entity.port.add("s%d_tstrb_i " % j,"in ","std_logic_vector(tdata_byte-1   downto 0)")
            self.entity.port.add("s%d_tuser_i " % j,"in ","std_logic_vector(tuser_size-1   downto 0)")
            self.entity.port.add("s%d_tdest_i " % j,"in ","std_logic_vector(tdest_size-1   downto 0)")
            self.entity.port.add("s%d_tready_o" % j,"out","std_logic")
            self.entity.port.add("s%d_tvalid_i" % j,"in ","std_logic")
            self.entity.port.add("s%d_tlast_i " % j,"in ","std_logic")

        self.architecture.signal.add("s_tdata_s ","in ","std_logic_matrix(%d downto 0)(%d downto 0)" % (self.slave_num,8*self.s_tdata_byte-1) )
        self.architecture.signal.add("s_tstrb_s ","in ","std_logic_matrix(%d downto 0)(%d downto 0)" % (self.slave_num,self.s_tdata_byte-1) )
        self.architecture.signal.add("s_tuser_s ","in ","std_logic_matrix(%d downto 0)(%d downto 0)" % (self.slave_num,self.s_tuser_size-1) )
        self.architecture.signal.add("s_tdest_s ","in ","std_logic_matrix(%d downto 0)(%d downto 0)" % (self.slave_num,self.s_tdest_size-1) )
        self.architecture.signal.add("s_tready_s","out","std_logic_vector(%d downto 0)" % self.slave_num)
        self.architecture.signal.add("s_tvalid_s","in ","std_logic_vector(%d downto 0)" % self.slave_num)
        self.architecture.signal.add("s_tlast_s ","in ","std_logic_vector(%d downto 0)" % self.slave_num)

        for j in range(self.slave_num):
            self.architecture.bodyCodeHeader.add("--Slave %d" % j)
            self.architecture.bodyCodeHeader.add("s_tvalid_s(%d) <= s%d_tvalid_i;"   % (j, j) )
            self.architecture.bodyCodeHeader.add("s_tlast_s(%d)  <= s%d_tlast_i;"    % (j, j) )
            self.architecture.bodyCodeHeader.add("s%d_tready_o   <= s_tready_s(%d);" % (j, j) )
            self.architecture.bodyCodeHeader.add("s_tdata_s(%d)  <= s%d_tdata_i;"    % (j, j) )
            self.architecture.bodyCodeHeader.add("s_tstrb_s(%d)  <= s%d_tstrb_i;"    % (j, j) )
            self.architecture.bodyCodeHeader.add("s_tuser_s(%d)  <= s%d_tuser_i;"    % (j, j) )
            self.architecture.bodyCodeHeader.add("s_tdest_s(%d)  <= s%d_tdest_i;"    % (j, j) )
            self.architecture.bodyCodeHeader.add("")


class axi_custom(axiInfra):
    def __init__(self, entity_name, master_num,m_tdata_byte,m_tdest_size,m_tuser_size,slave_num,s_tdata_byte,s_tdest_size,s_tuser_size):
        axiInfra.__init__(self, entity_name, master_num,m_tdata_byte,m_tdest_size,m_tuser_size,slave_num,s_tdata_byte,s_tdest_size,s_tuser_size)


class axi_concat(axiInfra):
    def __init__(self, entity_name, slave_num,s_tdata_byte,s_tdest_size,s_tuser_size):
        master_num = 1
        m_tdata_byte = slave_num * s_tdata_byte
        m_tdest_size = slave_num * s_tdest_size
        m_tuser_size = slave_num * s_tuser_size
        axiInfra.__init__(self, entity_name, master_num,m_tdata_byte,m_tdest_size,m_tuser_size,slave_num,s_tdata_byte,s_tdest_size,s_tuser_size)

        #internal aligner. We will not use anything beyond the port map.
        _aligner = vhdl.BasicVHDL("axis_aligner", "dont_care")
        _aligner.entity.generic.add("number_ports","positive","2")
        _aligner.entity.generic.add("tdata_byte","positive","8")
        _aligner.entity.generic.add("tdest_size","positive","8")
        _aligner.entity.generic.add("tuser_size","positive","8")
        _aligner.entity.generic.add("switch_on_tlast","boolean","false")

        _aligner.entity.port.add("clk_i","in","std_logic")
        _aligner.entity.port.add("rst_i","in","std_logic")
        _aligner.entity.port.add("m_tdata_o","out","std_logic_array (number_ports-1 downto 0)(8*tdata_byte-1 downto 0)")
        _aligner.entity.port.add("m_tuser_o","out","std_logic_array (number_ports-1 downto 0)(tuser_size-1 downto 0)")
        _aligner.entity.port.add("m_tdest_o","out","std_logic_array (number_ports-1 downto 0)(tdest_size-1 downto 0)")
        _aligner.entity.port.add("m_tstrb_o","out","std_logic_array (number_ports-1 downto 0)(tdata_byte-1 downto 0)")
        _aligner.entity.port.add("m_tready_i","in","std_logic_vector(number_ports-1 downto 0)")
        _aligner.entity.port.add("m_tvalid_o","out","std_logic_vector(number_ports-1 downto 0)")
        _aligner.entity.port.add("m_tlast_o","out","std_logic_vector(number_ports-1 downto 0)")
        _aligner.entity.port.add("s_tdata_i","in","std_logic_array (number_ports-1 downto 0)(8*tdata_byte-1 downto 0)")
        _aligner.entity.port.add("s_tuser_i","in","std_logic_array (number_ports-1 downto 0)(tuser_size-1 downto 0)")
        _aligner.entity.port.add("s_tdest_i","in","std_logic_array (number_ports-1 downto 0)(tdest_size-1 downto 0)")
        _aligner.entity.port.add("s_tstrb_i","in","std_logic_array (number_ports-1 downto 0)(tdata_byte-1 downto 0)")
        _aligner.entity.port.add("s_tready_o","out","std_logic_vector(number_ports-1 downto 0)")
        _aligner.entity.port.add("s_tvalid_i","in", "std_logic_vector(number_ports-1 downto 0)")
        _aligner.entity.port.add("s_tlast_i ","in", "std_logic_vector(number_ports-1 downto 0)")

        self.architecture.component.append(_aligner.object())
        instance_1 = _aligner.instanciation("aligner_a")
        instance_2 = copy.deepcopy(_aligner.instanciation("aligner_b"))

        #self.architecture.instances.append(_aligner.instanciation("aligner_a"))
        #self.architecture.instances.append(_aligner.instanciation("aligner_b"))

        print(instance_1)
        print(instance_2)

test = axi_concat("teste",2,8,8,8)
#print(test.code())
sys.exit()

# class axis_mux (axiInfra):
#     #check for axis_concat existance
#     output_file_name = "output/"+entity_name+".vhd"
#     output_file = open(output_file_name,"w+")

#     concat_source = open("templates/axis_mux.vhd","r")
#     code_lines = concat_source.readlines()

#     for line in code_lines:
#         if ("entity axis_mux is" in line):
#             output_file.write("entity %s is\r\n" % entity_name)
#         elif ("end axis_mux;" in line):
#             output_file.write("end %s;\r\n" % entity_name)
#         elif ("architecture" in line):
#             output_file.write("architecture behavioral of %s is\r\n" % entity_name)
#         elif ("--python port code" in line):
#             output_file.write(create_axis_port("s","slave",number_elements,3))
#         elif ("--python constant code" in line):
#             output_file.write("  constant number_ports : integer := %d;\r\n" % number_elements)
#         elif ("--array connections" in line):
#             for j in range(number_elements):
#                 output_file.write(indent(1)+"s_tvalid_s(%d) <= s%d_tvalid_i;\r\n" % (j, j))

#             output_file.write("\r\n")
#             for j in range(number_elements):
#                 output_file.write(indent(1)+"s_tlast_s(%d)  <= s%d_tlast_i;\r\n" % (j, j))

#             output_file.write("\r\n")
#             for j in range(number_elements):
#                 output_file.write(indent(1)+"axi_tdata_s(%d) <= s%d_tdata_i;\r\n" % (j,j))
#                 output_file.write(indent(1)+"axi_tuser_s(%d) <= s%d_tuser_i;\r\n" % (j,j))
#                 output_file.write(indent(1)+"axi_tdest_s(%d) <= s%d_tdest_i;\r\n" % (j,j))

#         elif ("--ready connections" in line):
#             for j in range(number_elements):
#                 output_file.write(indent(1)+"s%d_tready_o   <= s_tready_s(%d) and m_tready_i;\r\n" % (j,j))

#         else:
#             output_file.write(line)

def axis_demux ( entity_name, number_elements):
    #check for axis_concat existance
    output_file_name = "output/"+entity_name+".vhd"
    output_file = open(output_file_name,"w+")

    concat_source = open("templates/axis_demux.vhd","r")
    code_lines = concat_source.readlines()

    for line in code_lines:
        if ("entity axis_demux is" in line):
            output_file.write("entity %s is\r\n" % entity_name)
        elif ("end axis_demux;" in line):
            output_file.write("end %s;\r\n" % entity_name)
        elif ("architecture" in line):
            output_file.write("architecture behavioral of %s is\r\n" % entity_name)
        elif ("--python port code" in line):
            output_file.write(create_axis_port("m","master",number_elements,3))
        elif ("--python constant code" in line):
            output_file.write("  constant number_masters : integer := %d;\r\n" % number_elements)
        elif ("--array connections" in line):
            output_file.write(create_port_connection("m","master",number_masters,1))
        else:
            output_file.write(line)
    return True;

def axis_aligner ( entity_name, number_elements):
    #check for axis_concat existance
    output_file_name = "output/"+entity_name+".vhd"
    output_file = open(output_file_name,"w+")

    concat_source = open("templates/axis_aligner.vhd","r")
    code_lines = concat_source.readlines()

    for line in code_lines:
        if ("entity axis_aligner is" in line):
            output_file.write("entity %s is\r\n" % entity_name)
        elif ("end axis_aligner;" in line):
            output_file.write("end %s;\r\n" % entity_name)
        elif ("architecture" in line):
            output_file.write("architecture behavioral of %s is\r\n" % entity_name)
        elif ("--python port code" in line):
            output_file.write(indent(1)+create_axis_port("m","master",number_elements,3))
            output_file.write(indent(1)+create_axis_port("s","slave",number_elements,3))
        elif ("--python constant code" in line):
            output_file.write("  constant number_ports : integer := %d;\r\n" % number_elements)
        elif ("--array connections" in line):
            for j in range(number_elements):
                output_file.write(indent(3)+"s_tvalid_s(%d) <= s%d_tvalid_i;\r\n" % (j, j))

            output_file.write("\r\n")
            for j in range(number_elements):
                output_file.write(indent(3)+"s_tlast_s(%d)  <= s%d_tlast_i;\r\n" % (j, j))

            output_file.write("\r\n")
            for j in range(number_elements):
                output_file.write(indent(3)+"axi_tdata_s(%d) <= s%d_tdata_i;\r\n" % (j,j))
                output_file.write(indent(3)+"axi_tuser_s(%d) <= s%d_tuser_i;\r\n" % (j,j))
                output_file.write(indent(3)+"axi_tdest_s(%d) <= s%d_tdest_i;\r\n" % (j,j))

        elif ("--python signal connections" in line):
            output_file.write(create_port_connection("m","master",number_elements,1))
            output_file.write(create_port_connection("s","slaves",number_elements,1))

        else:
            output_file.write(line)
    return True;

def axis_intercon ( entity_name, number_slaves, number_masters):
    #first we create inernal needed block.
    internal_name = entity_name+"_mux"
    if (not axis_mux(internal_name,number_slaves)):
        print("Error, cannot create internal mux.\r\n")
        sys.exit()
    internal_name = entity_name+"_demux"
    if (not axis_demux(internal_name,number_masters)):
        print("Error, cannot create internal demux.\r\n")
        sys.exit()

    output_file_name = "output/"+entity_name+".vhd"
    output_file = open(output_file_name,"w+")

    concat_source = open("templates/axis_intercon.vhd","r")

    code_lines = concat_source.readlines()

    for line in code_lines:
        if ("entity axis_intercon is" in line):
            output_file.write("entity %s is\r\n" % entity_name)
        elif ("end axis_intercon;" in line):
            output_file.write("end %s;\r\n" % entity_name)
        elif ("architecture" in line):
            output_file.write("architecture behavioral of %s is\r\n" % entity_name)
        elif ("--python port code" in line):
            output_file.write(create_axis_port("m","master",number_masters,3))
            output_file.write(create_axis_port("s","slave",number_slaves,3))
        elif ("component axis_demux is" in line):
            output_file.write(indent(1)+"component %s_demux is\r\n" % entity_name)
        elif ("component axis_mux is" in line):
            output_file.write(indent(1)+"component %s_mux is\r\n" % entity_name)
        elif ("--number of mux ports" in line):
            output_file.write(create_axis_port("s","slave",number_slaves,3))
        elif ("--number of demux ports" in line):
            output_file.write(create_axis_port("m","master",number_masters,3))
        elif ("--python constant code" in line):
            output_file.write("  constant number_masters : integer := %d;\r\n" % number_masters)
            output_file.write("  constant number_slaves  : integer := %d;\r\n" % number_slaves)
        elif ("--signal creation" in line):
            for j in range(number_masters):
                output_file.write(create_axis_signal("demux%s" % j, "number_slaves", 1))
            output_file.write("\r\n")
            for j in range(number_slaves):
                output_file.write(create_axis_signal("mux%s" % j, "number_masters", 1))
        elif ("--array connections" in line):
            output_file.write(create_port_connection("m","master",number_masters,1))
            output_file.write(create_port_connection("s","slave",number_slaves,1))
            for j in range(number_masters):
                for k in range(number_slaves):
                    output_file.write(create_signal_connection("demux%s" % j,"(%s)" % k,"mux%s" % k,"(%s)" % j,1))
        elif ("axis_mux_u : axis_mux" in line):
            output_file.write(indent(2)+"%s_mux_u : %s_mux\r\n" % (entity_name,entity_name))
        elif ("axis_demux_u : axis_demux" in line):
            output_file.write(indent(2)+"%s_demux_u : %s_demux\r\n" % (entity_name,entity_name))
        elif ("--mux instance" in line):
            for j in range(number_slaves):
                output_file.write(create_instance_connection("s%s" % j,"mux%s" % j,"(j)","slave",4))
        elif ("--demux instance" in line):
            for j in range(number_masters):
                output_file.write(create_instance_connection("m%s" % j,"demux%s" % j,"(j)","master",4))
        else:
            output_file.write(line)
    return True;

def axis_broadcast ( entity_name, number_masters):

    output_file_name = "output/"+entity_name+".vhd"
    output_file = open(output_file_name,"w+")

    concat_source = open("templates/axis_broadcast.vhd","r")


    code_lines = concat_source.readlines()

    for line in code_lines:
        if ("entity axis_broadcast is" in line):
            output_file.write("entity %s is\r\n" % entity_name)
        elif ("end axis_broadcast;" in line):
            output_file.write("end %s;\r\n" % entity_name)
        elif ("architecture" in line):
            output_file.write("architecture behavioral of %s is\r\n" % entity_name)
        elif ("--python port code" in line):
            output_file.write(create_axis_port("m","master",number_masters,3))
        elif ("--component slaves port code" in line):
            output_file.write(indent(4)+create_axis_port("m","master",number_masters,4))
        elif ("--python constant code" in line):
            output_file.write("  constant number_masters : integer := %d;\r\n" % number_masters)
        elif ("--array connections" in line):
            output_file.write(create_port_connection("m","master",number_masters,1))
        else:
            output_file.write(line)
    return True;

def error_help():
    print("plase, select a valid option. Current available:\r\n")
    print("'custom'      : create axi empty block with master and slave ports.\r\n")
    print("'concat'      : create axi concatenation block. Makes two sync streams into one.\r\n")
    print("'switch'      : create an automatic AXI switch endine. Selects from various sources.\r\n")
    print("'aligner'     : forces early channels wait for late channels.\r\n")
    print("'intercon'    : AXI-S interconnect. TDEST based.\r\n")
    print("'broadcast'   : Copy slave stream data to several masters.\r\n")
    print("Usage: python axi-build.py <option> <entity name> <command paramenter>\r\n")
    print("Example: python axi-build.py concat my_concat_block 3\r\n")
    sys.exit()

####################################################################################################
# Application Menu
####################################################################################################
try:
    command = sys.argv[1]
except:
    error_help()

try:
    entity_name = sys.argv[2]
except:
    error_help()

if (command == "custom"):
    try:
        entity_name = sys.argv[2]
        number_slaves = int(sys.argv[3])
        number_masters = int(sys.argv[4])
    except:
        print("Something is missing.\r\n")
        print("python axi-build.py custom <entity name> <number of slaves> <number of masters>\r\n")
        sys.exit()
elif (command == "concat"):
    try:
        entity_name = sys.argv[2]
        number_masters = int(sys.argv[3])
    except:
        print("Something is missing.\r\n")
        print("python axi-build.py concat <entity name> <number of slaves>\r\n")
        sys.exit()
elif (command == "mux"):
    try:
        entity_name = sys.argv[2]
        number_slaves = int(sys.argv[3])
    except:
        print("Something is missing.\r\n")
        print("python axi-build.py mux <entity name> <number of slaves>\r\n")
        sys.exit()
elif (command == "demux"):
    try:
        entity_name = sys.argv[2]
        number_masters = int(sys.argv[3])
    except:
        print("Something is missing.\r\n")
        print("python axi-build.py demux <entity name> <number of masters>\r\n")
        sys.exit()
elif (command == "aligner"):
    try:
        entity_name = sys.argv[2]
        number_slaves = int(sys.argv[3])
    except:
        print("Something is missing.\r\n")
        print("python axi-build.py aligner <entity name> <number of ports>\r\n")
        sys.exit()
elif (command == "intercon"):
    try:
        entity_name = sys.argv[2]
        number_slaves = int(sys.argv[3])
        number_masters = int(sys.argv[4])
    except:
        print("Something is missing.\r\n")
        print("python axi-build.py intercon <entity name> <number of slaves> <number of masters>\r\n")
        sys.exit()
elif (command == "broadcast"):
    try:
        entity_name = sys.argv[2]
        number_masters = int(sys.argv[3])
    except:
        print("Something is missing.\r\n")
        print("python axi-build.py broadcast <entity name> <number of masters>\r\n")
        sys.exit()
else:
    print("Command not supported or yet to be implemented.")
    error_help()

# if success:
#     print("# Copyright 2020 Ricardo F Tafas Jr\r\n")
#     print("#\r\n"
#     print("# Licensed under the Apache License, Version 2.0 (the "License"); you may not\r\n"
#     print("# use this file except in compliance with the License. You may obtain a copy of\r\n"
#     print("# the License at:\r\n"
#     print("#\r\n"
#     print("#    http://www.apache.org/licenses/LICENSE-2.0\r\n"
#     print("#\r\n"
#     print("# Unless required by applicable law or agreed to in writing, software distributed\r\n"
#     print("# under the License is distributed on an \"AS IS\" BASIS, WITHOUT WARRANTIES\r\n"
#     print("# OR CONDITIONS OF ANY KIND, either express or implied. See the License for\r\n"
#     print("# the specific language governing permissions and limitations under the License.\r\n"
#     print("-----------------------------------------------------------------------------------\r\n")
#     print("-- You can download more VHDL stuff at https://github.com/rftafas\r\n")
#     print("-- output at otuput/"+entity_name+".vhd\r\n")
#     print("-- \r\n")
#     print("-- Do not forget to add all contents on dependencies folder by doing:\r\n")
#     print("-- git submodule update --init --recursive\r\n")
#     print("---------------------------------------------------------------------------------------")
sys.exit()
