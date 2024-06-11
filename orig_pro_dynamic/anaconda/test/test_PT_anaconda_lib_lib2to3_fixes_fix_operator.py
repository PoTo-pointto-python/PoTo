from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_operator import invocation
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_operator import FixOperator

def test_PT_invocation():
    invocation()

def test_PT_FixOperator_transform():
    f = FixOperator()
    f.transform()