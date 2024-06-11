from anaconda.anaconda_lib._typing import NamedTuple
from anaconda.anaconda_lib._typing import IO
from anaconda.anaconda_lib._typing import BinaryIO

def test_PT_NamedTuple():
    NamedTuple('Employee', [('name', str), 'id', int])

def test_PT_io_read():
    io = IO()
    s = io.read()

def test_PT_io_readline():
    io = IO()
    s = io.readline()

def test_PT_io_readlines():
    io = IO()
    s = io.readlines()

def test_PT_io_truncate():
    io = IO()
    s = io.truncate()

def test_PT_io_write():
    io = IO()
    s = io.write()

def test_PT_io_writelines():
    io = IO()
    s = io.writelines()

def test_PT_bio_write():
    io = BinaryIO()
    s = io.write()