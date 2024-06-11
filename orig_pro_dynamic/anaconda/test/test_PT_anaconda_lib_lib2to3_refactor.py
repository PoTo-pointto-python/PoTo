from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.refactor import get_all_fix_names
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.refactor import get_fixers_from_package
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.refactor import RefactoringTool
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.refactor import MultiprocessRefactoringTool
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.refactor import xxx
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.refactor import xxx

def test_PT_get_all_fix_names():
    get_all_fix_names()

def test_PT_get_fixers_from_package():
    get_fixers_from_package("pkg_name")

def test_PT_RefactoringTool_get_fixers():
    r = RefactoringTool()
    r.get_fixers()

def test_PT_RefactoringTool_log_error():
    r = RefactoringTool()
    r.log_error("test_msg")

def test_PT_RefactoringTool_log_message():
    r = RefactoringTool()
    r.log_message("test_msg")

def test_PT_RefactoringTool_log_debug():
    r = RefactoringTool()
    r.log_debug("test_msg")

def test_PT_RefactoringTool_print_output():
    r = RefactoringTool()
    r.print_output("old_text","new_text","f_name",False)

def test_PT_RefactoringTool_refactor():
    r = RefactoringTool()
    r.refactor()

def test_PT_RefactoringTool_refactor_dir():
    r = RefactoringTool()
    r.refactor_dir("dir_name")

def test_PT_RefactoringTool_refactor_file():
    r = RefactoringTool()
    r.refactor_file("f_name")

def test_PT_RefactoringTool_refactor_string():
    r = RefactoringTool()
    r.refactor_string("data_strign", "test_name")

def test_PT_RefactoringTool_refactor_stdin():
    r = RefactoringTool()
    r.refactor_stdin()

def test_PT_RefactoringTool_refactor_tree():
    r = RefactoringTool()
    r.refactor_tree(tree,"name")

def test_PT_RefactoringTool_traverse_by():
    r = RefactoringTool()
    r.traverse_by()

def test_PT_RefactoringTool_processed_file():
    r = RefactoringTool()
    r.processed_file("new_text", "f_name")

def test_PT_RefactoringTool_write_file():
    r = RefactoringTool()
    r.write_file("new_text","f_name","old_text")

def test_PT_RefactoringTool_refactor_docstring():
    r = RefactoringTool()
    r.refactor_docstring("input_string","f_name")

def test_PT_RefactoringTool_refactor_doctest():
    r = RefactoringTool()
    r.refactor_doctest(block,1,indent,"f_name")

def test_PT_RefactoringTool_summarize():
    r = RefactoringTool()
    r.summarize()

def test_PT_RefactoringTool_parse_block():
    r = RefactoringTool()
    r.parse_block(block,1,indent)

def test_PT_RefactoringTool_wrap_toks():
    r = RefactoringTool()
    r.wrap_toks(block,1,indent)

def test_PT_RefactoringTool_gen_lines():
    r = RefactoringTool()
    r.gen_lines()

def test_PT_MultiprocessRefactoringTool_refactor():
    m = MultiprocessRefactoringTool()
    m.refactor()

def test_PT_MultiprocessRefactoringTool_refactor_file():
    m = MultiprocessRefactoringTool()
    m.refactor_file()
