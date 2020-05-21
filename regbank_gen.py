import sys
import os
import vhdl_gen

regsiter_type = ["read only", "read write", "pulse", "write to clear"]

class register:
    def __init__(Self,size):
        self.generic = vhdl_gen.generic_list()
        self.port = vhdl_gen.port_list()



class axi_regbank:
    def __init__(self, name):
        self.name = ("%s_reg" % name)
        self.regbank = vhdl_gen.vhdl_file(self.name,"rtl")
        self.library.list[0].package.add("numeric_std")
        self.entity.generic.add("addr_size", "integer", "8")
        self.entity.generic.add("data_size", "integer", "8")

        self.entity.port.add("S_AXI_ACLK", "in", "std_logic")
        self.entity.port.add("S_AXI_ARESETN", "in", "std_logic")
        self.entity.port.add("S_AXI_AWADDR", "in", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
		self.entity.port.add("S_AXI_AWPROT", "in", "std_logic_vector(2 downto 0)")
		self.entity.port.add("S_AXI_AWVALID", "in", "std_logic")
		self.entity.port.add("S_AXI_AWREADY", "out", "std_logic")
		self.entity.port.add("S_AXI_WSTRB", "in", "std_logic_vector((C_S_AXI_DATA_WIDTH/8)-1 downto 0)")
		self.entity.port.add("S_AXI_WVALID", "in", "std_logic")
		self.entity.port.add("S_AXI_WREADY", "out", "std_logic")
		self.entity.port.add("S_AXI_BRESP", "out", "std_logic_vector(1 downto 0)")
		self.entity.port.add("S_AXI_BVALID", "out", "std_logic")
		self.entity.port.add("S_AXI_BREADY", "in", "std_logic")
		self.entity.port.add("S_AXI_ARADDR", "in", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
		self.entity.port.add("S_AXI_ARPROT", "in", "std_logic_vector(2 downto 0)")
		self.entity.port.add("S_AXI_ARVALID", "in", "std_logic")
		self.entity.port.add("S_AXI_ARREADY", "out", "std_logic")
		self.entity.port.add("S_AXI_RDATA", "out", "std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0)")
		self.entity.port.add("S_AXI_RRESP", "out", "std_logic_vector(1 downto 0)")
		self.entity.port.add("S_AXI_RVALID", "out", "std_logic")
		self.entity.port.add("S_AXI_RREADY", "in", "std_logic")

        self.architecture.constant.add("delay", "integer", "0")
        self.architecture.signal.add("dout_s", "std_logic_vector(addr_size-1 downto 0)", "")
        self.architecture.signal.add("ram_s", "ram_t", "")
        self.architecture.declaration_code = "  --Test adding custom declarative code."
        self.architecture.body_code = "  --Test adding custom body code."
