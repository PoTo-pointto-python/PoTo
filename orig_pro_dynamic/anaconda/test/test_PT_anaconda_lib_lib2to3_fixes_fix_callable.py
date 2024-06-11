from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_callable import FixCallable

def test_PT_FixCallable_transform():
    f = FixCallable()
    f.transform()
