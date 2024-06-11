from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.btm_matcher import BottomMatcher
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.btm_matcher import type_repr

def test_PT_BottomMatcher_add_fixer():
    b = BottomMatcher()
    b.add_fixer()

def test_PT_BottomMatcher_add():
    b = BottomMatcher()
    b.add()

def test_PT_BottomMatcher_run():
    b = BottomMatcher()
    b.run()

def test_PT_BottomMatcher_print_ac():
    b = BottomMatcher()
    b.print_ac()

def test_PT_type_repr():
    type_repr()