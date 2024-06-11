from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.token import ISTERMINAL
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.token import ISNONTERMINAL
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.token import ISEOF

def test_PT_ISTERMINAL():
    ISTERMINAL(1)

def test_PT_ISNONTERMINAL():
    ISNONTERMINAL(2)

def test_PT_ISEOF():
    ISEOF(3)