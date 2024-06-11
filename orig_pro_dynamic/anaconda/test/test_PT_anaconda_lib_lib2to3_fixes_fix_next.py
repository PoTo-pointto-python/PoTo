from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_next import FixNext
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_next import is_assign_target
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_next import find_assign
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_next import is_subtree

def test_PT_FixNext_start_tree():
    f = FixNext()
    f.start_tree()

def test_PT_FixNext_transform():
    f = FixNext()
    f.transform()

def test_PT_is_assign_target():
    is_assign_target()

def test_PT_find_assign():
    find_assign()

def test_PT_is_subtree():
    is_subtree()