# -*- coding: utf-8 -*-
from os.path import join, dirname, abspath
import subprocess
from vunit.sim_if.ghdl import GHDLInterface
from vunit.sim_if.factory import SIMULATOR_FACTORY
from vunit import VUnit, VUnitCLI

##############################################################################
##############################################################################
##############################################################################

# VUnit instance.
ui = VUnit.from_argv()

# # Xilinx Vivado libraries.
# xilinx_libraries_path = "C:/users/tomaspcorrea/AppData/Local/ghdl/lib/xilinx-vivado"
# unisim_path = join(xilinx_libraries_path, "unisim", "v08")
# unifast_path = join(xilinx_libraries_path, "unifast", "v08")
# unimacro_path = join(xilinx_libraries_path, "unimacro", "v08")
# secureip_path = join(xilinx_libraries_path, "secureip", "v08")
# ui.add_external_library("unisim", unisim_path)
# ui.add_external_library("unimacro", unimacro_path)
# ui.add_external_library("secureip", secureip_path)

# UVVM libraries path.
uvvm_util_root = "C:/users/tomaspcorrea/AppData/Local/ghdl/lib/uvvm/uvvm_util/v08"
uvvm_axilite_root = "C:/users/tomaspcorrea/AppData/Local/ghdl/lib/uvvm/bitvis_vip_axilite/v08"

# Add UVVM libraries.
ui.add_external_library("uvvm_util", uvvm_util_root)
ui.add_external_library("bitvis_vip_axilite", uvvm_axilite_root)

# Add expert library.
expert_root = "C:/Lib/Compiled/expert"
ui.add_external_library("expert", expert_root)

##############################################################################
##############################################################################
##############################################################################

# Add module sources.
ssvectors_src_lib = ui.add_library("src_lib")
ssvectors_src_lib.add_source_files("TestBench/myregbank_pkg.vhd")
ssvectors_src_lib.add_source_files("TestBench/myregbank.vhd")

# Add tb sources.
ssvectors_tb_lib = ui.add_library("tb_lib")
ssvectors_tb_lib.add_source_files("TestBench/myregbank_tb.vhd")

##############################################################################
##############################################################################
##############################################################################

# GHDL parameters.
ssvectors_src_lib.add_compile_option(
    "ghdl.a_flags", ["-fexplicit", "--ieee=synopsys", "--no-vital-checks", "-frelaxed-rules"])
ssvectors_tb_lib.add_compile_option(
    "ghdl.a_flags", ["-fexplicit", "--ieee=synopsys", "--no-vital-checks", "-frelaxed-rules"])
ui.set_sim_option("ghdl.elab_flags", ["-fexplicit",
                                      "--ieee=synopsys", "--no-vital-checks", "-frelaxed-rules"])
ui.set_sim_option("modelsim.init_files.after_load", ["modelsim.do"])

# Run tests.
ui.main()
