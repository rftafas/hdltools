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
# Contributor list:
# 2020 - Ricardo F Tafas Jr - https://github.com/rftafas
# 2020 - T.P. Correa - https://github.com/tpcorrea

import sys
import os

# TODO:
# Process
# Procedures
# Block
# Protected Types


# NOTE:
# The license below may be changed to be compliant to those using these
# generators. The generator itself is licensed under Apache as stated above.
license_text = """---------------------------------------------------------------------------------
-- This is free and unencumbered software released into the public domain.
--
-- Anyone is free to copy, modify, publish, use, compile, sell, or
-- distribute this software, either in source code form or as a compiled
-- binary, for any purpose, commercial or non-commercial, and by any
-- means.
--
-- In jurisdictions that recognize copyright laws, the author or authors
-- of this software dedicate any and all copyright interest in the
-- software to the public domain. We make this dedication for the benefit
-- of the public at large and to the detriment of our heirs and
-- successors. We intend this dedication to be an overt act of
-- relinquishment in perpetuity of all present and future rights to this
-- software under copyright law.
--
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
-- EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
-- MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
-- IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
-- OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
-- ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
-- OTHER DEALINGS IN THE SOFTWARE.
--
-- For more information, please refer to <http://unlicense.org/>
---------------------------------------------------------------------------------
"""

try:
    x = tabsize
except NameError:
    tabsize = 2


def indent(value):
    txt = ""
    if value > 0:
        j = 0
        while j < tabsize * value:
            txt = txt + " "
            j += 1
    return txt


def VHDLenum(list, indent_level = 0):
    hdl_code = ""
    i = 0
    for j in list:
        i = i+1
        if (i == len(list)):
            tmp = list[j].code()
            tmp = tmp.replace(";", "")
            tmp = tmp.replace(",", "")
            hdl_code = hdl_code + indent(indent_level) + tmp
        else:
            hdl_code = hdl_code + indent(indent_level) + list[j].code()
    return hdl_code


def DictCode(DictInput, indent_level = 0):
    hdl_code = ""
    for j in DictInput:
        hdl_code = hdl_code + indent(indent_level) + DictInput[j].code()
    return hdl_code


# ------------------- GenericCodeBlock -----------------------

class SingleCodeLine:
    def __init__(self, value, line_end=""):
        self.value = value
        self.line_end = line_end

    def code(self):
        return self.value+self.line_end
        

class GenericCodeBlock:
    def __init__(self, indent_level = 0):
        self.list = []
        self.indent = indent_level

    def __call__(self):
        pass

    def add(self, text):
        self.list.append(text)

    def code(self, indent_level = 0):
        if indent_level:
            self.indent = indent_level
        hdl_code = ""
        for j in self.list:
            hdl_code = hdl_code + indent(self.indent) + str(j) + "\r\n"
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

    def code(self, libname="work"):
        hdl_code = ""
        indent_tmp = 1
        if (libname == "work"):
            indent_tmp = 0
        hdl_code = hdl_code + indent(indent_tmp) + ("use %s.%s.%s;\r\n" % (libname, self.name, self.operator))
        if (libname == "work"):
            hdl_code = hdl_code + "\r\n"
        return hdl_code


class PackageList(dict):
    def add(self, name, *args):
        self[name] = PackageObj(name)
        if args:
            self[name].operator = args[0]

    def code(self, libname="work"):
        hdl_code = ""
        for eachPkg in self:
            hdl_code = hdl_code + self[eachPkg].code(libname)
        return hdl_code


class ContextObj:
    def __init__(self, name):
        self.source = "File Location Unknown."
        self.name = name


class ContextList(dict):
    def add(self, name):
        self[name] = ContextObj(name)


class LibraryObj:
    def __init__(self, name, *args):
        self.name = name
        self.package = PackageList()
        self.context = ContextList()

    def code(self, indent_level=0):
        hdl_code = ""
        hdl_code = hdl_code + indent(indent_level + 0) + ("library %s;\r\n" % self.name)
        for j in self.context:
            hdl_code = hdl_code + indent(indent_level + 1) + ("context %s.%s;\r\n" % (self.name, self.context[j].name))
        hdl_code = hdl_code + self.package.code(self.name)
        return hdl_code


class LibraryList(dict):
    def add(self, name):
        self[name] = LibraryObj(name)

    def code(self, indent_level=0):
        return DictCode(self) + "\r\n"


# ------------------- Generic -----------------------


class GenericObj:
    def __init__(self, name, type, value):
        self.name = name
        self.value = value
        self.type = type

    def code(self, indent_level=0):
        if self.value:
            hdl_code = indent(indent_level) + ("%s : %s := %s;\r\n" % (self.name, self.type, self.value))
        else:
            hdl_code = indent(indent_level) + ("%s : %s;\r\n" % (self.name, self.type))
        return hdl_code


class GenericList(dict):
    def add(self, name, type, value):
        self[name] = GenericObj(name, type, value)

    def code(self, indent_level=0):
        return VHDLenum(self,indent_level)


# ------------------- Port -----------------------


class PortObj:
    def __init__(self, name, direction, type, value):
        self.name = name
        self.direction = direction
        self.type = type
        self.value = value
    
    def code(self, indent_level=0):
        if self.value is None:
            hdl_code = indent(indent_level) + ("%s : %s %s;\r\n" % (self.name, self.direction, self.type))
        else:
            hdl_code = indent(indent_level) + ("%s : %s %s := %s;\r\n" %
                                              (self.name, self.direction, self.type, self.value))
        return hdl_code


class PortList(dict):
    def add(self, name, direction, type, value=None):
        self[name] = PortObj(name, direction, type, value)

    def append(self, port_obj):
        if isinstance(port_obj, PortObj):
            self[port_obj.name] = port_obj
        else:
            pass
            #print("Appended element must be of class PortObj")

    def code(self, indent_level=0):
        return VHDLenum(self,indent_level)

# ------------------- Custom Types -----------------------


class IncompleteTypeObj:
    def __init__(self, name):
        self.name = name

    def code(self):
        hdl_code = ""
        hdl_code = "type %s;\r\n" % self.name
        hdl_code = hdl_code + "\r\n"
        return hdl_code


class EnumerationTypeObj:
    def __init__(self, name, *args):
        self.name = name
        self.type = type
        self.typeElement = dict()
        self.newLine = False
        self.endLine = ", "

        if args:
            self.add(args[0])

    def SetNewLine(self, input):
        pass
        if input:
            self.newLine = True
            self.endLine = ",\r\n"
        else:
            self.newLine = False
            self.endLine = ", "
        for element in self.typeElement:
            self.typeElement[element].line_end = self.endLine

    def add(self, input):
        if isinstance(input, str):
            self.typeElement[input] = SingleCodeLine(input, self.endLine)
        else:
            for element in input:
                self.typeElement[element] = SingleCodeLine(element, self.endLine)

    def code(self, indent_level=1):
        hdl_code = ""
        if self.typeElement:
            hdl_code =  hdl_code + indent(indent_level) + "type %s is ( " % self.name
            if self.newLine:
                hdl_code = hdl_code + "\r\n"
                hdl_code = hdl_code + "%s" % VHDLenum(self.typeElement, indent_level+1)
                hdl_code = hdl_code + indent(indent_level)
            else:
                hdl_code = hdl_code + "%s" % VHDLenum(self.typeElement)
            hdl_code = hdl_code + ");\r\n" 
            hdl_code = hdl_code + "\r\n"
        return hdl_code


class ArrayTypeObj:
    def __init__(self, name, *args):
        self.name = name
        self.arrayRange = args[0]
        self.arrayType = args[1]

    def code(self):
        hdl_code = ""
        hdl_code = indent(1) + "type %s is array (%s) of %s;\r\n" % (self.name, self.arrayRange, self.arrayType)
        hdl_code = hdl_code + "\r\n"
        return hdl_code


class RecordTypeObj:
    def __init__(self, name, *args):
        self.name = name

        if args:
            if isinstance(args[0], GenericList):
                self.element = args[0]
        else:
            self.element = GenericList()

    def add(self, name, type, init=None):
        self.element.add(name, type, init)

    def code(self):
        hdl_code = ""
        hdl_code = hdl_code + indent(1) + "type %s is record\r\n" % self.name
        for j in self.element:
            hdl_code = hdl_code + indent(2) + "%s : %s;\n\r" % (self.element[j].name, self.element[j].type)
        hdl_code = hdl_code + "end record %s;\r\n" % self.name
        hdl_code = hdl_code + "\r\n"
        return hdl_code

class SubTypeObj:
    def __init__(self, name, *args):
        self.name = name
        self.ofType = args[0]
        self.element = GenericList()

    def add(self, name, type, init=None):
        self.element.add(name, type, init)

    def code(self):
        hdl_code = ""
        hdl_code = hdl_code + indent(1) + "subtype %s is %s (\r\n" % (self.name, self.ofType)
        i = 0
        for j in self.element:
            i += 1
            if (i == len(self.element)):
                hdl_code = hdl_code + indent(2) + "%s (%s)); \n\r" % (self.element[j].name, self.element[j].type)
            else:
                hdl_code = hdl_code + indent(2) + "%s (%s),\n\r" % (self.element[j].name, self.element[j].type)
        hdl_code = hdl_code + "\r\n"
        return hdl_code


class CustomTypeList(dict):
    def add(self, name, type, *args):
        if "Array" in type:
            self[name] = ArrayTypeObj(name, *args)
        elif "Enumeration" in type:
            self[name] = EnumerationTypeObj(name, *args)
        elif "Record" in type:
            self[name] = RecordTypeObj(name, *args)
        elif "SubType" in type:
            self[name] = SubTypeObj(name, *args)
        else:
            self[name] = IncompleteTypeObj(name)

    def code(self, indent_level=0):
        return DictCode(self)


# ------------------- Constant -----------------------


class ConstantObj:
    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value

    def code(self, indent_level=0):
        return indent(indent_level + 1) + "constant %s : %s := %s;\r\n" % (self.name, self.type, self.value)


class ConstantList(dict):
    def add(self, name, type, value):
        self[name] = ConstantObj(name, type, value)

    def code(self, indent_level=0):
        return DictCode(self)


# ------------------- Custom Type Constant List -----------------------


class RecordConstantObj(RecordTypeObj):
    def __init__(self, name, record):
        self.name = name
        if isinstance(record,RecordTypeObj):
            self.element = record.element
            self.recordName  = record.name
        else:
            print("Error: object must be of record type.")

    def code(self):
        hdl_code = ""
        hdl_code = hdl_code + "constant %s : %s := (\r\n" % (self.name, self.recordName)
        i = 0
        for j in self.element:
            i += 1
            if self.element[j].init is None:
                init = "'0'"
            else:
                init = self.element[j].init
            if (i == len(self.element)):
                hdl_code = hdl_code + indent(1) + "%s => %s\n\r" % (self.element[j].name, init)
            else:
                hdl_code = hdl_code + indent(1) + "%s => %s,\n\r" % (self.element[j].name, init)
        hdl_code = hdl_code + ");\r\n"
        hdl_code = hdl_code + "\r\n"
        return hdl_code

class CustomTypeConstantList(dict):
    def add(self, name, type, value):
        if isinstance(type,RecordTypeObj):
            self[name] = RecordConstantObj(name,type)
        else:
            self[name] = GenericObj(name,type,value)

    def code(self, indent_level=0):
        return DictCode(self)


# ------------------- Signals -----------------------


class SignalObj:
    def __init__(self, name, type, *args):
        self.name = name
        self.type = type
        if args:
            self.value = args[0]
        else:
            self.value = ""

    def code(self, indent_level=0):
        if self.value:
            return indent(indent_level + 1) + ("signal %s : %s := %s;\r\n" % (self.name, self.type, self.value))
        else:
            return indent(indent_level + 1) + ("signal %s : %s;\r\n" % (self.name, self.type))


class SignalList(dict):
    def add(self, name, type, *args):
        self[name] = SignalObj(name, type, *args)

    def code(self, indent_level=0):
        return DictCode(self)


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
        return DictCode(self)


# ------------------- Functions & Procedures -----------------------


class FunctionObj:
    def __init__(self, name):
        self.name = name
        # todo: generic types here.
        self.customTypes = CustomTypeList()
        self.generic = GenericList()
        # function parameters in VHDL follow the same fashion as
        # generics on a portmap. name : type := init value;
        self.parameter = GenericList()
        self.variable = VariableList()
        self.functionBody = GenericCodeBlock(1)
        self.returnType = "return_type_here"
        self.genericInstance = InstanceObjList()

    def new(self, newName):
        hdl_code = "function %s is new %s\r\n" % (newName, self.name)
        hdl_code = hdl_code + indent(1)+"generic (\r\n"
        # todo: generic types here.
        if not self.genericInstance:
            for item in self.genericInstance:
                self.genericInstance.add(item, "<new value>")
        hdl_code = hdl_code + self.genericInstance.code()
        hdl_code = hdl_code + indent(1)+");\r\n"

    def declaration(self):
        hdl_code = self._code()
        hdl_code = hdl_code + indent(0) + ("return %s;\r\n" % self.returnType)
        return hdl_code

    def _code(self):
        hdl_code = indent(0) + ("function %s" % self.name)
        if (self.generic | self.customTypes):
            hdl_code = hdl_code + ("\r\n")
            hdl_code = hdl_code + indent(1) + ("generic (\r\n")
            if (self.customTypes):
                hdl_code = hdl_code + self.customTypes.code()
            if (self.generic):
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


class ProcedureObj:
    def __init__(self, name):
        self.name = name

    def new(self):
        hdl_code = "--Not implemented."
        return hdl_code

    def declaration(self):
        hdl_code = "--Procedure Declaration not Implemented."
        return hdl_code

    def code(self):
        hdl_code = "--Procedure Code not Implemented."
        return hdl_code


class SubProgramList(dict):
    def add(self, name, type):
        if type == "Function":
            self[name] = FunctionObj(name)
        elif type == "Procedure":
            self[name] = ProcedureObj(name)
        else:
            print("Error. Select \"Function\" or \"Procedure\". Keep the quotes.")

    def declaration(self, indent_level=0):
        hdl_code = ""
        for j in self:
            hdl_code = hdl_code + self[j].declaration()
        return hdl_code

    def code(self, indent_level=0):
        hdl_code = ""
        for j in self:
            hdl_code = hdl_code + self[j].code()
        return hdl_code

# ------------------- Component -----------------------


class ComponentObj:
    def __init__(self, name):
        self.name = name
        self.generic = GenericList()
        self.port = PortList()
        self.filename = ""

    def code(self, indent_level=0):
        hdl_code = ""
        hdl_code = hdl_code + indent(1) + ("component %s is\r\n" % self.name)
        if (self.generic):
            hdl_code = hdl_code + indent(2) + ("generic (\r\n")
            hdl_code = hdl_code + self.generic.code(3)
            hdl_code = hdl_code + indent(2) + (");\r\n")
        else:
            hdl_code = hdl_code + indent(2) + ("--generic (\r\n")
            hdl_code = hdl_code + indent(3) + ("--generic_declaration_tag\r\n")
            hdl_code = hdl_code + indent(2) + ("--);\r\n")
        if (self.port):
            hdl_code = hdl_code + indent(2) + ("port (\r\n")
            hdl_code = hdl_code + self.port.code(3)
            hdl_code = hdl_code + indent(2) + (");\r\n")
        else:
            hdl_code = hdl_code + indent(2) + ("--port (\r\n")
            hdl_code = hdl_code + indent(3) + ("--port_declaration_tag\r\n")
            hdl_code = hdl_code + indent(2) + ("--);\r\n")
        hdl_code = hdl_code + indent(1) + ("end component;\r\n")
        hdl_code = hdl_code + "\r\n"
        return hdl_code


class ComponentList(dict):
    def add(self, name):
        self[name] = ComponentObj(name)

    def append(self, component_obj):
        if isinstance(component_obj, ComponentObj):
            self[component_obj.name] = component_obj

    def code(self, indent_level=0):
        return DictCode(self)

# ------------------- Instance -----------------------


class InstanceObj:
    def __init__(self, name, value=""):
        self.name = name
        if value == "":
            self.value = name
        else:
            self.value = value
    
    def code(self, indent_level=3):
        hdl_code = indent(indent_level) + ("%s => %s,\r\n" % (self.name, self.value))
        return hdl_code


class InstanceObjList(dict):
    def add(self, name, value=""):
        if value == "":
            self[name] = InstanceObj(name, name)
        self[name] = InstanceObj(name, value)

    def code(self, indent_level=0):
        return VHDLenum(self)


class ComponentInstanceObj:
    def __init__(self, component_name, *args):
        self.component_name = component_name
        self.instance_name = component_name + "_u"
        if args:
            self.instance_name = args[0]
            
        self.generic = InstanceObjList()
        self.port = InstanceObjList()
        self.filename = ""
          
    def __call__(self, instance_name):
        self.instance_name = instance_name
        return self.code()
    
    def read(self, input):
        if isinstance(input,GenericList):
            for j in input:
                self.generic.add(j)

        if isinstance(input,PortList):
            for j in input:
                self.port.add(j)


    def code(self, indent_level=1):
        hdl_code = indent(indent_level) + ("%s : %s\r\n" % (self.instance_name, self.component_name))
        if (self.generic):
            hdl_code = hdl_code + indent(indent_level+1) + ("generic map (\r\n")
            hdl_code = hdl_code + self.generic.code(indent_level+2)
        if (self.port):
            hdl_code = hdl_code + indent(indent_level+1) + (")\r\n")
            hdl_code = hdl_code + indent(indent_level+1) + ("port map (\r\n")
            hdl_code = hdl_code + self.port.code(indent_level+2)
        hdl_code = hdl_code + indent(2) + (");\r\n")
        hdl_code = hdl_code + "\r\n"
        return hdl_code


class ComponentInstanceList(dict):
    def add(self, component_name, instance_name):
        self[instance_name] = ComponentInstanceObj(component_name,instance_name)

    def append(self, input):
        if isinstance(input,ComponentInstanceObj):
            self[input.instance_name] = input

    def code(self, indent_level=0):
        hdl_code = ""
        for j in self:
            hdl_code = hdl_code + self[j].code()
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
            hdl_code = hdl_code + self.generic.code(2)
            hdl_code = hdl_code + indent(1) + (");\r\n")
        else:
            hdl_code = hdl_code + indent(1) + ("--generic (\r\n")
            hdl_code = hdl_code + indent(2) + ("--generic_declaration_tag\r\n")
            hdl_code = hdl_code + indent(1) + ("--);\r\n")
        if (self.port):
            hdl_code = hdl_code + indent(1) + ("port (\r\n")
            hdl_code = hdl_code + self.port.code(2)
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
        self.subPrograms = SubProgramList()
        self.customTypes = CustomTypeList()
        self.customTypesConstants = CustomTypeConstantList()
        self.declarationHeader = GenericCodeBlock(1)
        self.declarationFooter = GenericCodeBlock(1)
        self.bodyCodeHeader = GenericCodeBlock(1)
        self.instances = ComponentInstanceList()
        self.blocks = ""
        self.process = ""
        self.bodyCodeFooter = GenericCodeBlock(1)

    def code(self, indent_level=0):
        hdl_code = ""
        hdl_code = indent(0) + ("architecture %s of %s is\r\n" % (self.name, self.entityName))
        hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + indent(1) + ("--architecture_declaration_tag\r\n")
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
        if (self.customTypesConstants):
            hdl_code = hdl_code + self.customTypesConstants.code()
            hdl_code = hdl_code + "\r\n"
        if (self.component):
            hdl_code = hdl_code + self.component.code()
            hdl_code = hdl_code + "\r\n"
        if (self.signal):
            hdl_code = hdl_code + self.signal.code()
            hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + indent(0) + ("begin\r\n")
        hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + indent(1) + ("--architecture_body_tag.\r\n")
        hdl_code = hdl_code + "\r\n"
        if (self.bodyCodeHeader):
            hdl_code = hdl_code + self.bodyCodeHeader.code()
            hdl_code = hdl_code + "\r\n"
        # blocks will come here.
        # process will come here.
        if (self.instances):
            hdl_code = hdl_code + self.instances.code()
            hdl_code = hdl_code + "\r\n"
        if (self.bodyCodeFooter):
            hdl_code = hdl_code + self.bodyCodeFooter.code()
            hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + indent(0) + ("end %s;\r\n" % self.name)
        hdl_code = hdl_code + "\r\n"
        return hdl_code


class BasicVHDL:
    def __init__(self, entity_name, architecture_name):
        self.fileHeader = GenericCodeBlock(0)
        self.fileHeader.add(license_text)
        self.library = LibraryList()
        self.work = PackageList()
        self.entity = Entity(entity_name)
        self.architecture = Architecture(architecture_name, entity_name)
        self.instance = ComponentInstanceObj(self.entity.name,self.entity.name+"_u")

    def object(self):
        self.component = ComponentObj(self.entity.name)
        self.component.generic = self.entity.generic
        self.component.port = self.entity.port
        return self.component
    
    def declaration(self):
        tmp = self.object()
        return tmp.code()

    def instanciation(self, instance_name=""):
        self.instance.read(self.entity.generic)
        self.instance.read(self.entity.port)
        self.instance.instance_name = instance_name
        if instance_name == "":
            instance_name = self.entity.name+"_u"
        return self.instance

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
        hdl_code = hdl_code + self.fileHeader.code()
        hdl_code = hdl_code + self.library.code()
        hdl_code = hdl_code + self.work.code()
        hdl_code = hdl_code + self.entity.code()
        hdl_code = hdl_code + self.architecture.code()
        return hdl_code


if __name__ == '__main__':

    ram = BasicVHDL("ram", "behavioral")
    ram.library.add("IEEE")
    ram.library["IEEE"].package.add("std_logic_1164")
    ram.library["IEEE"].package.add("numeric_std")
    ram.library.add("expert")
    ram.library["expert"].package.add("std_logic_expert")

    ram.entity.generic.add("data_size", "positive", "8")
    ram.entity.generic.add("addr_size", "positive", "4")

    ram.entity.port.add("rst_i", "in", "std_logic")
    ram.entity.port.add("clk_i", "in", "std_logic")
    ram.entity.port.add("we_i", "in", "std_logic")
    ram.entity.port.add("data_i", "in", "std_logic_vector(data_size-1 downto 0)")
    ram.entity.port.add("data_o", "out", "std_logic_vector(data_size-1 downto 0)")
    ram.entity.port.add("addr_i", "in", "std_logic_vector(addr_size-1 downto 0)")
    ram.entity.port.add("addr_o", "in", "std_logic_vector(addr_size-1 downto 0)")

    ram.architecture.customTypes.add("ram_t", "Array", "2**addr_size-1 downto 0", "std_logic_vector(data_size-1 downto 0)")

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

    print("############################# Ram Source Code ###############################")
    print(ram.code())
    print("########################### Declaration Template ############################")
    print(ram.declaration())
    print("########################## Instantiation Template ###########################")
    print(ram.instanciation("ram_inst"))
    ram.write_file()
