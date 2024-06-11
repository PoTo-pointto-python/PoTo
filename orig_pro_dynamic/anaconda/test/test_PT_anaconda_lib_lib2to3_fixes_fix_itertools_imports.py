from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_itertools_imports import FixItertoolsImports

def test_PT_FixItertoolsImports_transform():
    f = FixItertoolsImports()
    f.transform()