from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.driver import Driver
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.driver import load_grammar
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.driver import main

def test_PT_Driver_parse_tokens():
    d = Driver()
    d.parse_tokens()

def test_PT_Driver_parse_stream_raw():
    d = Driver()
    d.parse_stream_raw()

def test_PT_Driver_parse_stream():
    d = Driver()
    d.parse_stream()

def test_PT_Driver_parse_file():
    d = Driver()
    d.parse_file("filename")

def test_PT_Driver_parse_string():
    d = Driver()
    d.parse_string("testtext")

def test_PT_load_grammar():
    load_grammar()

def test_PT_main():
    main()