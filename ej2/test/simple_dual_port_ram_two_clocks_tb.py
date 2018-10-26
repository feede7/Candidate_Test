import cocotb
import random

from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, ReadOnly
from cocotb.result import TestFailure, TestError, ReturnValue, SimFailure
from cocotb.binary import BinaryValue

from cocotb.utils import get_sim_time

CLK_PERIOD_A = 2
CLK_PERIOD_B = 4


@cocotb.test()
def simple_test(dut):
    """
        Simple test: it writes 2 values and reads them back.
    """

    dut._log.info('Init Clocks')
    cocotb.fork(Clock(dut.CLKA, CLK_PERIOD_A, units='ns').start())
    cocotb.fork(Clock(dut.CLKB, CLK_PERIOD_B, units='ns').start())

    dut._log.info('Setup the initial state of signals')
    dut.ENA <= 1 # Always enable
    dut.ENB <= 1 # Always enable
    dut.WEA <= 0

    dut.ADDRA <= 0
    dut.ADDRB <= 0

    dut.DIA <= 0
    dut.DOB <= 0

    yield RisingEdge(dut.CLKA)
    yield RisingEdge(dut.CLKA)

    dut._log.info('Write value 0x0F10A in address 0x00100')
    dut.WEA <= 1
    dut.ADDRA <= 0x00100
    dut.DIA <= 0x0F10A
    yield RisingEdge(dut.CLKA)
    dut.WEA <= 0
    dut.ADDRB <= 0x00100
    yield ReadOnly()

    dut._log.info('Read value in address 0x00100')

    # It's a synch read memory, so you need 2 cycles to read the real data

    yield RisingEdge(dut.CLKB)
    yield RisingEdge(dut.CLKB)

    if (dut.DOB.value.integer != dut.DIA.value.integer):
        raise TestFailure(
            "Data read in address 0x00100 is not correct")
