from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_reduce import FixReduce

def test_PT_FixReduce_transform():
    f = FixReduce()
    f.transform()
