"""Contains functionality to run cocotb tests from the command line
"""
import os
import sys

from cocotb.runner import get_runner


def main(dut_name: str, sources: list[str], parameters: dict[str, int]):
    """Main function to trigger execution of a test

    Args:
        dut_name: The name of the DUT
        sources: The paths to the files that are need to build, 
            including the DUT itself. Fe src/dut.v
        parameters: Dict representing build parameters
    """
    simulator = get_runner("icarus")
    simulator.build(
        sources=sources,
        hdl_toplevel=dut_name,
        clean=True,
        waves=True,
        parameters=parameters,
        timescale=("10ns", "100ps")
    )
    simulator.test(
        hdl_toplevel=dut_name,
        test_module=dut_name + "_tb",
        waves=True,
        parameters=parameters,
        timescale=("10ns", "100ps")
    )


# dependencies of the different modules
# should be handled differently if the number of modules increases
# fe with separate dependencies file
dependencies = {
    "Mac": [],
    "MacManager": ["Mac"],
    "SystolicMatrixMultiplier": ["Mac", "MacManager"]
}

if __name__ == "__main__":
    # read from command line
    src_path = sys.argv[1]
    dut_name = sys.argv[2]

    # create source paths
    sources = [dut_name] + dependencies[dut_name]
    sources = [os.path.join(src_path, s + ".v") for s in sources]

    # read parameters from command line and write them to the environment
    # so that they are accessible inside the <module_name>_tb.py files
    parameters = dict()
    for i in range(3, len(sys.argv)):
        arg = sys.argv[i]
        k, v = arg.split("=")[0], arg.split("=")[1]

        # v has to be an int at the moment
        parameters[k] = int(v)

        # the DUT_ prefix is used to find the variables in the test code
        os.environ["DUT_" + k] = v

    main(dut_name, sources, parameters)
