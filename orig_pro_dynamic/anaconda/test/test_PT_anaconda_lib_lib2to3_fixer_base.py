from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_base import BaseFix
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixer_base import ConditionalFix

def test_PT_BaseFix_compile_pattern():
    b = BaseFix()
    b.compile_pattern()

def test_PT_BaseFix_set_filename():
    b = BaseFix()
    b.set_filename()

def test_PT_BaseFix_match():
    b = BaseFix()
    b.match()

def test_PT_BaseFix_transform():
    b = BaseFix()
    b.transform()

def test_PT_BaseFix_new_name():
    b = BaseFix()
    b.new_name()

def test_PT_BaseFix_log_message():
    b = BaseFix()
    b.log_message()

def test_PT_BaseFix_cannot_convert():
    b = BaseFix()
    b.cannot_convert()

def test_PT_BaseFix_warning():
    b = BaseFix()
    b.warning()

def test_PT_BaseFix_start_tree():
    b = BaseFix()
    b.start_tree()

def test_PT_BaseFix_finish_tree():
    b = BaseFix()
    b.finish_tree()

def test_PT_ConditionalFix_start_tree():
    c = ConditionalFix()
    c.start_tree()

def test_PT_ConditionalFix_should_skip():
    c = ConditionalFix()
    c.should_skip()