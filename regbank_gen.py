import sys
import os
import vhdl_gen as vhdl
import math
import myhdl
from myhdl import block, always_seq, always_comb, Signal, ResetSignal, modbv
from myhdl._extractHierarchy import (_HierExtr, _isMem, _getMemInfo, _UserVhdlCode, _userCodeMap)

RegisterTypeSet = {"ReadOnly", "ReadWrite", "Write2Clear", "Write2Pulse"}

TemplateCode = """
	-- I/O Connections assignments
	S_AXI_AWREADY	<= axi_awready;
	S_AXI_WREADY	<= axi_wready;
	S_AXI_BRESP	  <= axi_bresp;
	S_AXI_BVALID	<= axi_bvalid;
	S_AXI_ARREADY	<= axi_arready;
	S_AXI_RDATA	  <= axi_rdata;
	S_AXI_RRESP	  <= axi_rresp;
	S_AXI_RVALID	<= axi_rvalid;

	-- Implement axi_awready generation
	-- axi_awready is asserted for one S_AXI_ACLK clock cycle when both
	-- S_AXI_AWVALID and S_AXI_WVALID are asserted. axi_awready is
	-- de-asserted when reset is low.
  process(S_AXI_ARESETN, S_AXI_ACLK)
  begin
		if S_AXI_ARESETN = '0' then
					axi_awready <= '0';
					aw_en <= '1';
		elsif rising_edge(S_AXI_ACLK) then
      if (axi_awready = '0' and S_AXI_AWVALID = '1' and S_AXI_WVALID = '1' and aw_en = '1') then
      -- slave is ready to accept write address when
      -- there is a valid write address and write data
      -- on the write address and data bus. This design
      -- expects no outstanding transactions.
          axi_awready <= '1';
          aw_en <= '0';
      elsif (S_AXI_BREADY = '1' and axi_bvalid = '1') then
          aw_en <= '1';
          axi_awready <= '0';
      else
          axi_awready <= '0';
      end if;
    end if;
	end process;

	-- Implement axi_awaddr latching
	-- This process is used to latch the address when both
	-- S_AXI_AWVALID and S_AXI_WVALID are valid.

	process (S_AXI_ARESETN, S_AXI_ACLK)
	begin
		if S_AXI_ARESETN = '0' then
			axi_awaddr <= (others => '0');
	  elsif rising_edge(S_AXI_ACLK) then
      if (axi_awready = '0' and S_AXI_AWVALID = '1' and S_AXI_WVALID = '1' and aw_en = '1') then
        -- Write Address latching
        axi_awaddr <= S_AXI_AWADDR;
	    end if;
	  end if;
	end process;

	-- Implement axi_wready generation
	-- axi_wready is asserted for one S_AXI_ACLK clock cycle when both
	-- S_AXI_AWVALID and S_AXI_WVALID are asserted. axi_wready is
	-- de-asserted when reset is low.

	process (S_AXI_ACLK)
	begin
		if S_AXI_ARESETN = '0' then
			axi_wready <= '0';
		elsif rising_edge(S_AXI_ACLK) then
    	if (axi_wready = '0' and S_AXI_WVALID = '1' and S_AXI_AWVALID = '1' and aw_en = '1') then
	          -- slave is ready to accept write data when
	          -- there is a valid write address and write data
	          -- on the write address and data bus. This design
	          -- expects no outstanding transactions.
	          axi_wready <= '1';
	    else
	    	axi_wready <= '0';
	    end if;
	  end if;
	end process;

	-- Implement memory mapped register select and write logic generation
	-- The write data is accepted and written to memory mapped registers when
	-- axi_awready, S_AXI_WVALID, axi_wready and S_AXI_WVALID are asserted. Write strobes are used to
	-- select byte enables of slave registers while writing.
	-- These registers are cleared when reset (active low) is applied.
	-- Slave register write enable is asserted when valid address and data are available
	-- and the slave is ready to accept the write address and write data.
	regwrite_en <= axi_wready and S_AXI_WVALID and axi_awready and S_AXI_AWVALID ;



	process (S_AXI_ACLK)
		variable loc_addr : integer;
	begin
		if S_AXI_ARESETN = '0' then
			regwrite_s <= (others => (others => '0'));
		elsif rising_edge(S_AXI_ACLK) then
			loc_addr := to_integer(unsigned(axi_awaddr(C_S_AXI_ADDR_WIDTH-1 downto ADDR_LSB)));
			for j in regwrite_s'range loop
				for k in BYTE_NUM-1 downto 0 loop
					for m in 7 downto 0 loop
						if ext_clear_s(j)(k*8+m) = '1' then
						elsif regwrite_en = '1' then
							if S_AXI_WSTRB(k) = '1' then
								if write2clear_c(j)(k*8+m) or write2pulse_c(j)(k*8+m) = '1' then
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



	-- Implement write response logic generation
	-- The write response and response valid signals are asserted by the slave
	-- when axi_wready, S_AXI_WVALID, axi_wready and S_AXI_WVALID are asserted.
	-- This marks the acceptance of address and indicates the status of
	-- write transaction.

	process (S_AXI_ACLK)
	begin
	  if rising_edge(S_AXI_ACLK) then
	    if S_AXI_ARESETN = '0' then
	      axi_bvalid  <= '0';
	      axi_bresp   <= "00"; --need to work more on the responses
	    else
	      if (axi_awready = '1' and S_AXI_AWVALID = '1' and axi_wready = '1' and S_AXI_WVALID = '1' and axi_bvalid = '0'  ) then
	        axi_bvalid <= '1';
	        axi_bresp  <= "00";
	      elsif (S_AXI_BREADY = '1' and axi_bvalid = '1') then   --check if bready is asserted while bvalid is high)
	        axi_bvalid <= '0';                                 -- (there is a possibility that bready is always asserted high)
	      end if;
	    end if;
	  end if;
	end process;

	-- Implement axi_arready generation
	-- axi_arready is asserted for one S_AXI_ACLK clock cycle when
	-- S_AXI_ARVALID is asserted. axi_awready is
	-- de-asserted when reset (active low) is asserted.
	-- The read address is also latched when S_AXI_ARVALID is
	-- asserted. axi_araddr is reset to zero on reset assertion.

	process(S_AXI_ARESETN, S_AXI_ACLK)
	begin
		if S_AXI_ARESETN = '0' then
			axi_arready <= '0';
			axi_araddr  <= (others => '1');
	  elsif rising_edge(S_AXI_ACLK) then
	      if (axi_arready = '0' and S_AXI_ARVALID = '1') then
	        -- indicates that the slave has acceped the valid read address
	        axi_arready <= '1';
	        -- Read Address latching
	        axi_araddr  <= S_AXI_ARADDR;
	      else
	        axi_arready <= '0';
	      end if;
	    end if;
	end process;

	-- Implement axi_arvalid generation
	-- axi_rvalid is asserted for one S_AXI_ACLK clock cycle when both
	-- S_AXI_ARVALID and axi_arready are asserted. The slave registers
	-- data are available on the axi_rdata bus at this instance. The
	-- assertion of axi_rvalid marks the validity of read data on the
	-- bus and axi_rresp indicates the status of read transaction.axi_rvalid
	-- is deasserted on reset (active low). axi_rresp and axi_rdata are
	-- cleared to zero on reset (active low).
	process (S_AXI_ACLK)
	begin
		if S_AXI_ARESETN = '0' then
			axi_rvalid <= '0';
			axi_rresp  <= "00";
	  elsif rising_edge(S_AXI_ACLK) then
	      if (axi_arready = '1' and S_AXI_ARVALID = '1' and axi_rvalid = '0') then
	        -- Valid read data is available at the read data bus
	        axi_rvalid <= '1';
	        axi_rresp  <= "00"; -- 'OKAY' response
	      elsif (axi_rvalid = '1' and S_AXI_RREADY = '1') then
	        -- Read data is accepted by the master
	        axi_rvalid <= '0';
	      end if;
	    end if;
	end process;

	-- Implement memory mapped register select and read logic generation
	-- Slave register read enable is asserted when valid address is available
	-- and the slave is ready to accept the read address.
	regread_en <= axi_arready and S_AXI_ARVALID and (not axi_rvalid) ;

    -- Get data from ports to bus
    read_reg_p : process( S_AXI_ACLK ) is
				variable reg_tmp : reg_t := (others => (others => '0'));
    begin
				if (S_AXI_ARESETN = '0') then
					axi_rdata <= (others => '0');
					reg_tmp    := (others => (others => '0'));
        elsif (rising_edge (S_AXI_ACLK)) then
					reg_tmp   := regread_s;
          axi_rdata <= (others => '0');
					for j in regread_s'range then
						for k in regread_s(0)'range then'
          		if regclear_s(j)(k) = '1' then
								reg_tmp(j)(k) <= '0';
							elsif regset_s(j)(k) = '1' then
								reg_tmp(j)(k) <= '1';
							end if;
						end loop;
					end loop;
					axi_rdata <= reg_tmp(to_integer(axi_araddr(C_S_AXI_ADDR_WIDTH-1 downto ADDR_LSB))
        end if;
    end process;

    read_p : process ( S_AXI_ACLK )
    begin
			if S_AXI_ARESETN = '0'then
					S_AXI_RDATA  <= (others => '0');
      elsif (rising_edge (S_AXI_ACLK)) then
        if (regread_en = '1') then
          S_AXI_RDATA	<= axi_rdata;
        end if;
      end if;
    end process;
		S_AXI_RDATA	  <= axi_rdata;
"""

def GetDirection(type):
    if type in ("ReadOnly", "Write2Clear"):
        return "in"
    else:
        return "out"

def GetSuffix(type):
    if type in ("ReadOnly", "Write2Clear"):
        return "_i"
    else:
        return "_o"

class RegisterBit:
    def __init__(self,name,type):
        if type in RegisterTypeSet:
            self.RegType = type
        else:
            self.RegType = "ReadOnly"
            print("Register Type not known. Using ReadOnly")
            Print(RegisterTypeSet)
        self.ExternalClear = False
        self.name = name+GetSuffix(type)
        self.radix = name
        self.direction = GetDirection(type)
        self.vhdlType = "std_logic"

class RegisterSlice(RegisterBit):
    def __init__(self,name,type,size):
        RegisterBit.__init__(self,name,type)
        self.size = size
        self.vhdlrange = "(%d downto 0)" % size
        self.vhdlType = "std_logic_vector(%d downto 0)" % (size-1)

class RegisterWord(dict):
    def __init__(self,name,size):
        dict.__init__(self)
        self.name = name
        for j in range(size):
            self[j] = ["empty"]

    def add(self,name,type,start,size):
        if "empty" in self[start]:
            if size > 1:
                self[start] = RegisterSlice(name,type,size)
            else:
                self[start] = RegisterBit(name,type)
                for j in range(start+1,start+size):
                    if "empty" in self[j]:
                        self[j] = name+"(%d)" % j
                    else:
                        print("Reg is already occupied by %s" % self[j].name)
        else:
            print("This reg is already occupied by %s" % self[start].name)

class RegisterList(dict):
    def add(self,number,Register):
        self[number] = Register

class RegisterBank(vhdl.BasicVHDL):
    def __init__(self, entity_name, architecture_name, datasize, RegisterNumber):
        vhdl.BasicVHDL.__init__(self, entity_name, architecture_name)
        self.reg = RegisterList()
        self.datasize = datasize
        self.addrsize = math.ceil(math.log(RegisterNumber,2))

        self.Library.add("IEEE")
        self.Library["IEEE"].package.add("numeric_std")
        self.Library.add("stdexpert")
        self.Library["stdexpert"].package.add("std_logic_expert")
        self.Entity.generic.add("C_S_AXI_ADDR_WIDTH", "integer", str(self.addrsize))
        self.Entity.generic.add("C_S_AXI_DATA_WIDTH", "integer", str(self.datasize))
        self.Entity.port.add("S_AXI_ACLK", "in", "std_logic")
        self.Entity.port.add("S_AXI_ARESETN", "in", "std_logic")
        self.Entity.port.add("S_AXI_AWADDR", "in", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.Entity.port.add("S_AXI_AWPROT", "in", "std_logic_vector(2 downto 0)")
        self.Entity.port.add("S_AXI_AWVALID", "in", "std_logic")
        self.Entity.port.add("S_AXI_AWREADY", "out", "std_logic")
        self.Entity.port.add("S_AXI_WSTRB", "in", "std_logic_vector((C_S_AXI_DATA_WIDTH/8)-1 downto 0)")
        self.Entity.port.add("S_AXI_WVALID", "in", "std_logic")
        self.Entity.port.add("S_AXI_WREADY", "out", "std_logic")
        self.Entity.port.add("S_AXI_BRESP", "out", "std_logic_vector(1 downto 0)")
        self.Entity.port.add("S_AXI_BVALID", "out", "std_logic")
        self.Entity.port.add("S_AXI_BREADY", "in", "std_logic")
        self.Entity.port.add("S_AXI_ARADDR", "in", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.Entity.port.add("S_AXI_ARPROT", "in", "std_logic_vector(2 downto 0)")
        self.Entity.port.add("S_AXI_ARVALID", "in", "std_logic")
        self.Entity.port.add("S_AXI_ARREADY", "out", "std_logic")
        self.Entity.port.add("S_AXI_RDATA", "out", "std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0)")
        self.Entity.port.add("S_AXI_RRESP", "out", "std_logic_vector(1 downto 0)")
        self.Entity.port.add("S_AXI_RVALID", "out", "std_logic")
        self.Entity.port.add("S_AXI_RREADY", "in", "std_logic")

        self.Architecture.CustomTypes.add("type reg_t is array (NATURAL RANGE<>) of std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);")
        self.Architecture.Signal.add("axi_awaddr", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.Architecture.Signal.add("axi_awready", "std_logic")
        self.Architecture.Signal.add("axi_wready", "std_logic")
        self.Architecture.Signal.add("axi_bresp", "std_logic_vector(1 downto 0)")
        self.Architecture.Signal.add("axi_bvalid", "std_logic")
        self.Architecture.Signal.add("axi_araddr", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
        self.Architecture.Signal.add("axi_arready", "std_logic")
        self.Architecture.Signal.add("axi_rdata", "std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0)")
        self.Architecture.Signal.add("axi_rresp", "std_logic_vector(1 downto 0)")
        self.Architecture.Signal.add("axi_rvalid", "std_logic")

        self.Architecture.Signal.add("regwrite_s", "reg_t", "(others=>(others=>'0'))")
        self.Architecture.Signal.add("regread_s", "reg_t", "(others=>(others=>'0'))")
        self.Architecture.Signal.add("regclear_s", "reg_t", "(others=>(others=>'0'))")
        self.Architecture.Signal.add("regset_s", "reg_t", "(others=>(others=>'0'))")

        self.Architecture.Signal.add("regread_en", "std_logic")
        self.Architecture.Signal.add("regwrite_en", "std_logic")
        self.Architecture.Signal.add("aw_en", "std_logic")

        for lines in TemplateCode.splitlines():
            self.Architecture.BodyCodeHeader.add(lines)


    def add(self,number,name):
        self.reg.add(number,RegisterWord(name,self.datasize))

    def RegisterPortAdd(self):
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                try:
                    self.Entity.port.add(register[bit].name,register[bit].direction,register[bit].vhdlType)
                except:
                    pass

    def RegisterClearAdd(self):
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                try:
                    if register[bit].ExternalClear:
                        self.Entity.port.add(register[bit].radix+"_clear_i",register[bit].direction,register[bit].vhdlType)
                except:
                    pass

    def RegisterConnection(self):
        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "--Register Connection")
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                if isinstance(register[bit], RegisterBit):
                    VectorRange = str(bit)
                    if isinstance(register[bit], RegisterSlice):
                        VectorRange = "%d downto %d" % (bit+register[bit].size-1, bit)
                        register[bit].name = register[bit].name+"(%d downto 0)" %  (register[bit].size-1)
                    if "ReadOnly" in register[bit].RegType:
                        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" % (index,VectorRange,register[bit].name))
                    elif "ReadWrite" in register[bit].RegType:
                        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" % (register[bit].name,index,VectorRange))
                        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= regwrite_s(%d)(%s);" % (index,VectorRange,index,VectorRange))
                    elif "Write2Clear" in register[bit].RegType:
                        pass #self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "regread_s(%d)(%s) <= %s;" % (index,VectorRange,register[bit].name))
                    elif "Write2Pulse" in register[bit].RegType:
                        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "%s <= regwrite_s(%d)(%s);" % (register[bit].name,index,VectorRange))
        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "")

    def RegisterSetConnection(self):
        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "--Set Connection for Write to Clear")
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                if isinstance(register[bit], RegisterBit):
                    VectorRange = str(bit)
                    if isinstance(register[bit], RegisterSlice):
                        VectorRange = "%d downto %d" % (bit+register[bit].size-1, bit)
                    if "Write2Clear" in register[bit].RegType:
                        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "regset_s(%d)(%s) <= %s;" % (index,VectorRange,register[bit].name))
                        #self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "regset_s(%d)(%s) <= regread_s(%d)(%s)" % (index,VectorRange,index,VectorRange))
        self.Architecture.BodyCodeFooter.add("")

    def RegisterClearConnection(self):
        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "--External Clear Connection")
        for index in self.reg:
            register = self.reg[index]
            for bit in register:
                if isinstance(register[bit], RegisterBit):
                    clearname = register[bit].radix+"_clear_i"
                    defaultvalue = "'1'"
                    elsevalue = "'0'"
                    VectorRange = str(bit)
                    if isinstance(register[bit], RegisterSlice):
                        VectorRange = "%d downto %d" % (bit+register[bit].size-1, bit)
                        defaultvalue = "(others=>'1')"
                    if "Write2Clear" in register[bit].RegType:
                        elsevalue =  "regwrite_s(%d)(%s)" % (index,VectorRange)
                    if register[bit].ExternalClear:
                        self.Architecture.BodyCodeFooter.add(vhdl.indent(1) + "regclear_s(%d)(%s) <= %s when %s = '1' else %s;" % (index,VectorRange,defaultvalue,clearname,elsevalue))
        self.Architecture.BodyCodeFooter.add("")

    def code(self):
        self.RegisterPortAdd()
        self.RegisterClearAdd()
        self.RegisterConnection()
        self.RegisterSetConnection()
        self.RegisterClearConnection()
        return vhdl.BasicVHDL.code(self)



myregbank = RegisterBank("myregbank","rtl",32,8)
myregbank.add(0,"golden")
myregbank.reg[0].add("golden","ReadOnly",0,32)
myregbank.add(1,"scrap1")
myregbank.reg[1].add("scrap1","ReadWrite",0,32)
myregbank.reg[1][0].ExternalClear = True
myregbank.add(2,"scrap2")
myregbank.reg[2].add("scrap2","ReadWrite",0,32)
myregbank.reg[2][0].ExternalClear = True

myregbank.add(3,"diverse")
myregbank.reg[3].add("pulse","Write2Pulse",0,1)
myregbank.reg[3].add("w2l","Write2Clear",2,1)
myregbank.reg[3].add("rot","ReadOnly",24,8)
myregbank.reg[3][0].ExternalClear = True
myregbank.reg[3][2].ExternalClear = True
myregbank.reg[3][24].ExternalClear = True

myregbank.add(4,"diverse2")
myregbank.reg[4].add("div2w2clr","Write2Clear",0,16)
myregbank.reg[4][0].ExternalClear = True

print(myregbank.Entity.port.code())

S_AXI_ARESETN = ResetSignal(0, active=0, isasync=True)
S_AXI_ACLK  = Signal(bool(0))
axi_awready = Signal(bool(0))
aw_en = Signal(bool(0));
S_AXI_AWVALID = Signal(bool(0))
axi_bvalid = Signal(bool(0))
S_AXI_WVALID = Signal(bool(0))
S_AXI_BREADY = Signal(bool(0))
axi_bvalid = Signal(bool(0))
S_AXI_AWVALID = Signal(bool(0))
axi_wready = Signal(bool(0))
duff = Signal(bool(0))
axi_awaddr = Signal(myhdl.intbv(0)[32:])
S_AXI_AWADDR = Signal(myhdl.intbv(0)[32:])
regwrite_en = Signal(bool(0))




#inc_1 = inc(S_AXI_ACLK,S_AXI_ARESETN)
#inc_1.convert(hdl='VHDL')
toVHDL = myhdl.toVHDL
toVHDL(inc(S_AXI_ACLK,S_AXI_ARESETN))

#Without using the "VHDL FILE"
# def regbank_create(name,qty,size):
#     Entity.generic.add("C_S_AXI_ADDR_WIDTH", "integer", addr_witdh)
#     Entity.generic.add("C_S_AXI_DATA_WIDTH", "integer", data_witdh)
#     #entity - port

#
#     #adds custom code not provided by lib.
#     regbank.architecture.declaration_code("type reg_t is array (NATURAL RANGE<>) of std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);\r\n")
#
#     regbank.architecture.signal.add("axi_awaddr", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
#     regbank.architecture.signal.add("axi_awready", "std_logic")
#     regbank.architecture.signal.add("axi_wready", "std_logic")
#     regbank.architecture.signal.add("axi_bresp", "std_logic_vector(1 downto 0)")
#     regbank.architecture.signal.add("axi_bvalid", "std_logic")
#     regbank.architecture.signal.add("axi_araddr", "std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0)")
#     regbank.architecture.signal.add("axi_arready", "std_logic")
#     regbank.architecture.signal.add("axi_rdata", "std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0)")
#     regbank.architecture.signal.add("axi_rresp", "std_logic_vector(1 downto 0)")
#     regbank.architecture.signal.add("axi_rvalid", "std_logic")
#
#     regbank.architecture.constant.add("slv_reg_write", "reg_t", "(others=>(others=>'0'))")
#     regbank.architecture.constant.add("slv_reg_read", "reg_t", "(others=>(others=>'0'))")
#     regbank.architecture.constant.add("write_vec", "reg_t", "(others=>(others=>'0'))")
#     regbank.architecture.constant.add("read_fec", "reg_t", "(others=>(others=>'0'))")
#
#     regbank.architecture.body_code = "  --Test adding custom body code.\r\n"
#
#     return regbank
#
# regbank = regbank_create("test_axim_regbank",4,32)
# print Library.code()
