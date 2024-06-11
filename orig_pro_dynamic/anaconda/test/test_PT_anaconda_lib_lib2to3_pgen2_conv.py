from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.conv import Converter

def test_PT_Converter_run():
    c = Converter()
    c.run()

def test_PT_Converter_parse_graminit_h():
    c = Converter()
    c.parse_graminit_h("fname")

def test_PT_Converter_parse_graminit_c():
    c = Converter()
    c.parse_graminit_c("fname")

def test_PT_Converter_finish_off():
    c = Converter()
    c.finish_off()
