from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_raise import FixRaise

def test_PT_FixRaise_transform():
    f = FixRaise()
    f.transform()
