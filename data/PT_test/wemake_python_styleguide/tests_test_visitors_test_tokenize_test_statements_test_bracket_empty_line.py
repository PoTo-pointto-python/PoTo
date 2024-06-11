import pytest
from wemake_python_styleguide.violations.consistency import BracketBlankLineViolation
from wemake_python_styleguide.visitors.tokenize.statements import BracketLocationVisitor
correct_empty_module = ''
correct_single_line = 'arr = []'
correct_single_line_items = 'arr = [1, 2, 3]'
correct_single_line_call = 'some(1, 2, 3)'
correct_method = "\nclass Some(object):\n    '''\n    Dco.\n\n    Some [\n        Example,\n    ]\n    '''\n\n    def __init__(self, node=None, text: Optional[str] = None) -> None:\n        ...\n"
correct_blank_line_in_middle_list = '\narr = [\n    1,\n\n    2,\n]\n'
correct_blank_line_in_middle_dict = '\narr = {\n    1:\n\n    2,\n}\n'
correct_blank_line_in_middle_parens = '\narr = (\n    1,\n\n    2,\n)\n'
correct_comment_start_of_list = '\narr = [\n    # comment\n    1,\n\n    2,\n]\n'
correct_comment_in_middle_of_list = '\narr = [\n    1,\n\n    # comment\n    2,\n]\n'
wrong_blank_line_at_start_list = '\nsome = [\n\n    1,\n    2,\n    3,\n]\n'
wrong_blank_line_at_end_list = '\nsome = [\n    1,\n    2,\n    3,\n\n]\n'
wrong_blank_line_after_comment = "\nextra_new_line = [  # some\n\n    'wrong',\n]\n"
wrong_blank_line_at_start_dict = '\narr = {\n\n    1: 2,\n}\n'
wrong_blank_line_at_end_dict = '\narr = {\n    1: 2,\n\n}\n'
wrong_blank_line_at_start_parens = '\narr = (\n\n    1,\n    2,\n)\n'
wrong_blank_line_at_end_parens = '\narr = (\n    1, 2,\n\n)\n'

@pytest.mark.parametrize('code', [correct_empty_module, correct_single_line, correct_single_line_call, correct_single_line_items, correct_method, correct_blank_line_in_middle_list, correct_blank_line_in_middle_dict, correct_blank_line_in_middle_parens, correct_comment_start_of_list, correct_comment_in_middle_of_list])
def test_correct_blank_lines(parse_tokens, assert_errors, default_options, code):
    code = correct_empty_module
    parse_tokens = parse_tokens()
    assert_errors = assert_errors()
    default_options = default_options()
    'Ensures that correct blank lines work.'
    file_tokens = parse_tokens(code)
    visitor = BracketLocationVisitor(default_options, file_tokens=file_tokens)
    visitor.run()
    assert_errors(visitor, [])

@pytest.mark.parametrize('code', [wrong_blank_line_at_start_list, wrong_blank_line_at_end_list, wrong_blank_line_after_comment, wrong_blank_line_at_start_dict, wrong_blank_line_at_end_dict, wrong_blank_line_at_start_parens, wrong_blank_line_at_end_parens])
def test_wrong_blank_lines(parse_tokens, assert_errors, default_options, code):
    code = wrong_blank_line_at_start_list
    parse_tokens = parse_tokens()
    assert_errors = assert_errors()
    default_options = default_options()
    'Ensures that incorrect blank lines raise a warning.'
    file_tokens = parse_tokens(code)
    visitor = BracketLocationVisitor(default_options, file_tokens=file_tokens)
    visitor.run()
    assert_errors(visitor, [BracketBlankLineViolation])
import io
import tokenize
from textwrap import dedent
import pytest

@pytest.fixture(scope='session')
def parse_tokens():
    """Parses tokens from a string."""

    def factory(code: str):
        lines = io.StringIO(dedent(code))
        return list(tokenize.generate_tokens(lambda : next(lines)))
    return factory

@pytest.fixture(scope='session')
def parse_file_tokens(parse_tokens):
    """Parses tokens from a file."""

    def factory(filename: str):
        with open(filename, 'r', encoding='utf-8') as test_file:
            file_content = test_file.read()
            return parse_tokens(file_content)
    return factory
from typing import Optional, Sequence
import pytest
from wemake_python_styleguide.violations.base import ASTViolation, TokenizeViolation
from wemake_python_styleguide.visitors.base import BaseVisitor

@pytest.fixture(scope='session')
def assert_errors():
    """Helper function to assert visitor violations."""

    def factory(visitor: BaseVisitor, errors: Sequence[str], ignored_types=None):
        if ignored_types:
            real_errors = [error for error in visitor.violations if not isinstance(error, ignored_types)]
        else:
            real_errors = visitor.violations
        assert len(errors) == len(real_errors)
        for (index, error) in enumerate(real_errors):
            assert error.code == errors[index].code
            if isinstance(error, (ASTViolation, TokenizeViolation)):
                assert error._node is not None
                assert error._location() != (0, 0)
    return factory

@pytest.fixture(scope='session')
def assert_error_text():
    """Helper function to assert visitor violation's text."""

    def factory(visitor: BaseVisitor, text: str, baseline: Optional[int]=None, *, multiple: bool=False):
        if not multiple:
            assert len(visitor.violations) == 1
        violation = visitor.violations[0]
        error_format = ': {0}'
        assert error_format in violation.error_template
        assert violation.error_template.endswith(error_format)
        reproduction = violation.__class__(node=violation._node, text=text, baseline=baseline)
        assert reproduction.message() == violation.message()
    return factory
import os
from collections import namedtuple
import pytest
from wemake_python_styleguide.options.config import Configuration
pytest_plugins = ['plugins.violations', 'plugins.ast_tree', 'plugins.tokenize_parser', 'plugins.async_sync']

@pytest.fixture(scope='session')
def absolute_path():
    """Fixture to create full path relative to `contest.py` inside tests."""

    def factory(*files: str):
        dirname = os.path.dirname(__file__)
        return os.path.join(dirname, *files)
    return factory

@pytest.fixture(scope='session')
def options():
    """Returns the options builder."""
    default_values = {option.long_option_name[2:].replace('-', '_'): option.default for option in Configuration._options}
    Options = namedtuple('options', default_values.keys())

    def factory(**kwargs):
        final_options = default_values.copy()
        final_options.update(kwargs)
        return Options(**final_options)
    return factory

@pytest.fixture(scope='session')
def default_options(options):
    """Returns the default options."""
    return options()