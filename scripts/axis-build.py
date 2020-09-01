import sys
import os
import vhdl_gen as vhdl
import math

tabsize = 2
RegisterTypeSet = {"Custom", "ReadWrite", "Write2Clear", "Write2Pulse"}

indent = vhdl.indent

class AXISblock(BasicVHDL):
    def __init__(self, name, architecture_name):
        vhdl.BasicVHDL.__init__(self, entity_name, architecture_name)

    def create_axis_port( self, prefix, type):
        if ("master" in type):
            self.Entity.port.add("%d_tdata_o"  % prefix, "out", "std_logic_vector(tdata_size-1 downto 0)")
            self.Entity.port.add("%d_tuser_o"  % prefix, "out", "std_logic_vector(tuser_size-1 downto 0)")
            self.Entity.port.add("%d_tdest_o"  % prefix, "out", "std_logic_vector(tdest_size-1 downto 0)")
            self.Entity.port.add("%d_tready_i" % prefix, "in", "std_logic")
            self.Entity.port.add("%d_tvalid_o" % prefix, "out", "std_logic")
            self.Entity.port.add("%d_tlast_o"  % prefix, "out", "std_logic")
        else :
            self.Entity.port.add("%d_tdata_i"  % prefix, "in", "std_logic_vector(tdata_size-1 downto 0)")
            self.Entity.port.add("%d_tuser_i"  % prefix, "in", "std_logic_vector(tuser_size-1 downto 0)")
            self.Entity.port.add("%d_tdest_i"  % prefix, "in", "std_logic_vector(tdest_size-1 downto 0)")
            self.Entity.port.add("%d_tready_o" % prefix, "out", "std_logic")
            self.Entity.port.add("%d_tvalid_i" % prefix, "in", "std_logic")
            self.Entity.port.add("%d_tlast_i"  % prefix, "in", "std_logic")

    def create_axis_signal( self, signal_name, size):
        self.Architecture.Signal.add("%s_tdata_s"  % signal_name,  "axi_tdata_array(%s-1 downto 0)" % size )
        self.Architecture.Signal.add("%s_tuser_s"  % signal_name,  "axi_tdata_array(%s-1 downto 0)" % size )
        self.Architecture.Signal.add("%s_tdest_s"  % signal_name,  "axi_tdata_array(%s-1 downto 0)" % size )
        self.Architecture.Signal.add("%s_tvalid_s" % signal_name, "std_logic_vector(%s-1 downto 0)" % size )
        self.Architecture.Signal.add("%s_tlast_s"  % signal_name, "std_logic_vector(%s-1 downto 0)" % size )
        self.Architecture.Signal.add("%s_tready_s" % signal_name, "std_logic_vector(%s-1 downto 0)" % size )

    def create_port_connection( self, prefix, type):
        if ("slave" in type):
            self.Architecture.BodyCodeHeader("--Slave %s\r\n" % prefix)
            self.Architecture.BodyCodeHeader("s_tvalid_s(%d) <= %s_tvalid_i;\r\n"   % (j, prefix))
            self.Architecture.BodyCodeHeader("s_tlast_s(%d)  <= %s_tlast_i;\r\n"    % (j, prefix))
            self.Architecture.BodyCodeHeader("%s_tready_o  <= s_tready_s(%d);\r\n"  % (prefix, j))
            self.Architecture.BodyCodeHeader("s_tdata_s(%d)  <= %s_tdata_i;\r\n"    % (j, prefix))
            self.Architecture.BodyCodeHeader("s_tuser_s(%d)  <= %s_tuser_i;\r\n"    % (j, prefix))
            self.Architecture.BodyCodeHeader("s_tdest_s(%d)  <= %s_tdest_i;\r\n"    % (j, prefix))
            self.Architecture.BodyCodeHeader("\r\n")
        else:
            self.Architecture.BodyCodeHeader("--Master %d\r\n" % j)
            self.Architecture.BodyCodeHeader("%s_tvalid_o <= m_tvalid_s(%d);\r\n" % (prefix, j))
            self.Architecture.BodyCodeHeader("%s_tlast_o  <= m_tlast_s(%d);\r\n"  % (prefix, j))
            self.Architecture.BodyCodeHeader("m_tready_s(%d) <= %s_tready_i;\r\n" % (j, prefix))
            self.Architecture.BodyCodeHeader("%s_tdata_o  <= m_tdata_s(%d);\r\n"  % (prefix, j))
            self.Architecture.BodyCodeHeader("%s_tuser_o  <= m_tuser_s(%d);\r\n"  % (prefix, j))
            self.Architecture.BodyCodeHeader("%s_tdest_o  <= m_tdest_s(%d);\r\n"  % (prefix, j))
            self.Architecture.BodyCodeHeader("\r\n")


    def create_signal_connection( signal_prefix, signal_sufix, signalb_name, signalb_sufix, indsize):
        self.Architecture.BodyCodeHeader("--Connect %s to %s\r\n" % (signala_name,signalb_name))
        self.Architecture.BodyCodeHeader("%s_tvalid_s%s <= %s_tvalid_s%s;\r\n" % (signala_name, signala_sufix, signalb_name, signalb_sufix))
        self.Architecture.BodyCodeHeader("%s_tlast_s%s  <=  %s_tlast_s%s;\r\n" % (signala_name, signala_sufix, signalb_name, signalb_sufix))
        self.Architecture.BodyCodeHeader("%s_tready_s%s <= %s_tready_s%s;\r\n" % (signalb_name, signalb_sufix, signala_name, signala_sufix))
        self.Architecture.BodyCodeHeader("%s_tdata_s%s  <=  %s_tdata_s%s;\r\n" % (signala_name, signala_sufix, signalb_name, signalb_sufix))
        self.Architecture.BodyCodeHeader("%s_tuser_s%s  <=  %s_tuser_s%s;\r\n" % (signala_name, signala_sufix, signalb_name, signalb_sufix))
        self.Architecture.BodyCodeHeader("%s_tdest_s%s  <=  %s_tdest_s%s;\r\n" % (signala_name, signala_sufix, signalb_name, signalb_sufix))
        self.Architecture.BodyCodeHeader("\r\n")

class AXISCustom(AXISblock):
    def __init__(self, name, slavePorts, masterPorts, *args):
        vhdl.AXISblock.__init__(self, entity_name, "AXIbehavioral")
        self.slavePorts = slavePorts
        self.masterPorts = masterPorts
        self.tdata_size = args[0]
        self.tuser_size = args[1]
        self.tdest_size = args[2]

        self.Library.add("IEEE")
        self.Library["IEEE"].package.add("numeric_std")
        self.Library.add("stdexpert")
        self.Library["stdexpert"].package.add("std_logic_expert")
        self.Entity.generic.add("tdata_size", "integer", str(self.tdata_size))
        self.Entity.generic.add("tuser_size", "integer", str(self.tuser_size))
        self.Entity.generic.add("tdest_size", "integer", str(self.tdest_size))
        self.Entity.port.add("S_AXI_ACLK", "in", "std_logic")
        self.Entity.port.add("S_AXI_ARESETN", "in", "std_logic")

        for j in range(self.slavePorts):
            prefix = "s%d" % j
            self.create_axis_port(prefix,"slave")

        for j in range(self.masterPorts):
            prefix = "m%d" % j
            self.create_axis_port(prefix,"master")

class AXIconcat(AXISblock):
    def __init__(self, name, slavePorts, *args):
        vhdl.AXISblock.__init__(self, entity_name, "AXIbehavioral")
        self.slavePorts = slavePorts
        self.tdata_size = args[0]
        self.tuser_size = args[1]
        self.tdest_size = args[2]

        self.Library.add("IEEE")
        self.Library["IEEE"].package.add("numeric_std")
        self.Library.add("stdexpert")
        self.Library["stdexpert"].package.add("std_logic_expert")
        self.Entity.generic.add("tdata_size", "integer", str(self.tdata_size))
        self.Entity.generic.add("tuser_size", "integer", str(self.tuser_size))
        self.Entity.generic.add("tdest_size", "integer", str(self.tdest_size))
        self.Entity.port.add("S_AXI_ACLK", "in", "std_logic")
        self.Entity.port.add("S_AXI_ARESETN", "in", "std_logic")

        self.Entity.port.add("m_tdata_o"  % prefix, "out", "std_logic_vector(%d*tdata_size-1 downto 0)" % slavePorts)
        self.Entity.port.add("m_tuser_o"  % prefix, "out", "std_logic_vector(%d*tuser_size-1 downto 0)" % slavePorts)
        self.Entity.port.add("m_tdest_o"  % prefix, "out", "std_logic_vector(%d*tdest_size-1 downto 0)" % slavePorts)
        self.Entity.port.add("m_tready_i" % prefix, "in", "std_logic")
        self.Entity.port.add("m_tvalid_o" % prefix, "out", "std_logic")
        self.Entity.port.add("m_tlast_o"  % prefix, "out", "std_logic")

        self.Architecture.Constant.add("all1_c", "std_logic_vector(%s downto 0)" % self.slavePorts-1, "(others=>'1')")
        self.Architecture.Signal.add("s_tvalid_s", "std_logic_vector(%s downto 0)" % self.slavePorts-1, "(others=>'1')")
        self.Architecture.Signal.add("s_tlast_s", "std_logic_vector(%s downto 0)" % self.slavePorts-1, "(others=>'1')")

        for j in range(self.slavePorts):
            prefix = "s%d" % j
            self.create_axis_port(prefix,"slave")
            self.Architecture.BodyCodeHeader.add("m_tdata_o(%d*tdata_size-1 downto %d*tdata_size)  <= s%d_tdata_i;" % (j+1,j,j))
            self.Architecture.BodyCodeHeader.add("m_tuser_o(%d*tuser_size-1 downto %d*tuser_size)  <= s%d_tuser_i;" % (j+1,j,j))
            self.Architecture.BodyCodeHeader.add("m_tdest_o(%d*tdest_size-1 downto %d*tdest_size)  <= s%d_tdest_i;" % (j+1,j,j))
            self.Architecture.BodyCodeHeader.add("s_tvalid_s(%d) <= s%d_tvalid_i;" % j)
            self.Architecture.BodyCodeHeader.add("s_tlast_s(%d)  <=  s%d_tlast_i;" % j)
            self.Architecture.BodyCodeHeader.add("s%d_tready_o  <= m_tready_i;")

        self.Architecture.BodyCodeFooter.add("--if every master port have a valid data, we present valid data. Same for tlast.")
        self.Architecture.BodyCodeFooter.add("m_tvalid_o <= '1' when s_tvalid_s = all1_c else '0';")
        self.Architecture.BodyCodeFooter.add("m_tlast_o  <= '1' when  s_tlast_s = all1_c else '0';")

class AXImux(AXISblock):
    def __init__(self, name, slavePorts, *args):
        vhdl.AXISblock.__init__(self, entity_name, "AXIbehavioral")
        self.SlavePortsNumber = slavePorts
        self.tdata_size = args[0]
        self.tuser_size = args[1]
        self.tdest_size = args[2]
        self.select_auto  = True
        self.switch_tlast = True
        self.interleaving = True
        self.max_tx_size  = 10;
        self.mode         = 10

        self.Library.add("IEEE")
        self.Library["IEEE"].package.add("numeric_std")
        self.Library.add("stdexpert")
        self.Library["stdexpert"].package.add("std_logic_expert")

        self.Entity.generic.add("tdata_size", "integer", str(self.tdata_size))
        self.Entity.generic.add("tdest_size", "integer", str(self.tdata_size))
        self.Entity.generic.add("tuser_size", "integer", str(self.tdata_size))
        self.Entity.generic.add("select_auto", "boolean", "true")
        self.Entity.generic.add("switch_tlast", "boolean", "true")
        self.Entity.generic.add("interleaving", "boolean", "true")
        self.Entity.generic.add("max_tx_size", "integer", "10")
        self.Entity.generic.add("mode", "integer", "10")

        self.Entity.port.add("S_AXI_ACLK", "in", "std_logic")
        self.Entity.port.add("S_AXI_ARESETN", "in", "std_logic")

        self.create_axis_port("m","master")

        for j in range(SlavePortsNumber):
            self.create_axis_port("s%s" % str(j),"slave")
            self.Architecture.BodyCodeHeader.add("s_tvalid_s(%d) <= s%d_tvalid_i;\r\n" % (j, j))
            self.Architecture.BodyCodeHeader.add("s_tlast_s(%d)  <= s%d_tlast_i;\r\n" % (j, j))
            self.Architecture.BodyCodeHeader.add("axi_tdata_s(%d) <= s%d_tdata_i;\r\n" % (j,j))
            self.Architecture.BodyCodeHeader.add("axi_tuser_s(%d) <= s%d_tuser_i;\r\n" % (j,j))
            self.Architecture.BodyCodeHeader.add("axi_tdest_s(%d) <= s%d_tdest_i;\r\n" % (j,j))
            self.Architecture.BodyCodeHeader.add("s%d_tready_o   <= s_tready_s(%d) and m_tready_i;\r\n" % (j,j))

        self.Architecture.Component.add("priority_engine")
        self.Architecture.Component["priority_engine"].geenric.add("n_elements","integer","8")
        self.Architecture.Component["priority_engine"].generic.add("mode","integer","8")
        self.Architecture.Component["priority_engine"].port.add("rst_i", "in",  "std_logic")
        self.Architecture.Component["priority_engine"].port.add("clk_i", "in",  "std_logic")
        self.Architecture.Component["priority_engine"].port.add("request_i", "in",  "std_logic_vector(n_elements-1 downto 0)")
        self.Architecture.Component["priority_engine"].port.add("ack_i", "in",  "std_logic_vector(n_elements-1 downto 0)")
        self.Architecture.Component["priority_engine"].port.add("grant_o", "out", "std_logic_vector(n_elements-1 downto 0)")
        self.Architecture.Component["priority_engine"].port.add("index_o", "out", "natural")

        self.Architecture.Constant.add("number_ports", "integer", "%d" % SlavePortsNumber)

        self.Architecture.CustomTypes.add("type axi_tdata_array is array (number_ports-1 downto 0) of std_logic_vector(tdata_size-1 downto 0);")
        self.Architecture.CustomTypes.add("type axi_tuser_array is array (number_ports-1 downto 0) of std_logic_vector(tuser_size-1 downto 0);")
        self.Architecture.CustomTypes.add("type axi_tdest_array is array (number_ports-1 downto 0) of std_logic_vector(tdest_size-1 downto 0);")

        self.Architecture.Signal.add("axi_tdata_s", "axi_tdata_array")
        self.Architecture.Signal.add("axi_tuser_s", "axi_tuser_array")
        self.Architecture.Signal.add("axi_tdest_s", "axi_tdest_array")
        self.Architecture.Signal.add("tx_count_s", "integer")
        self.Architecture.Signal.add("index_s", "natural range 0 to number_ports-1")
        self.Architecture.Signal.add("ack_s", "std_logic_vector(number_ports-1 downto 0)")

        self.Architecture.BodyCodeFooter.add("m_tdata_o  <= axi_tdata_s(index_s);")
        self.Architecture.BodyCodeFooter.add("m_tdest_o  <= axi_tdest_s(index_s);")
        self.Architecture.BodyCodeFooter.add("m_tuser_o  <= axi_tuser_s(index_s);")
        self.Architecture.BodyCodeFooter.add("m_tvalid_o <= s_tvalid_s(index_s);")
        self.Architecture.BodyCodeFooter.add("m_tlast_o  <= s_tlast_s(index_s);")
        self.Architecture.BodyCodeFooter.add("")
        self.Architecture.BodyCodeFooter.add("process(all)")
        self.Architecture.BodyCodeFooter.add("begin")
        self.Architecture.BodyCodeFooter.add(indent(1)+"if rst_i = '1' then")
        self.Architecture.BodyCodeFooter.add(indent(2)+"tx_count_s <= 0;")
        self.Architecture.BodyCodeFooter.add(indent(1)+"elsif rising_edge(clk_i) then")
        self.Architecture.BodyCodeFooter.add(indent(2)+"if max_tx_size = 0 then")
        self.Architecture.BodyCodeFooter.add(indent(3)+"tx_count_s <= 1;")
        self.Architecture.BodyCodeFooter.add(indent(2)+"elsif (s_tready_s(index_s) and s_tvalid_s(index_s)) = '1' then")
        self.Architecture.BodyCodeFooter.add(indent(3)+"if ack_s(index_s) = '1' then")
        self.Architecture.BodyCodeFooter.add(indent(4)+"tx_count_s <= 0;")
        self.Architecture.BodyCodeFooter.add(indent(3)+"elsif tx_count_s = max_tx_size-1 then")
        self.Architecture.BodyCodeFooter.add(indent(4)+"tx_count_s <= 0;")
        self.Architecture.BodyCodeFooter.add(indent(3)+"else")
        self.Architecture.BodyCodeFooter.add(indent(4)+"tx_count_s <= tx_count_s + 1;")
        self.Architecture.BodyCodeFooter.add(indent(3)+"end if;")
        self.Architecture.BodyCodeFooter.add(indent(2)+"end if;")
        self.Architecture.BodyCodeFooter.add(indent(1)+"end if;")
        self.Architecture.BodyCodeFooter.add("end process;")
        self.Architecture.BodyCodeFooter.add("")
        self.Architecture.BodyCodeFooter.add("priority_engine_i : priority_engine")
        self.Architecture.BodyCodeFooter.add(indent(1)+"generic map (")
        self.Architecture.BodyCodeFooter.add(indent(2)+"n_elements => number_ports,")
        self.Architecture.BodyCodeFooter.add(indent(2)+"mode       => mode")
        self.Architecture.BodyCodeFooter.add(indent(1)+")")
        self.Architecture.BodyCodeFooter.add(indent(1)+"port map (")
        self.Architecture.BodyCodeFooter.add(indent(2)+"clk_i     => clk_i,")
        self.Architecture.BodyCodeFooter.add(indent(2)+"rst_i     => rst_i,")
        self.Architecture.BodyCodeFooter.add(indent(2)+"request_i => s_tvalid_s,")
        self.Architecture.BodyCodeFooter.add(indent(2)+"ack_i     => ack_s,")
        self.Architecture.BodyCodeFooter.add(indent(2)+"grant_o   => s_tready_s,")
        self.Architecture.BodyCodeFooter.add(indent(2)+"index_o   => index_s")
        self.Architecture.BodyCodeFooter.add(indent(1)+");")
        self.Architecture.BodyCodeFooter.add("")
        self.Architecture.BodyCodeFooter.add("ack_gen : for j in number_ports-1 downto 0 generate")
        self.Architecture.BodyCodeFooter.add(indent(1)+"ack_s(j) <= s_tlast_s(j) when switch_tlast               else")
        self.Architecture.BodyCodeFooter.add(indent(7)+"'1'          when tx_count_s = max_tx_size-1 else")
        self.Architecture.BodyCodeFooter.add(indent(7)+"'1'          when interleaving               else")
        self.Architecture.BodyCodeFooter.add(indent(7)+"'0';")
        self.Architecture.BodyCodeFooter.add("end generate;")

class AXIdemux(AXISblock):
    def __init__(self, name, MasterPortsNumber, *args):
        vhdl.AXISblock.__init__(self, entity_name, "AXIbehavioral")
        self.MasterPortsNumber = MasterPortsNumber
        self.tdata_size = args[0]
        self.tuser_size = args[1]
        self.tdest_size = args[2]
        self.select_auto  = True
        self.switch_tlast = True
        self.select_auto  = True
        self.max_tx_size  = 10;

        self.Library.add("IEEE")
        self.Library["IEEE"].package.add("numeric_std")
        self.Library.add("stdexpert")
        self.Library["stdexpert"].package.add("std_logic_expert")

        self.Entity.generic.add("tdata_size", "integer", str(self.tdata_size))
        self.Entity.generic.add("tdest_size", "integer", str(self.tdata_size))
        self.Entity.generic.add("tuser_size", "integer", str(self.tdata_size))
        self.Entity.generic.add("select_auto", "boolean", "true")
        self.Entity.generic.add("switch_tlast", "boolean", "true")
        self.Entity.generic.add("max_tx_size", "integer", "10")

        self.Entity.port.add("S_AXI_ACLK", "in", "std_logic")
        self.Entity.port.add("S_AXI_ARESETN", "in", "std_logic")

        self.create_axis_port("s","slave")

        for j in range(MasterPortsNumber):
            self.create_axis_port("m%s" % str(j),"master")
            self.create_port_connection("m%s" % str(j),j,"master")

        self.Architecture.Constant.add("number_ports", "integer", "%d" % MasterPortsNumber)

        self.Architecture.CustomTypes.add("type axi_tdata_array is array (number_ports-1 downto 0) of std_logic_vector(tdata_size-1 downto 0);")
        self.Architecture.CustomTypes.add("type axi_tuser_array is array (number_ports-1 downto 0) of std_logic_vector(tuser_size-1 downto 0);")
        self.Architecture.CustomTypes.add("type axi_tdest_array is array (number_ports-1 downto 0) of std_logic_vector(tdest_size-1 downto 0);")

        self.Architecture.Signal.add("axi_tdata_s", "axi_tdata_array")
        self.Architecture.Signal.add("axi_tuser_s", "axi_tuser_array")
        self.Architecture.Signal.add("axi_tdest_s", "axi_tdest_array")
        self.Architecture.Signal.add("m_tvalid_s", "std_logic_vector(number_ports-1 downto 0)")
        self.Architecture.Signal.add("m_tlast_s",  "std_logic_vector(number_ports-1 downto 0)")
        self.Architecture.Signal.add("m_tready_s", "std_logic_vector(number_ports-1 downto 0)")

        self.Architecture.BodyCodeFooter.add("out_gen : for j in number_masters-1 downto 0 generate")
        self.Architecture.BodyCodeFooter.add(indent(1)+"m_tdata_s(j)  <= s_tdata_i;--  when to_integer(s_tdest_i) = j else (others=>'0');")
        self.Architecture.BodyCodeFooter.add(indent(1)+"m_tuser_s(j)  <= s_tuser_i;--  when to_integer(s_tdest_i) = j else (others=>'0');")
        self.Architecture.BodyCodeFooter.add(indent(1)+"m_tdest_s(j)  <= s_tdest_i;--  when to_integer(s_tdest_i) = j else (others=>'0');")
        self.Architecture.BodyCodeFooter.add(indent(1)+"m_tlast_s(j)  <= s_tlast_i;--  when to_integer(s_tdest_i) = j else '0';")
        self.Architecture.BodyCodeFooter.add(indent(1)+"m_tvalid_s(j) <= s_tvalid_i;-- when to_integer(s_tdest_i) = j else '0';")
        self.Architecture.BodyCodeFooter.add("end generate;")
        self.Architecture.BodyCodeFooter.add("")
        self.Architecture.BodyCodeFooter.add("s_tready_o <= m_tready_s(to_integer(s_tdest_i));")

class AXIaligner:
    def __init__(self, entity_name, number_elements):
        vhdl.AXISblock.__init__(self, entity_name, "AXIbehavioral")
        self.PortsNumber = number_elements
        self.tdata_size = args[0]
        self.tuser_size = args[1]
        self.tdest_size = args[2]

        self.Library.add("IEEE")
        self.Library["IEEE"].package.add("numeric_std")
        self.Library.add("stdexpert")
        self.Library["stdexpert"].package.add("std_logic_expert")

        self.Entity.generic.add("tdata_size", "integer", str(self.tdata_size))
        self.Entity.generic.add("tdest_size", "integer", str(self.tdata_size))
        self.Entity.generic.add("tuser_size", "integer", str(self.tdata_size))
        self.Entity.generic.add("select_auto", "boolean", "true")
        self.Entity.generic.add("switch_tlast", "boolean", "true")
        self.Entity.generic.add("max_tx_size", "integer", "10")

        self.Entity.port.add("S_AXI_ACLK", "in", "std_logic")
        self.Entity.port.add("S_AXI_ARESETN", "in", "std_logic")

        for j in range(self.PortsNumber):
            self.create_axis_port("s%s" % str(j),"slave")
            self.create_axis_port("m%s" % str(j),"master")

        self.Architecture.Constant.add("number_ports", "integer", "%d" % self.PortsNumber)
        self.Architecture.Constant.add("all1_c", "std_logic_vector(number_ports-1 downto 0)", "(others=>'1')")

        self.Architecture.CustomTypes.add("type axi_tdata_array is array (number_ports-1 downto 0) of std_logic_vector(tdata_size-1 downto 0);")
        self.Architecture.CustomTypes.add("type axi_tuser_array is array (number_ports-1 downto 0) of std_logic_vector(tuser_size-1 downto 0);")
        self.Architecture.CustomTypes.add("type axi_tdest_array is array (number_ports-1 downto 0) of std_logic_vector(tdest_size-1 downto 0);")

        create_axis_signal("s", self.PortsNumber):
        create_axis_signal("m", self.PortsNumber):

        self.Architecture.Signal.add("ready_s", "std_logic_vector(number_ports-1 downto 0)")
        self.Architecture.Signal.add("en_o_s", "std_logic_vector(number_ports-1 downto 0)")
        self.Architecture.Signal.add("en_i_s", "std_logic_vector(number_ports-1 downto 0)")

        self.Architecture.BodyCodeFooter.add("m_tdata_s <= s_tdata_s;")
        self.Architecture.BodyCodeFooter.add("m_tdest_s <= s_tdest_s;")
        self.Architecture.BodyCodeFooter.add("m_tuser_s <= s_tuser_s;")
        self.Architecture.BodyCodeFooter.add("")
        self.Architecture.BodyCodeFooter.add("en_i_s     <= s_tvalid_s and ready_s;")
        self.Architecture.BodyCodeFooter.add("s_tready_s <= en_o_s;")
        self.Architecture.BodyCodeFooter.add("m_tvalid_s <= en_o_s;")
        self.Architecture.BodyCodeFooter.add("")
        self.Architecture.BodyCodeFooter.add("pulse_align_i : pulse_align")
        self.Architecture.BodyCodeFooter.add(indent(1)+"generic map (")
        self.Architecture.BodyCodeFooter.add(indent(2)+"port_size => number_ports")
        self.Architecture.BodyCodeFooter.add(indent(1)+")")
        self.Architecture.BodyCodeFooter.add(indent(1)+"port map (")
        self.Architecture.BodyCodeFooter.add(indent(2)+"rst_i  => rst_i,")
        self.Architecture.BodyCodeFooter.add(indent(2)+"mclk_i => clk_i,")
        self.Architecture.BodyCodeFooter.add(indent(2)+"en_i   => en_i_s,")
        self.Architecture.BodyCodeFooter.add(indent(2)+"en_o   => en_o_s")
        self.Architecture.BodyCodeFooter.add(indent(1)+");")
        self.Architecture.BodyCodeFooter.add("")
        self.Architecture.BodyCodeFooter.add("ready_gen : for j in number_ports-1 downto 0 generate")
        self.Architecture.BodyCodeFooter.add(indent(1)+"det_down_i : det_down")
        self.Architecture.BodyCodeFooter.add(indent(2)+"port map (")
        self.Architecture.BodyCodeFooter.add(indent(3)+"rst_i  => rst_i,")
        self.Architecture.BodyCodeFooter.add(indent(3)+"mclk_i => clk_i,")
        self.Architecture.BodyCodeFooter.add(indent(3)+"din    => m_tready_s,")
        self.Architecture.BodyCodeFooter.add(indent(3)+"dout   => ready_s")
        self.Architecture.BodyCodeFooter.add(indent(2)+");")
        self.Architecture.BodyCodeFooter.add("end generate;")

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
