from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.tokenize import group
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.tokenize import any
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.tokenize import maybe
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.tokenize import printtoken
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.tokenize import tokenize
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.tokenize import tokenize_loop
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.tokenize import Untokenizer
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.tokenize import detect_encoding
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.tokenize import untokenize
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pgen2.tokenize import generate_tokens

def test_PT_group():
    group()
    
def test_PT_any():
    any()
    
def test_PT_maybe():
    maybe()
    
def test_PT_printtoken():
    printtoken()
    
def test_PT_tokenize():
    tokenize()
    
def test_PT_tokenize_loop():
    tokenize_loop()
    
def test_PT_Untokenizer_add_whitespace():
    u = Untokenizer()
    u.add_whitespace()
    
def test_PT_Untokenizer_untokenize():
    u = Untokenizer()
    u.untokenize()
    
def test_PT_Untokenizer_compat():
    u = Untokenizer()
    u.compat()
    
def test_PT_detect_encoding():
    detect_encoding()
    
def test_PT_untokenize():
    untokenize()
    
def test_PT_generate_tokens():
    generate_tokens()