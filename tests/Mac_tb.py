import cocotb
from cocotb.runner import get_runner


class MacDataGenerator:
    def __init__(self):
        ...


class MacDriver:
    def __init__(self, dut):
        self.dut = dut


class MacMonitor:
    def __init__(self):
        ...


class MacScoreboard:
    def __init__(self):
        ...


class MacGoldenModel:
    def __init__(self):
        ...


class MacTest:
    def __init__(self, dut):
        self.dut = dut
        self.data_generator = MacDataGenerator()
        self.driver = MacDriver(dut)
        self.monitor = MacMonitor()
        self.scoreboard = MacScoreboard()
        self.golden_model = MacGoldenModel()


@cocotb.test()
async def test_mac_basic(dut):
    pass


def main():
    simulator = get_runner("icarus")
    simulator.build(
        sources=["../Mac.v"],
        hdl_toplevel="Mac",
        clean=True
    )
    simulator.test(
        hdl_toplevel="Mac",
        test_module="Mac_tb",
    )


if __name__ == "__main__":
    main()
