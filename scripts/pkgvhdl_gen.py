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
import vhdl_gen as vhdl
import math


class PackageDeclarationObj:
    def __init__(self, name):
        self.name = name
        self.generic = vhdl.GenericList()
        self.constant = vhdl.ConstantList()
        self.component = vhdl.ComponentList()
        self.record = vhdl.RecordList()
        self.signal = vhdl.SignalList()
        self.functions = ""
        self.procedures = ""
        self.customTypes = vhdl.GenericCodeBlock(1)
        self.declarationHeader = vhdl.GenericCodeBlock(1)
        self.declarationFooter = vhdl.GenericCodeBlock(1)

    def code(self, indent_level=0):
        hdl_code = vhdl.indent(indent_level) + ("package %s is\r\n" % self.name)
        # Constants
        hdl_code = hdl_code + vhdl.indent(indent_level+1) + ("-- constants  (\r\n")
        if (self.constant):
            hdl_code = hdl_code + self.constant.code(indent_level+1)
            hdl_code = hdl_code + "\r\n"
        else:
            hdl_code = hdl_code + vhdl.indent(indent_level+2) + ("--constant_declaration_tag\r\n")
            hdl_code = hdl_code + vhdl.indent(indent_level+1) + ("--);\r\n")

        # Records
        for i in self.record:
            hdl_code = hdl_code + vhdl.indent(indent_level+1) + ("-- records (\r\n")
            if (self.record[i]):
                hdl_code = hdl_code + self.record[i].code(indent_level+1)
            else:
                hdl_code = hdl_code + vhdl.indent(indent_level+2) + ("-- records_declaration_tag\r\n")
                hdl_code = hdl_code + vhdl.indent(indent_level+1) + ("--);\r\n")

        # Record initialization constants
        hdl_code = hdl_code + vhdl.indent(indent_level+1) + ("-- records initialization constants (\r\n")
        for i in self.record:
            if (self.record[i]):
                hdl_code = hdl_code + self.record[i].code_init(indent_level+1)
            else:
                hdl_code = hdl_code + vhdl.indent(indent_level+2) + ("-- records_init_declaration_tag\r\n")
                hdl_code = hdl_code + vhdl.indent(indent_level+1) + ("--);\r\n")

        hdl_code = hdl_code + vhdl.indent(indent_level) + ("end %s;\r\n" % self.name)
        hdl_code = hdl_code + "\r\n"
        return hdl_code


class PackageBodyObj:
    def __init__(self, name):
        self.name = name
        self.functions = ""
        self.procedures = ""
        self.bodyCodeHeader = vhdl.GenericCodeBlock(1)
        self.bodyCodeFooter = vhdl.GenericCodeBlock(1)

    def code(self, indent_level=0):
        hdl_code = ""
        hdl_code = vhdl.indent(indent_level) + ("package body %s is\r\n" % self.name)
        hdl_code = hdl_code + "\r\n"
        if (self.bodyCodeHeader):
            hdl_code = hdl_code + self.bodyCodeHeader.code(indent_level)
            hdl_code = hdl_code + "\r\n"
        if (self.functions):
            #hdl_code = hdl_code + self.functions.code()
            hdl_code = hdl_code + "\r\n"
        if (self.procedures):
            #hdl_code = hdl_code + self.procedures.code()
            hdl_code = hdl_code + "\r\n"
        if (self.bodyCodeHeader):
            hdl_code = hdl_code + self.bodyCodeFooter.code(indent_level)
            hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + vhdl.indent(indent_level) + ("end package body;\r\n")
        hdl_code = hdl_code + "\r\n"
        return hdl_code


class PkgVHDL:
    def __init__(self, name):
        self.library = vhdl.LibraryList()
        self.declaration = PackageDeclarationObj(name)
        self.body = PackageBodyObj(name)

    def addRecord(self, name):
        self.declaration.record[name] = vhdl.RecordList(name)

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

    def code(self):
        hdl_code = ""
        hdl_code = hdl_code + self.library.code()
        hdl_code = hdl_code + self.declaration.code()
        hdl_code = hdl_code + self.body.code()
        return hdl_code
