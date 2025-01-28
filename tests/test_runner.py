import os
import sys

from cocotb.runner import get_runner


def main(dut_name, sources):
    simulator = get_runner("icarus")
    simulator.build(
        sources=sources,
        hdl_toplevel=dut_name,
        clean=True,
        waves=True
    )
    simulator.test(
        hdl_toplevel=dut_name,
        test_module=dut_name + "_tb",
        waves=True
    )


if __name__ == "__main__":
    src_path = sys.argv[1]
    dut_name = sys.argv[2]
    sources = [os.path.join(src_path, sys.argv[i] + ".v")
               for i in range(2, len(sys.argv))]

    main(dut_name, sources)
