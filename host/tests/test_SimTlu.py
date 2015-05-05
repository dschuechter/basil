#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# SiLab, Institute of Physics, University of Bonn
# ------------------------------------------------------------
#

import unittest
from time import time
from basil.dut import Dut
from basil.utils.sim.utils import cocotb_compile_and_run, cocotb_compile_clean

cnfg_yaml = """
transfer_layer:
  - name  : intf
    type  : SiSim
    init:
        host : localhost
        port  : 12345

hw_drivers:
  - name      : gpio
    type      : gpio
    interface : intf
    base_addr : 0x0000
    size      : 8

  - name      : tlu
    type      : tlu
    interface : intf
    base_addr : 0x8200

  - name      : sram
    type      : sram_fifo
    interface : intf
    base_addr : 0x8100
    base_data_addr : 0x80000000

registers:
  - name        : CONTROL
    type        : StdRegister
    hw_driver   : gpio
    size        : 8
    fields:
      - name    : ENABLE
        size    : 1
        offset  : 0
"""


class TestSimTlu(unittest.TestCase):
    def setUp(self):
        cocotb_compile_and_run(['test_SimTlu.v'])

        self.chip = Dut(cnfg_yaml)
        self.chip.init()

    def test_version(self):
        self.chip['tlu'].TRIGGER_MODE = 3
        self.chip['CONTROL']['ENABLE'] = 1

        start = time()
        while(self.chip['sram'].get_fifo_int_size() < 4):
            if time() - start > 1:
                break

        self.chip['CONTROL']['ENABLE'] = 0

        self.assertGreaterEqual(self.chip['sram'].get_fifo_int_size(), 4)

        data = self.chip['sram'].get_data()[:4]
        self.assertEqual(data[0], 0x80000000)
        self.assertEqual(data[1], 0x80000001)
        self.assertEqual(data[2], 0x80000002)
        self.assertEqual(data[3], 0x80000003)

    def tearDown(self):
        self.chip.close()  # let it close connection and stop simulator
        cocotb_compile_clean()

if __name__ == '__main__':
    unittest.main()
