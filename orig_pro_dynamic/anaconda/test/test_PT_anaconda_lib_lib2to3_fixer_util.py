from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import KeywordArg
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import LParen
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import RParen
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import Assign
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import Name
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import Attr
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import Comma
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import Dot
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import ArgList
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import Call
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import Newline
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import BlankLine
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import Number
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import Subscript
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import String
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import ListComp
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import FromImport
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import is_tuple
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import is_list
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import parenthesize
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import attr_chain
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import in_special_context
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import is_probably_builtin
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import find_indentation
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import make_suite
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import find_root
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import does_tree_import
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import is_import
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import touch_import
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_util import find_binding


def test_PT_KeywordArg():
    KeywordArg()

def test_PT_LParen():
    LParen()

def test_PT_RParen():
    RParen()

def test_PT_Assign():
    Assign()

def test_PT_Name():
    Name()

def test_PT_Attr():
    Attr()

def test_PT_Comma():
    Comma()

def test_PT_Dot():
    Dot()

def test_PT_ArgList():
    ArgList()

def test_PT_Call():
    Call()

def test_PT_Newline():
    Newline()

def test_PT_BlankLine():
    BlankLine()

def test_PT_Number():
    Number()

def test_PT_Subscript():
    Subscript()

def test_PT_String():
    String()

def test_PT_ListComp():
    ListComp()

def test_PT_FromImport():
    FromImport()

def test_PT_is_tuple():
    is_tuple()

def test_PT_is_list():
    is_list()

def test_PT_parenthesize():
    parenthesize()

def test_PT_attr_chain():
    attr_chain()

def test_PT_in_special_context():
    in_special_context()

def test_PT_is_probably_builtin():
    is_probably_builtin()

def test_PT_find_indentation():
    find_indentation()

def test_PT_make_suite():
    make_suite()

def test_PT_find_root():
    find_root()

def test_PT_does_tree_import():
    does_tree_import()

def test_PT_is_import():
    is_import()

def test_PT_touch_import():
    touch_import()

def test_PT_find_binding():
    find_binding()
