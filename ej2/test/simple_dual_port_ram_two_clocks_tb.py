import cocotb
from random import randint
import math

from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, ReadOnly
from cocotb.result import TestFailure, TestError, ReturnValue, SimFailure
from cocotb.binary import BinaryValue

from cocotb.utils import get_sim_time

CLK_PERIOD_A = 2
CLK_PERIOD_B = 4

DATA_SIZE = 64
MEM_SIZE = 1024

@cocotb.coroutine
def read_ram(dut, address):
    dut.ADDRB <= address
    yield ReadOnly()
    yield RisingEdge(dut.CLKB)
    yield RisingEdge(dut.CLKB)
    raise ReturnValue(int(dut.DOB.value))

@cocotb.coroutine
def write_ram(dut, address, value):
    dut.WEA <= 0
    yield RisingEdge(dut.CLKA)
    yield RisingEdge(dut.CLKA)
    dut.WEA <= 1
    dut.ADDRA <= BinaryValue(value=address, bits=int(math.ceil(math.log(MEM_SIZE,2))), bigEndian=False)
    dut.DIA <= BinaryValue(value=value, bits=DATA_SIZE, bigEndian=False)
    dut._log.info('Write value {} in address {}'.format(hex(value),hex(address)))
    yield RisingEdge(dut.CLKA)
    dut.WEA <= 0

@cocotb.test()
def write_read_test(dut):
    """
        Write-Read test: it writes random values in whole memory, and reads them back to evaluate equality.
    """

    dut._log.info('Init Clocks')
    cocotb.fork(Clock(dut.CLKA, CLK_PERIOD_A, units='ns').start())
    cocotb.fork(Clock(dut.CLKB, CLK_PERIOD_B, units='ns').start())
    dut._log.info('Setup the initial state of signals')
    dut.ENA <= 1
    dut.ENB <= 1
    dut.WEA <= 0
    dut.ADDRA <= 0
    dut.ADDRB <= 0
    dut.DIA <= 0
    dut.DOB <= 0

    to_be_write = [i for i in range(MEM_SIZE)]
    iter=0
    for addr in to_be_write:
	    iter+=1
	    write_value = randint(0,pow(2,DATA_SIZE)-1)

	    yield write_ram(dut, addr, write_value)

	    read_value = yield read_ram(dut, BinaryValue(value=addr, bits=int(math.ceil(math.log(MEM_SIZE,2))), bigEndian=False))

	    if (read_value != write_value):
	        raise TestFailure(
	            "Data read in address {} is not correct".format(hex(addr)))
	    else:
	        dut._log.info('Iter {}/{} in address {} OK'.format(iter,len(to_be_write),hex(addr)))

@cocotb.test()
def write_adress_test(dut):
    """
        Write test: it writes a random writing address in writing address, and reads it back to evaluate equality.
    """

    dut._log.info('Init Clocks')
    cocotb.fork(Clock(dut.CLKA, CLK_PERIOD_A, units='ns').start())
    cocotb.fork(Clock(dut.CLKB, CLK_PERIOD_B, units='ns').start())
    dut._log.info('Setup the initial state of signals')
    dut.ENA <= 1
    dut.ENB <= 1
    dut.WEA <= 0
    dut.ADDRA <= 0
    dut.ADDRB <= 0
    dut.DIA <= 0
    dut.DOB <= 0

    to_be_write = [i for i in range(MEM_SIZE)]
    for addr in to_be_write:
	    write_value = addr
	    yield write_ram(dut, addr, write_value)
	    read_value = yield read_ram(dut, BinaryValue(value=addr, bits=int(math.log(MEM_SIZE,2)), bigEndian=False))

	    if (read_value != write_value):
	        raise TestFailure(
	            "Writing address read {} is not equal at previously setted {} ".format(hex(read_value),hex(write_value)))

@cocotb.test()
def read_test(dut):
    """
        Read test: it writes a fix value in whole memory, and reads it back to evaluate equality.
    """

    dut._log.info('Init Clocks')
    cocotb.fork(Clock(dut.CLKA, CLK_PERIOD_A, units='ns').start())
    cocotb.fork(Clock(dut.CLKB, CLK_PERIOD_B, units='ns').start())
    dut._log.info('Setup the initial state of signals')
    dut.ENA <= 1
    dut.ENB <= 1
    dut.WEA <= 0
    dut.ADDRA <= 0
    dut.ADDRB <= 0
    dut.DIA <= 0
    dut.DOB <= 0

    to_be_write = [i for i in range(MEM_SIZE)]
    iter=0
    write_value = randint(0,pow(2,DATA_SIZE)-1)

    for addr in to_be_write:
	    iter+=1

	    yield write_ram(dut, addr, write_value)

	    read_value = yield read_ram(dut, BinaryValue(value=addr, bits=int(math.log(MEM_SIZE,2)), bigEndian=False))

	    if (read_value != write_value):
	        raise TestFailure(
	            "Data read in address {} is not correct".format(hex(addr)))
	    else:
	        dut._log.info('Iter {}/{} in address {} OK'.format(iter,len(to_be_write),hex(addr)))
