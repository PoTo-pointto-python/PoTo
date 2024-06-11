from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_itertools import FixItertools

def test_PT_FixItertools_transform():
    f = FixItertools()
    f.transform()