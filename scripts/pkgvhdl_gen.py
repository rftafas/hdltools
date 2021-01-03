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
# Contributor list:
# 2020 - Ricardo F Tafas Jr - https://github.com/rftafas
# 2020 - T.P. Correa - https://github.com/tpcorrea

import sys
import os
import vhdl_gen as vhdl
import math


class PackageDeclarationObj:
    def __init__(self, name):
        self.name = name
        self.generic = vhdl.GenericList()
        self.genericTypes = vhdl.CustomTypeList()
        self.constant = vhdl.ConstantList()
        self.component = vhdl.ComponentList()
        self.signal = vhdl.SignalList()
        self.subPrograms = vhdl.SubProgramList()
        self.customTypes = vhdl.CustomTypeList()
        self.declarationHeader = vhdl.GenericCodeBlock(1)
        self.declarationFooter = vhdl.GenericCodeBlock(1)

    def code(self, indent_level=0):
        hdl_code = ""
        hdl_code = vhdl.indent(indent_level) + ("package %s is\r\n" % self.name)
        hdl_code = hdl_code + "\r\n"
        # Pkg Generics
        if (self.generic or self.genericTypes):
            hdl_code = hdl_code + vhdl.indent(indent_level+1) + ("generic  (\r\n")
            hdl_code = hdl_code + self.generic.code(indent_level+1)
            hdl_code = hdl_code + self.genericTypes.code(indent_level+1)
            hdl_code = hdl_code + vhdl.indent(indent_level+1) + ("--);\r\n")
            hdl_code = hdl_code + "\r\n"
        else:
            hdl_code = hdl_code + vhdl.indent(indent_level+1) + ("--generic  (\r\n")
            hdl_code = hdl_code + vhdl.indent(indent_level+2) + ("--Package Generics go here.\r\n")
            hdl_code = hdl_code + vhdl.indent(indent_level+1) + ("--);\r\n")
            hdl_code = hdl_code + "\r\n"

        hdl_code = hdl_code + self.declarationHeader.code()
        hdl_code = hdl_code + self.constant.code()
        hdl_code = hdl_code + self.customTypes.code()
        hdl_code = hdl_code + self.customTypes.codeConstant()
        hdl_code = hdl_code + self.signal.code()
        hdl_code = hdl_code + self.subPrograms.declaration()
        hdl_code = hdl_code + self.component.code()
        hdl_code = hdl_code + self.declarationFooter.code()
        hdl_code = hdl_code + vhdl.indent(0) + ("end %s;\r\n" % self.name)
        hdl_code = hdl_code + "\r\n"
        return hdl_code


class PackageBodyObj:
    def __init__(self, name):
        self.name = name
        self.subPrograms = ""
        self.bodyCodeHeader = vhdl.GenericCodeBlock(1)
        self.bodyCodeFooter = vhdl.GenericCodeBlock(1)

    def code(self, indent_level=0):
        hdl_code = ""
        hdl_code = vhdl.indent(indent_level) + ("package body %s is\r\n" % self.name)
        hdl_code = hdl_code + "\r\n"
        # Header
        if (self.bodyCodeHeader):
            hdl_code = hdl_code + self.bodyCodeHeader.code()
            hdl_code = hdl_code + "\r\n"
        # Functions
        hdl_code = hdl_code + vhdl.indent(indent_level+1) + ("-- Functions & Procedures\r\n")
        if (self.subPrograms):
            hdl_code = hdl_code + self.subPrograms.code()
            hdl_code = hdl_code + "\r\n"
        else:
            hdl_code = hdl_code + vhdl.indent(indent_level+2) + ("-- subprograms_declaration_tag\r\n")

        # Footer
        if (self.bodyCodeHeader):
            hdl_code = hdl_code + self.bodyCodeFooter.code()
            hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + vhdl.indent(indent_level) + ("end package body;\r\n")
        hdl_code = hdl_code + "\r\n"
        return hdl_code


class PkgVHDL:
    def __init__(self, name, version=None):
        self.name = name
        self.fileHeader = vhdl.GenericCodeBlock(0)
        self.fileHeader.add(vhdl.license_text)
        self.library = vhdl.LibraryList()
        self.declaration = PackageDeclarationObj(name)
        self.body = PackageBodyObj(name)
        if version is not None:
            self.declaration.constant.add("package_version_c", "String", "\"%s\"" % version)

    def write_file(self):
        hdl_code = self.code()

        if (not os.path.exists("output")):
            os.makedirs("output")

        output_file_name = "output/"+self.name+".vhd"
        # to do: check if file exists. If so, emit a warning and
        # check if must clear it.
        output_file = open(output_file_name, "w+")
        for line in hdl_code:
            output_file.write(line)

        output_file.close()
        return True

    def code(self):
        self.body.subPrograms = self.declaration.subPrograms
        hdl_code = ""
        hdl_code = hdl_code + self.fileHeader.code()
        hdl_code = hdl_code + self.library.code()
        hdl_code = hdl_code + self.declaration.code()
        hdl_code = hdl_code + self.body.code()
        return hdl_code
