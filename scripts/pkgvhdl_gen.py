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
import sys
import os
import vhdl_gen as vhdl
import math


class PackageDeclarationObj:
    def __init__(self, name):
        self.name = name
        self.generic = vhdl.genericList()
        self.constant = vhdl.constantList()
        self.component = vhdl.componentList()
        self.signal = vhdl.signalList()
        self.functions = ""
        self.procedures = ""
        self.customTypes = vhdl.genericCodeBlock(1)
        self.declarationHeader = vhdl.genericCodeBlock(1)
        self.declarationFooter = vhdl.genericCodeBlock(1)

    def code(self):
        hdl_code = vhdl.indent(0) + ("entity %s is\r\n" % self.name)
        if (self.generic):
            hdl_code = hdl_code + vhdl.indent(1) + ("generic (\r\n")
            hdl_code = hdl_code + self.generic.code()
            hdl_code = hdl_code + vhdl.indent(1) + (");\r\n")
        else:
            hdl_code = hdl_code + vhdl.indent(1) + ("--generic (\r\n")
            hdl_code = hdl_code + vhdl.indent(2) + ("--generic_declaration_tag\r\n")
            hdl_code = hdl_code + vhdl.indent(1) + ("--);\r\n")

        hdl_code = hdl_code + self.declarationHeader.code()
        hdl_code = hdl_code + self.constant.code()
        hdl_code = hdl_code + self.customTypes.code()
        hdl_code = hdl_code + self.signal.code()
        #hdl_code = hdl_code + self.functions.declaration()
        #hdl_code = hdl_code + self.procedures.declaration()
        hdl_code = hdl_code + self.component.code()
        hdl_code = hdl_code + self.declarationFooter.code()
        hdl_code = hdl_code + vhdl.indent(0) + ("end %s;\r\n" % self.name)
        hdl_code = hdl_code + "\r\n"
        return hdl_code


class PackageBodyObj:
    def __init__(self, name):
        self.name = name
        self.functions = ""
        self.procedures = ""
        self.bodyCodeHeader = vhdl.genericCodeBlock(1)
        self.bodyCodeFooter = vhdl.genericCodeBlock(1)

    def code(self):
        hdl_code = ""
        hdl_code = vhdl.indent(0) + ("package body of %s is\r\n" % self.name)
        hdl_code = hdl_code + "\r\n"
        if (self.bodyCodeHeader):
            hdl_code = hdl_code + self.bodyCodeHeader.code()
            hdl_code = hdl_code + "\r\n"
        if (self.functions):
            #hdl_code = hdl_code + self.functions.code()
            hdl_code = hdl_code + "\r\n"
        if (self.procedures):
            #hdl_code = hdl_code + self.procedures.code()
            hdl_code = hdl_code + "\r\n"
        if (self.bodyCodeHeader):
            hdl_code = hdl_code + self.bodyCodeFooter.code()
            hdl_code = hdl_code + "\r\n"
        hdl_code = hdl_code + vhdl.indent(0) + ("end package body;\r\n")
        hdl_code = hdl_code + "\r\n"
        return hdl_code


class PkgVHDL:
    def __init__(self, name):
        self.library = vhdl.libraryList()
        self.packageDeclaration = PackageDeclarationObj(name)
        self.packageBody = PackageBodyObj(name)

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
        hdl_code = hdl_code + self.packageDeclaration.code()
        hdl_code = hdl_code + self.packageBody.code()
        return hdl_code
