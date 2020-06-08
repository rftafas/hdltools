import sys
import os

#TODO:
#Process
#Instances
#Component
#Functions
#Procedures
#Custom Custom
#Block

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

def VHDLenum(list):
    hdl_code = ""
    i = 0
    for j in list:
        i = i+1
        if (i == len(list)):
            hdl_code = hdl_code + list[j].code().replace(";","")
        else:
            hdl_code = hdl_code + list[j].code()
    return hdl_code

def DictCode(DictInput):
    hdl_code = ""
    for j in DictInput:
        hdl_code = hdl_code + DictInput[j].code()
    return hdl_code

class PackageObj:
    def __init__(self, name, *args):
        self.name = name
        if args:
            self.operator = args[0]
        else:
            self.operator = "all"

class PackageList(dict):
    def add(self, name, *args):
        self[name] = PackageObj(name)
        if args:
            self[name].operator = arg[0]

class LibraryObj:
    def __init__(self, name, *args):
        self.name = name
        self.package = PackageList()
    def code(self):
        hdl_code = ""
        hdl_code = hdl_code + indent(0) + ("library %s;\r\n" % self.name)
        for j in self.package:
            hdl_code = hdl_code + indent(1) + ("use %s.%s.%s;\r\n" % (self.name, j, self.package[j].operator))
        return hdl_code

class LibraryList(dict):
    def add(self, name):
        self[name] = LibraryObj(name)
    def code(self):
        return DictCode(self) + "\r\n"

class GenericObj:
    def __init__(self, name, type, init_value):
        self.name = name
        self.init = init_value
        self.type = type
    def code(self):
        hdl_code = indent(2) + ("%s : %s := %s;\r\n" % (self.name, self.type, self.init))
        return hdl_code

class PortObj:
    def __init__(self, name, direction, type):
        self.name = name
        self.direction = direction
        self.type = type
    def code(self):
        hdl_code = indent(2) + ("%s : %s %s;\r\n" % (self.name, self.direction, self.type))
        return hdl_code

class GenericList(dict):
    def add(self, name, type, init):
        self[name] = GenericObj(name,type,init)
    def code(self):
        return VHDLenum(self)

class PortList(dict):
    def add(self, name, direction, type):
        self[name] = PortObj(name, direction, type)
    def code(self):
        return VHDLenum(self)

class ConstantObj:
    def __init__(self, name, type, init):
        self.name = name
        self.type = type
        self.init = init
    def code(self):
        return indent(1) + "constant %s : %s := %s;\r\n" % (self.name, self.type, self.init)

class SignalObj:
    def __init__(self, name, type, *args):
        self.name = name
        self.type = type
        if args:
            self.init = args[0]
        else:
            self.init = "undefined"
    def code(self):
        if self.init != "undefined":
            return indent(1) + ("signal %s : %s := %s;\r\n" % (self.name, self.type, arg[0]))
        else:
            return indent(1) + ("signal %s : %s;\r\n" % (self.name, self.type))

class VariableObj:
    def __init__(self, name, type, *args):
        self.name = name
        self.type = type
        if args:
            self.init = args[0]
        else:
            self.init = "undefined"
    def code(self):
        if self.init != "undefined":
            return indent(1) + ("variable %s : %s := %s;\r\n" % (self.name, self.type, arg[0]))
        else:
            return indent(1) + ("variable %s : %s;\r\n" % (self.name, self.type))

class ConstantList(dict):
    def add(self,name,type,init):
        self[name] = ConstantObj(name,type,init)
    def code(self):
        return DictCode(self)

class SignalList(dict):
    def add(self,name,type,*args):
        self[name] = SignalObj(name,type,*args)
    def code(self):
        return DictCode(self)

class VariableList(dict):
    def add(self,name,type,*args):
        self[name] = VariableObj(name,type,*args)
    def code(self):
        return DictCode(self)

class GenericCodeBlock:
    def __init__(self, indent):
        self.list = []
        self.indent = indent
    def add(self,text):
        self.list.append(text)
    def code(self):
        hdl_code = ""
        for j in self.list:
            hdl_code = hdl_code + indent(self.indent) + str(j) + "\r\n"
        return hdl_code

class Entity:
    def __init__(self, name):
        self.name    = name
        self.generic = GenericList()
        self.port    = PortList()

    def code(self):
        hdl_code = indent(0) + ("entity %s is\r\n" % self.name)
        if (self.generic):
            hdl_code = hdl_code + indent(1) + ("generic (\r\n")
            hdl_code = hdl_code + self.generic.code()
            hdl_code = hdl_code + indent(1) + (");\r\n")
        else:
            hdl_code = hdl_code + indent(1) + ("--generic (\r\n")
            hdl_code = hdl_code + indent(2) + ("--generic_declaration_tag\r\n")
            hdl_code = hdl_code + indent(1) + ("--);\r\n")
        if (self.port):
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

class Architecture:
    def __init__(self, name, entity_name):
        self.name = name
        self.EntityName = entity_name
        self.Signal = SignalList()
        self.Constant = ConstantList()
        self.Functions = ""
        self.Procedures = ""
        self.CustomTypes = ""
        self.DeclarationHeader = GenericCodeBlock(1)
        self.DeclarationFooter = GenericCodeBlock(1)
        self.BodyCodeHeader = GenericCodeBlock(1)
        self.Instances = ""
        self.Blocks = ""
        self.Process = ""
        self.BodyCodeFooter = GenericCodeBlock(1)

    def code(self):
        hdl_code = ""
        hdl_code = indent(0) + ("architecture %s of %s is\r\n" % (self.name, self.EntityName))
        hdl_code = hdl_code + "\r\n"
        if (self.DeclarationHeader):
            hdl_code = hdl_code + self.DeclarationHeader.code()
            hdl_code = hdl_code + "\r\n"
        if (self.Constant):
            hdl_code = hdl_code + self.Constant.code()
            hdl_code = hdl_code + "\r\n"
        if (self.Signal):
            hdl_code = hdl_code + self.Signal.code()
            hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + indent(1) + ("--architecture_declaration_tag\r\n")
        hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + indent(0) + ("begin\r\n")
        hdl_code = hdl_code + "\r\n"
        if (self.BodyCodeHeader):
            hdl_code = hdl_code + self.BodyCodeHeader.code()
            hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + indent(1) + ("--architecture_body_tag.\r\n")
        hdl_code = hdl_code + "\r\n"
        if (self.BodyCodeHeader):
            hdl_code = hdl_code + self.BodyCodeFooter.code()
            hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + indent(0) + ("end %s;\r\n" % self.name)
        hdl_code = hdl_code + "\r\n"
        return hdl_code

class BasicVHDL:
    def __init__(self, entity_name, architecture_name):
        self.Library      = LibraryList()
        self.Entity       = Entity(entity_name)
        self.Architecture = Architecture(architecture_name, entity_name)

    def write_file(self):
        hdl_code = self.code()

        if (not os.path.exists("output")):
            os.makedirs(directory)

        output_file_name = "output/"+self.Entity.name+".vhd"
        #to do: check if file exists. If so, emit a warning and
        #check if must clear it.
        output_file = open(output_file_name,"w+")
        for line in hdl_code:
            output_file.write(line)

        output_file.close()
        return True;

    def code(self):
        hdl_code = ""
        hdl_code = hdl_code + self.Library.code()
        hdl_code = hdl_code + self.Entity.code()
        hdl_code = hdl_code + self.Architecture.code()
        return hdl_code
