from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import open_with_encoding
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import detect_encoding
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import readlines_from_file
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import extended_blank_lines
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import continued_indentation
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import FixPEP8
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import get_index_offset_contents
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import get_fixed_long_line
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import longest_line_length
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import join_logical_line
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import untokenize_without_newlines
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import get_item
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import code_almost_equal
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import split_and_strip_non_empty_lines
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import fix_e265
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import refactor
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import code_to_2to3
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import fix_2to3
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import fix_w602
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import find_newline
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import get_diff_text
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import shorten_line
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import ReformattedLines
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import Atom
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import Container
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import Tuple
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import List
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import DictOrSet
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import ListComprehension
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import normalize_multiline
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import fix_whitespace
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import Reindenter
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import refactor_with_2to3
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import check_syntax
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import filter_results
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import multiline_string_lines
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import commented_out_code_lines
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import shorten_comment
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import normalize_line_endings
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import mutual_startswith
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import code_match
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import fix_code
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import fix_lines
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import fix_file
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import global_fixes
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import apply_global_fixes
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import extract_code_from_function    
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import create_parser    
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import parse_args    
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import read_config    
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import decode_filename    
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import supported_fixes    
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import docstring_summary    
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import line_shortening_rank    
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import standard_deviation    
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import has_arithmetic_operator 
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import count_unbalanced_brackets 
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import split_at_offsets 
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import LineEndingWrapper 
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import match_file 
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import find_files   
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import fix_multiple_files   
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import is_python_file   
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import is_probably_part_of_multiline   
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import wrap_output   
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import get_encoding   
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import main 
from anaconda.anaconda_lib.autopep.autopep8_lib.autopep8 import CachedTokenizer   

def test_PT_open_with_encoding():
    open_with_encoding("fname.txt")

def test_PT_detect_encoding():
    detect_encoding("fname.txt")

def test_PT_readlines_from_file():
    readlines_from_file("fname.txt")

def test_PT_extended_blank_lines():
    logical_line = "testline"
    previous_logical = "ptestline"
    extended_blank_lines(logical_line,a,b,c,previous_logical)

def test_PT_continued_indentation():
    ll = "testline"
    indent_level = 1
    indent_char = "\t"
    noqa = True
    continued_indentation(ll,tokens,indent_level,indent_char,noqa)

def test_PT_FixPEP8_fix():
    fp = FixPEP8()
    fp.fix()

def test_PT_FixPEP8_fix_e112():
    fp = FixPEP8()
    fp.fix_e112()

def test_PT_FixPEP8_fix_e113():
    fp = FixPEP8()
    fp.fix_e113()

def test_PT_FixPEP8_fix_e125():
    fp = FixPEP8()
    fp.fix_e125()

def test_PT_FixPEP8_fix_e131():
    fp = FixPEP8()
    fp.fix_e131()

def test_PT_FixPEP8_fix_e201():
    fp = FixPEP8()
    fp.fix_e201()

def test_PT_FixPEP8_fix_e224():
    fp = FixPEP8()
    fp.fix_e224()

def test_PT_FixPEP8_fix_e225():
    fp = FixPEP8()
    fp.fix_e225()

def test_PT_FixPEP8_fix_e231():
    fp = FixPEP8()
    fp.fix_e231()

def test_PT_FixPEP8_fix_e251():
    fp = FixPEP8()
    fp.fix_e251()

def test_PT_FixPEP8_fix_e262():
    fp = FixPEP8()
    fp.fix_e262()

def test_PT_FixPEP8_fix_e271():
    fp = FixPEP8()
    fp.fix_e271()

def test_PT_FixPEP8_fix_e301():
    fp = FixPEP8()
    fp.fix_e301()

def test_PT_FixPEP8_fix_e302():
    fp = FixPEP8()
    fp.fix_e302()

def test_PT_FixPEP8_fix_e303():
    fp = FixPEP8()
    fp.fix_e303()

def test_PT_FixPEP8_fix_e304():
    fp = FixPEP8()
    fp.fix_e304()

def test_PT_FixPEP8_fix_e305():
    fp = FixPEP8()
    fp.fix_e305()

def test_PT_FixPEP8_fix_e401():
    fp = FixPEP8()
    fp.fix_e401()

def test_PT_FixPEP8_fix_long_line_logically():
    fp = FixPEP8()
    fp.fix_long_line_logically()

def test_PT_FixPEP8_fix_long_line_physically():
    fp = FixPEP8()
    fp.fix_long_line_physically()

def test_PT_FixPEP8_fix_long_line():
    fp = FixPEP8()
    fp.fix_long_line()

def test_PT_FixPEP8_fix_e502():
    fp = FixPEP8()
    fp.fix_e502()

def test_PT_FixPEP8_fix_e701():
    fp = FixPEP8()
    fp.fix_e701()

def test_PT_FixPEP8_fix_e702():
    fp = FixPEP8()
    fp.fix_e702()

def test_PT_FixPEP8_fix_e704():
    fp = FixPEP8()
    fp.fix_e704()

def test_PT_FixPEP8_fix_e711():
    fp = FixPEP8()
    fp.fix_e711()

def test_PT_FixPEP8_fix_e712():
    fp = FixPEP8()
    fp.fix_e712()

def test_PT_FixPEP8_fix_e713():
    fp = FixPEP8()
    fp.fix_e713()

def test_PT_FixPEP8_fix_e714():
    fp = FixPEP8()
    fp.fix_e714()

def test_PT_FixPEP8_fix_e722():
    fp = FixPEP8()
    fp.fix_e722()

def test_PT_FixPEP8_fix_e731():
    fp = FixPEP8()
    fp.fix_e731()

def test_PT_FixPEP8_fix_e731():
    fp = FixPEP8()
    fp.fix_e731()

def test_PT_FixPEP8_fix_w291():
    fp = FixPEP8()
    fp.fix_w291()

def test_PT_FixPEP8_fix_w391():
    fp = FixPEP8()
    fp.fix_w391()

def test_PT_FixPEP8_fix_w503():
    fp = FixPEP8()
    fp.fix_w503()

def test_PT_get_index_offset_contents():
    get_index_offset_contents()

def test_PT_get_fixed_long_line():
    get_fixed_long_line()

def test_PT_longest_line_length():
    longest_line_length()

def test_PT_join_logical_line():
    join_logical_line()

def test_PT_untokenize_without_newlines():
    untokenize_without_newlines()

def test_PT_get_item():
    get_item()

def test_PT_reindent():
    reindent()

def test_PT_code_almost_equal():
    code_almost_equal()

def test_PT_split_and_strip_non_empty_lines():
    split_and_strip_non_empty_lines()

def test_PT_fix_e265():
    fix_e265()

def test_PT_refactor():
    refactor()

def test_PT_code_to_2to3():
    code_to_2to3()

def test_PT_fix_2to3():
    fix_2to3()

def test_PT_fix_w602():
    fix_w602()

def test_PT_find_newline():
    find_newline()

def test_PT_get_diff_text():
    get_diff_text()

def test_PT_shorten_line():
    shorten_line()

def test_PT_ReformattedLines_add():
    r = ReformattedLines()
    r.add()

def test_PT_ReformattedLines_add_comment():
    r = ReformattedLines()
    r.add_comment()

def test_PT_ReformattedLines_add_indent():
    r = ReformattedLines()
    r.add_indent()

def test_PT_ReformattedLines_add_line_break():
    r = ReformattedLines()
    r.add_line_break()

def test_PT_ReformattedLines_add_line_break_at():
    r = ReformattedLines()
    r.add_line_break_at()

def test_PT_ReformattedLines_add_space_if_needed():
    r = ReformattedLines()
    r.add_space_if_needed()

def test_PT_ReformattedLines_previous_item():
    r = ReformattedLines()
    r.previous_item()

def test_PT_ReformattedLines_fits_on_current_line():
    r = ReformattedLines()
    r.fits_on_current_line()

def test_PT_ReformattedLines_current_size():
    r = ReformattedLines()
    r.current_size()

def test_PT_ReformattedLines_line_empty():
    r = ReformattedLines()
    r.line_empty()

def test_PT_ReformattedLines_emit():
    r = ReformattedLines()
    r.emit()

def test_PT_Atoms_reflow():
    a = Atom()
    a.reflow()

def test_PT_Atoms_emit():
    a = Atom()
    a.emit()

def test_PT_Container_reflow():
    c = Container()
    c.reflow()

def test_PT_Tuple_open_bracket():
    t = Tuple()
    t.open_bracket()

def test_PT_Tuple_close_bracket():
    t = Tuple()
    t.close_bracket()

def test_PT_List_open_bracket():
    t = List()
    t.open_bracket()

def test_PT_List_close_bracket():
    t = List()
    t.close_bracket()

def test_PT_DictOrSet_open_bracket():
    t = DictOrSet()
    t.open_bracket()

def test_PT_DictOrSet_close_bracket():
    t = DictOrSet()
    t.close_bracket()

def test_PT_ListComprehension_size():
    t = ListComprehension()
    t.size()

def test_PT_normalize_multiline():
    normalize_multiline()

def test_PT_fix_whitespace():
    fix_whitespace()

def test_PT_Reindenter_run():
    r = Reindenter()
    r.run()

def test_PT_Reindenter_getline():
    r = Reindenter()
    r.getline()

def test_PT_refactor_with_2to3():
    refactor_with_2to3()

def test_PT_check_syntax():
    check_syntax()

def test_PT_filter_results():
    filter_results()

def test_PT_multiline_string_lines():
    multiline_string_lines()

def test_PT_commented_out_code_lines():
    commented_out_code_lines()

def test_PT_shorten_comment():
    shorten_comment()

def test_PT_normalize_line_endings():
    normalize_line_endings()

def test_PT_mutual_startswith():
    mutual_startswith()

def test_PT_code_match():
    code_match()

def test_PT_fix_code():
    fix_code() 

def test_PT_fix_lines():
    fix_lines()

def test_PT_fix_file():
    fix_file()

def test_PT_global_fixes():
    global_fixes()

def test_PT_apply_global_fixes():
    apply_global_fixes()

def test_PT_extract_code_from_function():
    extract_code_from_function()

def test_PT_create_parser():
    create_parser()

def test_PT_parse_args():
    parse_args()

def test_PT_read_config():
    read_config()

def test_PT_decode_filename():
    decode_filename()

def test_PT_supported_fixes():
    supported_fixes()

def test_PT_docstring_summary():
    docstring_summary()  

def test_PT_line_shortening_rank():
    line_shortening_rank()

def test_PT_standard_deviation():
    standard_deviation()

def test_PT_has_arithmetic_operator():
    has_arithmetic_operator()

def test_PT_count_unbalanced_brackets():
    count_unbalanced_brackets()

def test_PT_split_at_offsets():
    split_at_offsets()

def test_PT_LineEndingWrapper_write():
    le = LineEndingWrapper()
    le.write("testtext")

def test_PT_LineEndingWrapper_flush():
    le = LineEndingWrapper()
    le.flush("testtext")

def test_PT_match_file():
    match_file()

def test_PT_find_files():
    find_files()

def test_PT_fix_multiple_files():
    fix_multiple_files("testname")

def test_PT_is_python_file():
    is_python_file("testname")

def test_PT_is_probably_part_of_multiline():
    is_probably_part_of_multiline()

def test_PT_wrap_output():
    wrap_output()

def test_PT_get_encoding():
    get_encoding()

def test_PT_main():
    main()

def test_PT_CachedTokenizer_generate_tokens():
    c = CachedTokenizer()
    c.generate_tokens()