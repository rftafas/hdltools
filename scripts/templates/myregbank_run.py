from os.path import join, dirname
import sys

try:
    from vunit import VUnit
except:
    print("Please, intall vunit_hdl with 'pip install vunit_hdl'")
    print("Also, make sure to have either GHDL or Modelsim installed.")
    exit()


root = dirname(__file__)

vu = VUnit.from_argv()

expert = vu.add_library("expert")
expert.add_source_files(join(root, "../../../stdexpert/src/*.vhd"))

lib = vu.add_library("stdblocks")
lib.add_source_files(join(root, "../../../stdblocks/sync_lib/*.vhd"))
lib.add_source_files(join(root, "../../../stdblocks/ram_lib/*.vhd"))
lib.add_source_files(join(root, "../../../stdblocks/fifo_lib/*.vhd"))
lib.add_source_files(join(root, "./*.vhd"))
test_tb = lib.entity("myregbank_tb")
test_tb.scan_tests_from_file(join(root, "myregbank_tb.vhd"))

test_tb.add_config(
    name="run_time",
    generics=dict(run_time=100)
)

vu.main()
