from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_except import find_excepts
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_except import FixExcept

def test_PT_find_excepts():
    find_excepts()

def test_PT_FixExcept_transform():
    f = FixExcept()
    f.transform()
