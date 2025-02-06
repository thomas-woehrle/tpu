"""Defines the basic structure and interface of tests.

Based on UVM.

Contains: 
    * TestBase
"""
from abc import ABC, abstractmethod

import cocotb
from cocotb.queue import Queue
from cocotb.triggers import FallingEdge, RisingEdge


class TestBase[ParametersT, DutSnapshotT, InputT](ABC):
    """Abstract class defining the structure of tests

    Intended to be subclassed per DUT, implementing the abstract methods and 
    potentially overriding the non-abstract ones.
    """

    def __init__(self, dut, params: ParametersT, n_checks: int):
        """
        Args:
            dut: DUT, received from cocotb
            params: Parameters used during the build process
            n_checks: The number of times generate_input is called
        """
        self.dut = dut
        self.params = params
        cocotb.log.info(self.params)
        self.n_checks = n_checks
        self.transaction_queue = Queue[tuple[DutSnapshotT, DutSnapshotT]](
        )
        self.input_queue = Queue[InputT]()

    @abstractmethod
    def get_dut_snapshot(self) -> DutSnapshotT:
        """Creates a Snapshot of the current state of the DUT

        Returns:
            Object representing the Snapshot
        """

    @abstractmethod
    async def wait_between_snapshots(self, first_snapshot: DutSnapshotT):
        """Specifies what should be done after receiving the first snapshot

        Is repeatedly called from start_monitor(), after the first snapshot 
        is received.

        Args:
            first_snapshot: The first snapshot of the current transaction, 
                received in start_monitor
        """

    @abstractmethod
    async def score_transaction(self, t: tuple[DutSnapshotT, DutSnapshotT]):
        """Scores a given transaction, acting as a golden model

        Repeatedly called from start_scoreboard

        Args:
            t: The transaction to score
        """

    @abstractmethod
    async def generate_input(self, i: int) -> InputT:
        """Generates an input

        Repeatedly called from start_input_generator.
        The inputs it returns are driven on the DUT in FIFO fashion.

        Args:
            i: The current repetition, starting at 0.
                Can have an influence on what should be generated, fe reset or not.

        Returns:
            The next input
        """

    @abstractmethod
    async def drive_input(self, next_input: InputT):
        """Method to drive a given input on the DUT

        This is called after waiting for a FallingEdge. It will be called
        again at the next FallingEdge, after it finished running. 
        Therefore, it should include logic to wait the appropriate 
        amount of time until it should be called again.

        Args:
            next_input: The next_input to drive, usually without waiting before
        """

    async def start_monitor(self):
        """Starts the monitor

        Awaits a RisingEdge first, then repeatedly:
        - gets a snapshot
        - calls wait_between_snapshots
        - gets another snapshot
        - puts the resulting transaction in the transaction_queue
        """
        await RisingEdge(self.dut.clk)
        while True:
            snapshot_0 = self.get_dut_snapshot()

            await self.wait_between_snapshots(snapshot_0)

            snapshot_1 = self.get_dut_snapshot()

            # put transaction in queue
            t = (snapshot_0, snapshot_1)
            await self.transaction_queue.put(t)

    async def start_scoreboard(self):
        """Starts the scoreboard

        Repeatedly:
        - gets transactions from the transaction_queue
        - lets these transactions be scored by score_transaction
        """
        while True:
            t = await self.transaction_queue.get()
            await self.score_transaction(t)

    async def start_input_generator(self):
        """Starts the input generator

        Repeatedly:
        - calls generate_input
        - places this input in the input_queue
        """
        for i in range(self.n_checks):
            next_input = await self.generate_input(i)
            await self.input_queue.put(next_input)

    async def start_input_driver(self):
        """Starts the input driver

        Repeatedly:
        - waits for FallingEdge
        - gets input from input_queue
        - calls drive_input with that input. drive_input will potentially 
            wait again on something
        """
        while True:
            await FallingEdge(self.dut.clk)
            next_input = await self.input_queue.get()
            await self.drive_input(next_input)

    def start_soon(self):
        """Invokes cocotb.start_soon on the different components
        """
        cocotb.start_soon(self.start_input_generator())
        cocotb.start_soon(self.start_input_driver())
        cocotb.start_soon(self.start_scoreboard())
        cocotb.start_soon(self.start_monitor())
