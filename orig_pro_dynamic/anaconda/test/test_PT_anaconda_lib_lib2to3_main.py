from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.main import diff_texts
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.main import StdoutRefactoringTool
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.main import warn
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.main import main

def test_PT_diff_texts():
    a = "stringa"
    b = "stringb"
    fn = "testfilename"
    diff_texts(a,b,fn)

def test_PT_StdoutRefactoringTool_log_error():
    s = StdoutRefactoringTool()
    s.log_error("testmsg")

def test_PT_StdoutRefactoringTool_write_file():
    s = StdoutRefactoringTool()
    s.write_file("testtext","filename","oldtext",encoding)

def test_PT_StdoutRefactoringTool_print_output():
    s = StdoutRefactoringTool()
    s.print_output("oldtext","newtext","fname",True)

def test_PT_warn():
    warn("warn_text")

def test_PT_main():
    main()