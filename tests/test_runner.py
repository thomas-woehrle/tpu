import os
import sys

from cocotb.runner import get_runner


def main(dut_name: str, sources: list[str], parameters: dict[str, int]):
    simulator = get_runner("icarus")
    simulator.build(
        sources=sources,
        hdl_toplevel=dut_name,
        clean=True,
        waves=True,
        parameters=parameters
    )
    simulator.test(
        hdl_toplevel=dut_name,
        test_module=dut_name + "_tb",
        waves=True,
        parameters=parameters
    )


dependencies = {
    "Mac": [],
    "MacManager": ["Mac"],
    "SystolicMatrixMultiplier": ["Mac", "MacManager"]
}

if __name__ == "__main__":
    src_path = sys.argv[1]
    dut_name = sys.argv[2]

    sources = [dut_name] + dependencies[dut_name]
    sources = [os.path.join(src_path, s + ".v") for s in sources]

    parameters = dict()
    for i in range(3, len(sys.argv)):
        arg = sys.argv[i]
        k, v = arg.split("=")[0], arg.split("=")[1]
        # v has to be an int
        parameters[k] = int(v)
        os.environ["DUT_" + k] = v

    main(dut_name, sources, parameters)
