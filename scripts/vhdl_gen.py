#################################################################################
# Copyright 2020 Ricardo F Tafas Jr
# Contrib.: T.P. Correa

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

# TODO:
# process
# Functions
# Procedures
# Custom Custom
# Block

try:
    x = tabsize
except NameError:
    tabsize = 2


def indent(value):
    txt = ""
    if value > 0:
        for j in range(tabsize * value):
            txt = txt + " "
    return txt


def VHDLenum(list):
    hdl_code = ""
    i = 0
    for j in list:
        i = i+1
        if (i == len(list)):
            hdl_code = hdl_code + list[j].code().replace(";", "")
        else:
            hdl_code = hdl_code + list[j].code()
    return hdl_code


def dictCode(DictInput, indent_level=0):
    hdl_code = ""
    for j in DictInput:
        hdl_code = hdl_code + indent(indent_level) + DictInput[j].code()
    return hdl_code

# ------------------- Library -----------------------


class PackageObj:
    def __init__(self, name, *args):
        self.source = "File Location Unknown."
        self.name = name
        if args:
            self.operator = args[0]
        else:
            self.operator = "all"


class PackageList(dict):
    def add(self, name, *args):
        self[name] = PackageObj(name)
        if args:
            self[name].operator = args[0]


class LibraryObj:
    def __init__(self, name, *args):
        self.name = name
        self.package = PackageList()

    def code(self, indent_level=0):
        hdl_code = ""
        hdl_code = hdl_code + indent(indent_level + 0) + ("library %s;\r\n" % self.name)
        for j in self.package:
            hdl_code = hdl_code + indent(indent_level + 1) + ("use %s.%s.%s;\r\n" % (self.name, j, self.package[j].operator))
        return hdl_code


class LibraryList(dict):
    def add(self, name):
        self[name] = LibraryObj(name)

    def code(self, indent_level=0):
        return dictCode(self) + "\r\n"


# ------------------- Generic -----------------------
class GenericObj:
    def __init__(self, name, type, init_value):
        self.name = name
        self.init_value = init_value
        self.type = type

    def code(self, indent_level=0):
        hdl_code = indent(indent_level + 2) + ("%s : %s := %s;\r\n" % (self.name, self.type, self.init_value))
        return hdl_code


class GenericList(dict):
    def add(self, name, type, init):
        self[name] = GenericObj(name, type, init)

    def code(self, indent_level=0):
        return VHDLenum(self)


# ------------------- Port -----------------------
class PortObj:
    def __init__(self, name, direction, type):
        self.name = name
        self.direction = direction
        self.type = type

    def code(self, indent_level=0):
        hdl_code = indent(indent_level + 2) + ("%s : %s %s;\r\n" % (self.name, self.direction, self.type))
        return hdl_code


class PortList(dict):
    def add(self, name, direction, type):
        self[name] = PortObj(name, direction, type)

    def code(self, indent_level=0):
        return VHDLenum(self)


# ------------------- Constant -----------------------
class ConstantObj:
    def __init__(self, name, type, init):
        self.name = name
        self.type = type
        self.init = init

    def code(self, indent_level=0):
        return indent(indent_level + 1) + "constant %s : %s := %s;\r\n" % (self.name, self.type, self.init)


class ConstantList(dict):
    def add(self, name, type, init):
        self[name] = ConstantObj(name, type, init)

    def code(self, indent_level=0):
        return dictCode(self)


# ------------------- Signals -----------------------
class SignalObj:
    def __init__(self, name, type, *args):
        self.name = name
        self.type = type
        if args:
            self.init = args[0]
        else:
            self.init = "undefined"

    def code(self, indent_level=0):
        if self.init != "undefined":
            return indent(indent_level + 1) + ("signal %s : %s := %s;\r\n" % (self.name, self.type, self.init))
        else:
            return indent(indent_level + 1) + ("signal %s : %s;\r\n" % (self.name, self.type))


class SignalList(dict):
    def add(self, name, type, *args):
        self[name] = SignalObj(name, type, *args)

    def code(self, indent_level=0):
        return dictCode(self)

# ------------------- Records -----------------------


class RecordObj:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def code(self, indent_level=0):
        return indent(indent_level + 1) + ("%s : %s;\r\n" % (self.name, self.type))


class RecordList(dict):
    def __init__(self, name="empty"):
        self.name = name

    def add(self, name, type):
        self[name] = RecordObj(name, type)

    def code(self, indent_level=0):
        hdl_code = indent(indent_level) + ("type %s is record\r\n" % (self.name + "_t"))
        hdl_code = hdl_code + dictCode(self, indent_level)
        hdl_code = hdl_code + indent(indent_level) + ("end record %s;\r\n" % (self.name + "_t"))
        hdl_code = hdl_code + "\r\n"
        return hdl_code

# ------------------- Variables -----------------------


class VariableObj:
    def __init__(self, name, type, *args):
        self.name = name
        self.type = type
        if args:
            self.init = args[0]
        else:
            self.init = "undefined"

    def code(self, indent_level=0):
        if self.init != "undefined":
            return indent(1) + ("variable %s : %s := %s;\r\n" % (self.name, self.type, self.init))
        else:
            return indent(1) + ("variable %s : %s;\r\n" % (self.name, self.type))


class VariableList(dict):
    def add(self, name, type, *args):
        self[name] = VariableObj(name, type, *args)

    def code(self, indent_level=0):
        return dictCode(self)


class GenericCodeBlock:
    def __init__(self, indent):
        self.list = []
        self.indent = indent

    def add(self, text):
        self.list.append(text)

    def code(self, indent_level=0):
        hdl_code = ""
        for j in self.list:
            hdl_code = hdl_code + indent(self.indent) + str(j) + "\r\n"
        return hdl_code

class functionObj:
    def __init__(self, name):
        self.name = name
        # todo: generic types here.
        self.generic = genericList()
        # function parameters in VHDL follow the same fashion as
        # generics on a portmap. name : type := init value;
        self.parameter = genericList()
        self.variable = variableList()
        self.functionBody = genericCodeBlock(1)
        self.returnType = "return_type_here"
        self.genericInstance = instanceObjList()

    def new(self, newName):
        hdl_code = "function %s is new %s\r\n" % (newName, self.name)
        hdl_code = hdl_code + indent(1)+"generic (\r\n"
        # todo: generic types here.
        if not self.genericInstance:
            for item in genericList:
                self.genericInstance.add(item,"<new value>")
        hdl_code = hdl_code + self.genericInstance.code()
        hdl_code = hdl_code + indent(1)+");\r\n"

    def declaration(self):
        hdl_code = self._code()
        hdl_code = hdl_code + indent(0) + ("return %s;\r\n" % self.returnType)
        return hdl_code

    def _code(self):
        hdl_code = indent(0) + ("function %s" % self.name)
        if (self.generic):
            hdl_code = hdl_code + ("\r\n")
            hdl_code = hdl_code + indent(1) + ("generic (\r\n")
            # todo: generic types here.
            hdl_code = hdl_code + self.generic.code()
            hdl_code = hdl_code + indent(1) + (")\r\n")
            hdl_code = hdl_code + indent(1) + ("parameter")
        if (self.parameter):
            hdl_code = hdl_code + indent(1) + (" (\r\n")
            hdl_code = hdl_code + self.parameter.code()
            hdl_code = hdl_code + indent(1) + (")\r\n")
        return hdl_code

    def code(self):
        hdl_code = self._code()
        hdl_code = hdl_code + indent(0) + ("return %s is\r\n")
        hdl_code = hdl_code + self.variable.code()
        hdl_code = hdl_code + indent(0) + ("begin\r\n")
        hdl_code = hdl_code + self.functionBody.code()
        hdl_code = hdl_code + indent(0) + ("end %s;\r\n" % self.name)
        return hdl_code

class functionObj:
    def __init__(self, name):
        self.name = name
        # todo: generic types here.
        self.generic = genericList()
        # function parameters in VHDL follow the same fashion as
        # generics on a portmap. name : type := init value;
        self.parameter = genericList()
        self.variable = variableList()
        self.functionBody = genericCodeBlock(1)
        self.returnType = "return_type_here"
        self.genericInstance = instanceObjList()

    def new(self, newName):
        hdl_code = "function %s is new %s\r\n" % (newName, self.name)
        hdl_code = hdl_code + indent(1)+"generic (\r\n"
        # todo: generic types here.
        if not self.genericInstance:
            for item in genericList:
                self.genericInstance.add(item,"<new value>")
        hdl_code = hdl_code + self.genericInstance.code()
        hdl_code = hdl_code + indent(1)+");\r\n"

    def declaration(self):
        hdl_code = self._code()
        hdl_code = hdl_code + indent(0) + ("return %s;\r\n" % self.returnType)
        return hdl_code

    def _code(self):
        hdl_code = indent(0) + ("function %s" % self.name)
        if (self.generic):
            hdl_code = hdl_code + ("\r\n")
            hdl_code = hdl_code + indent(1) + ("generic (\r\n")
            # todo: generic types here.
            hdl_code = hdl_code + self.generic.code()
            hdl_code = hdl_code + indent(1) + (")\r\n")
            hdl_code = hdl_code + indent(1) + ("parameter")
        if (self.parameter):
            hdl_code = hdl_code + indent(1) + (" (\r\n")
            hdl_code = hdl_code + self.parameter.code()
            hdl_code = hdl_code + indent(1) + (")\r\n")
        return hdl_code

    def code(self):
        hdl_code = self._code()
        hdl_code = hdl_code + indent(0) + ("return %s is\r\n")
        hdl_code = hdl_code + self.variable.code()
        hdl_code = hdl_code + indent(0) + ("begin\r\n")
        hdl_code = hdl_code + self.functionBody.code()
        hdl_code = hdl_code + indent(0) + ("end %s;\r\n" % self.name)
        return hdl_code

class componentObj:
    def __init__(self, name):
        self.name = name
        self.generic = GenericList()
        self.port = PortList()
        self.filename = ""

    def code(self, indent_level=0):
        hdl_code = indent(0) + ("component %s is\r\n" % self.name)
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
        hdl_code = hdl_code + indent(0) + ("end component;\r\n")
        hdl_code = hdl_code + "\r\n"
        return hdl_code


class ComponentList(dict):
    def add(self, name):
        self[name] = componentObj(name)

    def code(self, indent_level=0):
        hdl_code = ""
        for j in self.list:
            hdl_code = hdl_code + self.list[j].code()
        return hdl_code


# ------------------- Instance -----------------------
class InstanceObj:
    def __init__(self, name, value):
        self.name = name
        self.value = ""

    def code(self, indent_level=0):
        hdl_code = indent(2) + ("%s => %s,\r\n" % (self.name, self.value))
        return hdl_code


class InstanceObjList(dict):
    def add(self, name, type, value):
        self[name] = InstanceObj(name, value)

    def code(self, indent_level=0):
        return VHDLenum(self)


class ComponentInstanceObj:
    def __init__(self, instance_name, component_name):
        self.instance_name = instance_name
        self.component_name = component_name
        self.generic = InstanceObjList()
        self.port = InstanceObjList()
        self.filename = ""

    def code(self, indent_level=0):
        hdl_code = indent(0) + ("%s : %s\r\n" % (self.instance_name, self.component_name))
        if (self.generic):
            hdl_code = hdl_code + indent(1) + ("generic map(\r\n")
            hdl_code = hdl_code + self.generic.code()
            hdl_code = hdl_code + indent(1) + (")\r\n")
        if (self.port):
            hdl_code = hdl_code + indent(1) + ("port map(\r\n")
            hdl_code = hdl_code + self.port.code()
            hdl_code = hdl_code + indent(1) + (");\r\n")
        hdl_code = hdl_code + "\r\n"
        return hdl_code


class ComponentInstanceList(dict):
    def add(self, name):
        self[name] = ComponentInstanceObj(name)

    def code(self, indent_level=0):
        hdl_code = ""
        for j in self.list:
            hdl_code = hdl_code + self.list[j].code()
        return hdl_code

# ------------------- Entity -----------------------


class Entity:
    def __init__(self, name):
        self.name = name
        self.generic = GenericList()
        self.port = PortList()

    def code(self, indent_level=0):
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

# ------------------- Architecture -----------------------


class Architecture:
    def __init__(self, name, entity_name):
        self.name = name
        self.entityName = entity_name
        self.signal = SignalList()
        self.constant = ConstantList()
        self.component = ComponentList()
        self.functions = ""
        self.procedures = ""
        self.customTypes = GenericCodeBlock(1)
        self.declarationHeader = GenericCodeBlock(1)
        self.declarationFooter = GenericCodeBlock(1)
        self.bodyCodeHeader = GenericCodeBlock(1)
        self.instances = ""
        self.blocks = ""
        self.process = ""
        self.bodyCodeFooter = GenericCodeBlock(1)

    def code(self, indent_level=0):
        hdl_code = ""
        hdl_code = indent(0) + ("architecture %s of %s is\r\n" % (self.name, self.entityName))
        hdl_code = hdl_code + "\r\n"
        if (self.declarationHeader):
            hdl_code = hdl_code + self.declarationHeader.code()
            hdl_code = hdl_code + "\r\n"
        if (self.constant):
            hdl_code = hdl_code + self.constant.code()
            hdl_code = hdl_code + "\r\n"
        if (self.customTypes):
            hdl_code = hdl_code + self.customTypes.code()
            hdl_code = hdl_code + "\r\n"
        if (self.component):
            hdl_code = hdl_code + self.component.code()
            hdl_code = hdl_code + "\r\n"
        if (self.signal):
            hdl_code = hdl_code + self.signal.code()
            hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + indent(1) + ("--architecture_declaration_tag\r\n")
        hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + indent(0) + ("begin\r\n")
        hdl_code = hdl_code + "\r\n"
        if (self.bodyCodeHeader):
            hdl_code = hdl_code + self.bodyCodeHeader.code()
            hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + indent(1) + ("--architecture_body_tag.\r\n")
        hdl_code = hdl_code + "\r\n"
        if (self.bodyCodeHeader):
            hdl_code = hdl_code + self.bodyCodeFooter.code()
            hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + indent(0) + ("end %s;\r\n" % self.name)
        hdl_code = hdl_code + "\r\n"
        return hdl_code


class BasicVHDL:
    def __init__(self, entity_name, architecture_name):
        self.library = LibraryList()
        self.entity = Entity(entity_name)
        self.architecture = Architecture(architecture_name, entity_name)

    def instance(self, instance_name, generic_list, port_list):
        self.tmpinst = ComponentInstanceObj()
        for j in self.entity.generic.list:
            self.tmpinst.generic.add(j.name, j.value)
        for j in generic_list:
            self.tmpinst.generic[j.name].value = [j.name]
        for j in self.entity.port.list:
            self.tmpinst.port.add(j.name, j.value)
        for j in port_list:
            self.tmpinst.generic[j.name].value = [j.name]
        return self.tmpinst.code()

    def write_file(self):
        hdl_code = self.code()

        if (not os.path.exists("output")):
            os.makedirs("output")

        output_file_name = "output/"+self.entity.name+".vhd"
        # to do: check if file exists. If so, emit a warning and
        # check if must clear it.
        output_file = open(output_file_name, "w+")
        for line in hdl_code:
            output_file.write(line)

        output_file.close()
        return True

    def code(self, indent_level=0):
        hdl_code = ""
        hdl_code = hdl_code + self.library.code()
        hdl_code = hdl_code + self.entity.code()
        hdl_code = hdl_code + self.architecture.code()
        return hdl_code
