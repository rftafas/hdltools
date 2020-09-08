import sys
import os

tabsize = 2

def indent(value):
    txt = ""
    for j in range(tabsize * value):
        txt = txt + " "
    return txt;

def create_axis_port( port_name, type, number, indsize):
    code = ""
    if ("master" in type):
        for j in range(number):
            code = code + indent(indsize) + ("--AXIS Master Port %d\r\n" % j)
            code = code + indent(indsize) + port_name + ("%d_tdata_o    : out std_logic_vector(tdata_size-1 downto 0);\r\n" % j)
            code = code + indent(indsize) + port_name + ("%d_tuser_o    : out std_logic_vector(tuser_size-1 downto 0);\r\n" % j)
            code = code + indent(indsize) + port_name + ("%d_tdest_o    : out std_logic_vector(tdest_size-1 downto 0);\r\n" % j)
            code = code + indent(indsize) + port_name + ("%d_tready_i   : in  std_logic;\r\n" % j)
            code = code + indent(indsize) + port_name + ("%d_tvalid_o   : out std_logic;\r\n" % j)
            code = code + indent(indsize) + port_name + ("%d_tlast_o    : out std_logic;\r\n" % j)
    else :
        for j in range(number):
            code = code + indent(indsize) + ("--AXIS Slave Port %d\r\n" % j)
            code = code + indent(indsize) + port_name + ("%d_tdata_i  : in  std_logic_vector(tdata_size-1 downto 0);\r\n" % j)
            code = code + indent(indsize) + port_name + ("%d_tuser_i  : in  std_logic_vector(tuser_size-1 downto 0);\r\n" % j)
            code = code + indent(indsize) + port_name + ("%d_tdest_i  : in  std_logic_vector(tdest_size-1 downto 0);\r\n" % j)
            code = code + indent(indsize) + port_name + ("%d_tready_o : out std_logic;\r\n" % j)
            code = code + indent(indsize) + port_name + ("%d_tvalid_i : in  std_logic;\r\n" % j)
            code = code + indent(indsize) + port_name + ("%d_tlast_i  : in  std_logic;\r\n" % j)
    return code

def create_axis_signal( signal_name, size, indsize):
    code = ""
    code = code + indent(indsize) + ("signal %s_tdata_s  :  axi_tdata_array(%s-1 downto 0);\r\n" % (signal_name,size))
    code = code + indent(indsize) + ("signal %s_tuser_s  :  axi_tuser_array(%s-1 downto 0);\r\n" % (signal_name,size))
    code = code + indent(indsize) + ("signal %s_tdest_s  :  axi_tdest_array(%s-1 downto 0);\r\n" % (signal_name,size))
    code = code + indent(indsize) + ("signal %s_tvalid_s : std_logic_vector(%s-1 downto 0);\r\n" % (signal_name,size))
    code = code + indent(indsize) + ("signal %s_tlast_s  : std_logic_vector(%s-1 downto 0);\r\n" % (signal_name,size))
    code = code + indent(indsize) + ("signal %s_tready_s : std_logic_vector(%s-1 downto 0);\r\n" % (signal_name,size))
    return code

def create_port_connection( port_name, type, number_elements, indsize):
    code = ""
    if ("slave" in type):
        code = code + indent(indsize) + ("--Slave Connections\r\n")
        for j in range(number_elements):
            code = code + indent(indsize) + ("--Slave %d\r\n" % j)
            code = code + indent(indsize) + ("s_tvalid_s(%d) <= %s%d_tvalid_i;\r\n"   % (j, port_name, j))
            code = code + indent(indsize) + ("s_tlast_s(%d)  <= %s%d_tlast_i;\r\n"    % (j, port_name, j))
            code = code + indent(indsize) + ("%s%d_tready_o  <= s_tready_s(%d);\r\n" % (port_name, j, j))
            code = code + indent(indsize) + ("s_tdata_s(%d)  <= %s%d_tdata_i;\r\n"    % (j, port_name, j))
            code = code + indent(indsize) + ("s_tuser_s(%d)  <= %s%d_tuser_i;\r\n"    % (j, port_name, j))
            code = code + indent(indsize) + ("s_tdest_s(%d)  <= %s%d_tdest_i;\r\n"    % (j, port_name, j))
            code = code + indent(indsize) + ("\r\n")
    else:
        code = code + indent(indsize)+("--Master Connections\r\n")
        for j in range(number_elements):
            code = code + indent(indsize) + ("--Master %d\r\n" % j)
            code = code + indent(indsize) + ("%s%d_tvalid_o <= m_tvalid_s(%d);\r\n" % (port_name, j, j))
            code = code + indent(indsize) + ("%s%d_tlast_o  <= m_tlast_s(%d);\r\n"  % (port_name, j, j))
            code = code + indent(indsize) + ("m_tready_s(%d) <= %s%d_tready_i;\r\n"   % (j, port_name, j))
            code = code + indent(indsize) + ("%s%d_tdata_o  <= m_tdata_s(%d);\r\n"  % (port_name, j, j))
            code = code + indent(indsize) + ("%s%d_tuser_o  <= m_tuser_s(%d);\r\n"  % (port_name, j, j))
            code = code + indent(indsize) + ("%s%d_tdest_o  <= m_tdest_s(%d);\r\n"  % (port_name, j, j))
            code = code + indent(indsize) + ("\r\n")
    return code

def create_instance_connection( port_name, signal_name, signal_sufix, type, indsize):
    code = ""
    if ("slave" in type):
        code = code + indent(indsize) + ("--Slave %s\r\n" % port_name)
        code = code + indent(indsize) + ("%s_tvalid_i => %s_tvalid_s%s,\r\n" % (port_name, signal_name, signal_sufix))
        code = code + indent(indsize) + ("%s_tlast_i  =>  %s_tlast_s%s,\r\n" % (port_name, signal_name, signal_sufix))
        code = code + indent(indsize) + ("%s_tready_o => %s_tready_s%s,\r\n" % (port_name, signal_name, signal_sufix))
        code = code + indent(indsize) + ("%s_tdata_i  =>  %s_tdata_s%s,\r\n" % (port_name, signal_name, signal_sufix))
        code = code + indent(indsize) + ("%s_tuser_i  =>  %s_tuser_s%s,\r\n" % (port_name, signal_name, signal_sufix))
        code = code + indent(indsize) + ("%s_tdest_i  =>  %s_tdest_s%s,\r\n" % (port_name, signal_name, signal_sufix))
        code = code + indent(indsize) + ("\r\n")
    else:
        code = code + indent(indsize) + ("--Master %s\r\n" % port_name)
        code = code + indent(indsize) + ("%s_tvalid_o => %s_tvalid_s%s,\r\n" % (port_name, signal_name, signal_sufix))
        code = code + indent(indsize) + ("%s_tlast_o  =>  %s_tlast_s%s,\r\n" % (port_name, signal_name, signal_sufix))
        code = code + indent(indsize) + ("%s_tready_i => %s_tready_s%s,\r\n" % (port_name, signal_name, signal_sufix))
        code = code + indent(indsize) + ("%s_tdata_o  =>  %s_tdata_s%s,\r\n" % (port_name, signal_name, signal_sufix))
        code = code + indent(indsize) + ("%s_tuser_o  =>  %s_tuser_s%s,\r\n" % (port_name, signal_name, signal_sufix))
        code = code + indent(indsize) + ("%s_tdest_o  =>  %s_tdest_s%s,\r\n" % (port_name, signal_name, signal_sufix))
        code = code + indent(indsize) + ("\r\n")
    return code

def create_signal_connection( signala_name, signala_sufix, signalb_name, signalb_sufix, indsize):
    code = ""
    code = code + indent(indsize) + ("--Connext %s to %s\r\n" % (signala_name,signalb_name))
    code = code + indent(indsize) + ("%s_tvalid_s%s <= %s_tvalid_s%s;\r\n" % (signala_name, signala_sufix, signalb_name, signalb_sufix))
    code = code + indent(indsize) + ("%s_tlast_s%s  <=  %s_tlast_s%s;\r\n" % (signala_name, signala_sufix, signalb_name, signalb_sufix))
    code = code + indent(indsize) + ("%s_tready_s%s <= %s_tready_s%s;\r\n" % (signalb_name, signalb_sufix, signala_name, signala_sufix))
    code = code + indent(indsize) + ("%s_tdata_s%s  <=  %s_tdata_s%s;\r\n" % (signala_name, signala_sufix, signalb_name, signalb_sufix))
    code = code + indent(indsize) + ("%s_tuser_s%s  <=  %s_tuser_s%s;\r\n" % (signala_name, signala_sufix, signalb_name, signalb_sufix))
    code = code + indent(indsize) + ("%s_tdest_s%s  <=  %s_tdest_s%s;\r\n" % (signala_name, signala_sufix, signalb_name, signalb_sufix))
    code = code + indent(indsize) + ("\r\n")
    return code

def axi_custom( entity_name, number_slaves, number_masters):
    #check for axis_concat existance
    output_file_name = "output/"+entity_name+".vhd"
    output_file = open(output_file_name,"w+")

    concat_source = open("templates/axis_custom.vhd","r")
    code_lines = concat_source.readlines()

    for line in code_lines:
        if ("entity axi_custom is" in line):
            output_file.write("entity %s is\r\n" % entity_name)
        elif ("end axi_custom;" in line):
            output_file.write("end %s;\r\n" % entity_name)
        elif ("architecture" in line):
            output_file.write("architecture behavioral of %s is\r\n" % entity_name)
        elif ("--python port code" in line):
            output_file.write(create_axis_port("s","slave",number_slaves,3))
            output_file.write(create_axis_port("m","master",number_masters,3))
        elif ("--python constant code" in line):
            output_file.write(indent(1)+"constant number_slaves  : integer := %d;\r\n" % number_slaves)
            output_file.write(indent(1)+"constant number_masters : integer := %d;\r\n" % number_masters)
        elif ("--python signal connections" in line):
            output_file.write(create_port_connection("m","master",number_masters,1))
            output_file.write(create_port_connection("s","slaves",number_slaves,1))
        else:
            output_file.write(line)
    return True;

def axi_concat( entity_name, number_elements):
    #check for axis_concat existance
    output_file_name = "output/"+entity_name+".vhd"
    output_file = open(output_file_name,"w+")

    concat_source = open("templates/axis_concat.vhd","r")
    code_lines = concat_source.readlines()

    for line in code_lines:
        if ("entity axis_concat is" in line):
            output_file.write("entity %s is\r\n" % entity_name)
        elif ("end axis_concat;" in line):
            output_file.write("end %s;\r\n" % entity_name)
        elif ("architecture" in line):
            output_file.write("architecture behavioral of %s is\r\n" % entity_name)
        elif ("--python port code" in line):
            output_file.write(create_axis_port("s","slave",number_elements,3))
            output_file.write(indent(3)+"--AXIS Master Port\r\n")
            output_file.write(indent(3)+"m_tdata_o    : out std_logic_vector(%d*tdata_size-1 downto 0);\r\n" % number_elements)
            output_file.write(indent(3)+"m_tuser_o    : out std_logic_vector(%d*tuser_size-1 downto 0);\r\n" % number_elements)
            output_file.write(indent(3)+"m_tdest_o    : out std_logic_vector(%d*tdest_size-1 downto 0);\r\n" % number_elements)
        elif ("--python constant code" in line):
            output_file.write(indent(1)+"constant number_ports : integer := %d;\r\n" % number_elements)
        elif ("--python signal connections" in line):
            for j in range(number_elements):
                output_file.write(indent(2)+"s_tvalid_s(%d) <= s%d_tvalid_i;\r\n" % (j, j))

            output_file.write("\r\n")
            for j in range(number_elements):
                output_file.write(indent(2)+"s_tlast_s(%d)  <= s%d_tlast_i;\r\n" % (j, j))

            output_file.write("\r\n")
            for j in range(number_elements):
                output_file.write(indent(2)+"s%d_tready_o   <= m_tready_i;\r\n" % j)

            output_file.write("\r\n")
            for j in range(number_elements):
                output_file.write(indent(2)+"axi_tdata_s(%d) <= s%d_tdata_i;\r\n" % (j,j))
                output_file.write(indent(2)+"axi_tuser_s(%d) <= s%d_tuser_i;\r\n" % (j,j))
                output_file.write(indent(2)+"axi_tdest_s(%d) <= s%d_tdest_i;\r\n" % (j,j))
        else:
            output_file.write(line)
    return True;

def axis_mux ( entity_name, number_elements):
    #check for axis_concat existance
    output_file_name = "output/"+entity_name+".vhd"
    output_file = open(output_file_name,"w+")

    concat_source = open("templates/axis_mux.vhd","r")
    code_lines = concat_source.readlines()

    for line in code_lines:
        if ("entity axis_mux is" in line):
            output_file.write("entity %s is\r\n" % entity_name)
        elif ("end axis_mux;" in line):
            output_file.write("end %s;\r\n" % entity_name)
        elif ("architecture" in line):
            output_file.write("architecture behavioral of %s is\r\n" % entity_name)
        elif ("--python port code" in line):
            output_file.write(create_axis_port("s","slave",number_elements,3))
        elif ("--python constant code" in line):
            output_file.write("  constant number_ports : integer := %d;\r\n" % number_elements)
        elif ("--array connections" in line):
            for j in range(number_elements):
                output_file.write(indent(1)+"s_tvalid_s(%d) <= s%d_tvalid_i;\r\n" % (j, j))

            output_file.write("\r\n")
            for j in range(number_elements):
                output_file.write(indent(1)+"s_tlast_s(%d)  <= s%d_tlast_i;\r\n" % (j, j))

            output_file.write("\r\n")
            for j in range(number_elements):
                output_file.write(indent(1)+"axi_tdata_s(%d) <= s%d_tdata_i;\r\n" % (j,j))
                output_file.write(indent(1)+"axi_tuser_s(%d) <= s%d_tuser_i;\r\n" % (j,j))
                output_file.write(indent(1)+"axi_tdest_s(%d) <= s%d_tdest_i;\r\n" % (j,j))

        elif ("--ready connections" in line):
            for j in range(number_elements):
                output_file.write(indent(1)+"s%d_tready_o   <= s_tready_s(%d) and m_tready_i;\r\n" % (j,j))

        else:
            output_file.write(line)
    return True;

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
if not os.path.exists("output"):
    os.mkdir("output")

try:
    command = sys.argv[1]
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
    success = axi_custom( entity_name, number_slaves, number_masters)
elif (command == "concat"):
    try:
        entity_name = sys.argv[2]
        number_masters = int(sys.argv[3])
    except:
        print("Something is missing.\r\n")
        print("python axi-build.py concat <entity name> <number of slaves>\r\n")
        sys.exit()
    success = axi_concat(entity_name,number_slaves)
elif (command == "mux"):
    try:
        entity_name = sys.argv[2]
        number_slaves = int(sys.argv[3])
    except:
        print("Something is missing.\r\n")
        print("python axi-build.py mux <entity name> <number of slaves>\r\n")
        sys.exit()
    success = axis_mux(entity_name,number_slaves)
elif (command == "demux"):
    try:
        entity_name = sys.argv[2]
        number_masters = int(sys.argv[3])
    except:
        print("Something is missing.\r\n")
        print("python axi-build.py demux <entity name> <number of masters>\r\n")
        sys.exit()
    success = axis_demux(entity_name,number_masters)
elif (command == "aligner"):
    try:
        entity_name = sys.argv[2]
        number_slaves = int(sys.argv[3])
    except:
        print("Something is missing.\r\n")
        print("python axi-build.py aligner <entity name> <number of ports>\r\n")
        sys.exit()
    success = axis_aligner(entity_name,number_slaves)
elif (command == "intercon"):
    try:
        entity_name = sys.argv[2]
        number_slaves = int(sys.argv[3])
        number_masters = int(sys.argv[4])
    except:
        print("Something is missing.\r\n")
        print("python axi-build.py intercon <entity name> <number of slaves> <number of masters>\r\n")
        sys.exit()
    success = axis_intercon(entity_name,number_slaves,number_masters)
elif (command == "broadcast"):
    try:
        entity_name = sys.argv[2]
        number_masters = int(sys.argv[3])
    except:
        print("Something is missing.\r\n")
        print("python axi-build.py broadcast <entity name> <number of masters>\r\n")
        sys.exit()
    success = axis_broadcast(entity_name,number_masters)
else:
    print("Command not supported or yet to be implemented.")
    error_help()


if success:
    print("output is "+entity_name+".vhd")
    print("---------------------------------------------------------------------------------------------------------")
    print("-- This code and its autogenerated outputs are provided under LGPL by Ricardo Tafas.                   --")
    print("-- What does that mean? That you get it for free as long as you give back all good stuff you add to it.--")
    print("-- You can download more VHDL stuff at https://github.com/rftafas                                      --")
    print("---------------------------------------------------------------------------------------------------------")
sys.exit()
