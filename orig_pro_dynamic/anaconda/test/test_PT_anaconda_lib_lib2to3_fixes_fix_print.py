from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_print import FixPrint

def test_PT_FixPrint_transform():
    f = FixPrint()
    f.transform()
    
def test_PT_FixPrint_add_kwarg():
    f = FixPrint()
    f.add_kwarg()