import dataclasses
import cocotb
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.runner import get_runner
from cocotb.triggers import RisingEdge


@dataclasses.dataclass
class MacTransaction:
    prior_C: int
    A: int
    B: int
    ena: int
    reset: int
    C: int


class MacDataGenerator:
    def __init__(self):
        ...


class MacDriver:
    def __init__(self, dut):
        self.dut = dut

    def drive(self, A: int, B: int):
        self.dut.A <= A
        self.dut.B <= B


class MacMonitor:
    def __init__(self, dut, queue: Queue[MacTransaction]):
        self.dut = dut
        self.queue = queue

    async def monitor(self):
        while True:
            prior_C = self.dut.C.value

            cocotb.log.info(f"Before RisingEdge Monitoring: A={self.dut.A.value}, B={self.dut.B.value}, C={
                            self.dut.C.value}, Ena={self.dut.ena.value}, Reset={self.dut.reset.value}")
            await RisingEdge(self.dut.clk)
            cocotb.log.info(f"After RisingEdge Monitoring: A={self.dut.A.value}, B={self.dut.B.value}, C={
                            self.dut.C.value}, Ena={self.dut.ena.value}, Reset={self.dut.reset.value}")

            transaction = MacTransaction(
                prior_C, self.dut.A.value, self.dut.B.value, self.dut.ena.value, self.dut.reset.value, self.dut.C.value)
            await self.queue.put(transaction)


class MacScoreboard:
    def __init__(self, queue: Queue[MacTransaction]):
        self.queue = queue
        self.golden_model = MacGoldenModel()

    async def score(self):
        while True:
            transaction = await self.queue.get()

            if not transaction.reset and transaction.ena:
                expected_C = self.golden_model.get_expected(transaction)

                assert expected_C == transaction.C, f"Actual: {
                    transaction.C}, Expected: {expected_C}"


class MacGoldenModel:
    def __init__(self):
        pass

    def get_expected(self, transaction: MacTransaction):
        cocotb.log.info(f"prior_C: {transaction.prior_C}")
        return transaction.prior_C + transaction.A * transaction.B


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
    queue = Queue()
    monitor = MacMonitor(dut, queue)
    scoreboard = MacScoreboard(queue)

    clock = Clock(dut.clk, 2, "sec")
    await cocotb.start(clock.start())

    await cocotb.start(monitor.monitor())
    await cocotb.start(scoreboard.score())

    dut.reset.value = 1
    await RisingEdge(dut.clk)

    dut.reset.value = 0
    dut.ena.value = 1
    dut.A.value = 2
    dut.B.value = 3

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    # Problem: The test bench does not wait until the coroutines inside of it are executed.
    # Instead it quits after the last line is interpreted it seems like


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
        # timescale=("1ns", "1ps")
    )


if __name__ == "__main__":
    main()
