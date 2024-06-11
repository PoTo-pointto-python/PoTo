from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.literals import escape
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.literals import evalString
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.literals import test

def test_PT_escape():
    escape()

def test_PT_evalString():
    evalString("test_string")

def test_PT_test():
    test()