from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_types import FixTypes

def test_PT_FixTypes_transform():
    f = FixTypes()
    f.transform()
