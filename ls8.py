#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()

cpu.load()
cpu.run()

# run in terminal `python ls8.py examples/print8.ls8`
# sys.argv[1] --> examples/print8.ls8 === filename
# open the filename which can be any file we pass as second arg when I run ls8.py
