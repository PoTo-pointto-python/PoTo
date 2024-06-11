from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_input import FixInput

def test_PT_FixInput_transform():
    f = FixInput()
    f.transform()