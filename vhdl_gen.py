import sys
import os

try:
    x = tabsize
except NameError:
    tabsize = 2

def indent(value):
    txt = ""
    if value > 0:
        for j in range(tabsize * value):
            txt = txt + " "
    return txt;

def entity_enum(list):
    hdl_code = ""
    i = 0
    for j in list:
        i = i+1
        if (i == len(list)):
            hdl_code = hdl_code + j.code().replace(";","")
        else:
            hdl_code = hdl_code + j.code()
    return hdl_code

class element:
    def __init__(self):
        self.list = []
    def add(self, name):
        self.list.append(name)

class vhdl_library:
    class library_obj:
        class package_map:
            class package_obj:
                def __init__(self, name):
                    self.operator = "all"
                    self.name     = name

            def __init__(self):
                self.list = []

            def add(self, name):
                self.list.append(self.package_obj(name))

        def __init__(self, name):
            self.name = name
            self.package = self.package_map()

        def code(self):
            hdl_code = ""
            hdl_code = hdl_code + indent(0) + ("library %s;\r\n" % self.name)
            if self.package.list:
                for j in self.package.list:
                    hdl_code = hdl_code + indent(1) + ("use %s.%s.%s;\r\n" % (self.name, j.name, j.operator))
            hdl_code = hdl_code + "\r\n"
            return hdl_code

    def __init__(self):
        self.list = []

    def add(self, name):
        self.list.append(self.library_obj(name))

    def code(self):
        hdl_code = ""
        if self.list:
            for j in self.list:
                hdl_code = hdl_code + j.code()
        return hdl_code

class vhdl_entity:

    class generic_map:
        class generic_obj:
            def __init__(self, name, type, init_value):
                self.name = name
                self.init = init_value
                self.type = type
            def code(self):
                hdl_code = indent(2) + ("%s : %s := %s;\r\n" % (self.name, self.type, self.init))
                return hdl_code
        def __init__(self):
            self.list = []
        def add(self, name, type, init):
            self.list.append(self.generic_obj(name,type,init))
        def code(self):
            return entity_enum(self.list)

    class port_map:
        class port_obj:
            def __init__(self, name, direction, type):
                self.name = name
                self.direction = direction
                self.type = type
            def code(self):
                hdl_code = indent(2) + ("%s : %s %s;\r\n" % (self.name, self.direction, self.type))
                return hdl_code
        def __init__(self):
            self.list = []
        def add(self, name, direction, type):
            self.list.append(self.port_obj(name, direction, type))
        def code(self):
            return entity_enum(self.list)

    def __init__(self, name):
        self.name    = name
        self.generic = self.generic_map()
        self.port    = self.port_map()

    def code(self):
        hdl_code = indent(0) + ("entity %s is\r\n" % self.name)
        if (self.generic.list):
            hdl_code = hdl_code + indent(1) + ("generic (\r\n")
            hdl_code = hdl_code + self.generic.code()
            hdl_code = hdl_code + indent(1) + (");\r\n")
        else:
            hdl_code = hdl_code + indent(1) + ("--generic (\r\n")
            hdl_code = hdl_code + indent(2) + ("--generic_declaration_tag\r\n")
            hdl_code = hdl_code + indent(1) + ("--);\r\n")
        if (self.port.list):
            hdl_code = hdl_code + indent(1) + ("port (\r\n")
            hdl_code = hdl_code + self.port.code()
            hdl_code = hdl_code + indent(1) + (");\r\n")
        else:
            hdl_code = hdl_code + indent(1) + ("--port (\r\n")
            hdl_code = hdl_code + indent(2) + ("--port_declaration_tag\r\n")
            hdl_code = hdl_code + indent(1) + ("--);\r\n")
        hdl_code = hdl_code + indent(0) + ("end %s;\r\n" % self.name)
        hdl_code = hdl_code + "\r\n"
        return hdl_code

class vhdl_architecture:
    class vhdl_constant_map:
        class vhdl_constant_obj:
            def __init__(self, name, type, init):
                self.name = name
                self.type = type
                self.init = init
            def code(self):
                return indent(1) + "constant %s : %s := %s;\r\n" % (self.name, self.type, self.init)
        def __init__(self):
            self.list = []
        def add(self,name,type,init):
            self.list.append(self.vhdl_constant_obj(name,type,init))
        def code(self):
            hdl_code = ""
            for j in self.list:
                hdl_code = hdl_code + j.code()
            return hdl_code

    class vhdl_signal_map:
        class vhdl_signal_obj:
            def __init__(self, name, type, init):
                self.name = name
                self.type = type
                self.init = init
            def code(self):
                if (self.init == ""):
                    return indent(1) + ("signal %s : %s;\r\n" % (self.name, self.type))
                else:
                    return indent(1) + ("signal %s : %s := %s;\r\n" % (self.name, self.type, self.init))

        def __init__(self):
            self.list = []
        def add(self,name,type,init):
            self.list.append(self.vhdl_signal_obj(name,type,init))
        def code(self):
            hdl_code = ""
            for j in self.list:
                hdl_code = hdl_code + j.code()
            return hdl_code

    def __init__(self, name, entity_name):
        self.name = name
        self.entity_name = entity_name
        self.signal = self.vhdl_signal_map()
        self.constant = self.vhdl_constant_map()
        self.declaration_code = ""
        self.body_code = ""

    def code(self):
        hdl_code = ""
        hdl_code = indent(0) + ("architecture %s of %s is\r\n" % (self.name, self.entity_name))
        hdl_code = hdl_code + "\r\n"
        if (self.constant.list != []):
            hdl_code = hdl_code + self.constant.code()
            hdl_code = hdl_code + "\r\n"
        if (self.signal.list != []):
            hdl_code = hdl_code + self.signal.code()
            hdl_code = hdl_code + "\r\n"
        if (self.declaration_code != ""):
            hdl_code = hdl_code + self.declaration_code
            hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + indent(1) + ("--architecture_declaration_tag\r\n")
        hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + indent(0) + ("begin\r\n")
        hdl_code = hdl_code + "\r\n"
        if (self.body_code != ""):
            hdl_code = hdl_code + self.body_code
            hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + indent(1) + ("--architecture_body_tag\r\n")
        hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + indent(0) + ("end %s\r\n" % self.name)
        hdl_code = hdl_code + "\r\n"
        return hdl_code

class vhdl_file:
    def __init__(self, entity_name, architecture_name):
        self.library      = vhdl_library()
        self.entity       = vhdl_entity(entity_name)
        self.architecture = vhdl_architecture(architecture_name, entity_name)

    def write_file(self):
        hdl_code = ""
        hdl_code = hdl_code + self.library.code()
        hdl_code = hdl_code + self.entity.code()
        hdl_code = hdl_code + self.architecture.code()

        if (not os.path.exists("output")):
            os.makedirs(directory)

        output_file_name = "output/"+self.entity.name+".vhd"
        #to do: check if file exists. If so, emit a warning and
        #check if must clear it.
        output_file = open(output_file_name,"w+")
        for line in hdl_code:
            output_file.write(line)

        output_file.close()
        return True;

    def code(self):
        hdl_code = ""
        hdl_code = hdl_code + self.library.code()
        hdl_code = hdl_code + self.entity.code()
        hdl_code = hdl_code + self.architecture.code()
        return hdl_code
