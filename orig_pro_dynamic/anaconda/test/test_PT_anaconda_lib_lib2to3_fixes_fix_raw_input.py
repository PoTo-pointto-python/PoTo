from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_raw_input import FixRawInput

def test_PT_FixRawInput_transform():
    f = FixRawInput()
    f.transform()
