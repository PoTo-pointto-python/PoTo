from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_exitfunc import FixExitfunc

def test_PT_FixExitfunc_transform():
    f = FixExitfunc()
    f.transform()

def test_PT_FixExitfunc_start_tree():
    f = FixExitfunc()
    f.start_tree()
