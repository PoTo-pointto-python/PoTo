import pytest
from wemake_python_styleguide.compat.constants import PY38
from wemake_python_styleguide.violations.best_practices import LoopControlFinallyViolation
from wemake_python_styleguide.visitors.ast.exceptions import WrongTryExceptVisitor
right_try_example_with_for = '\ndef function():\n    for element in range(10):\n        try:\n            ...\n        except:\n            ...\n        finally:\n            ...\n'
right_try_example_with_while = '\ndef function():\n    while first_element < second_element:\n        try:\n            ...\n        except:\n            ...\n        finally:\n            ...\n'
right_example_with_for = '\ndef function():\n    def some():\n        for elem in range(10):\n            if elem > 5:\n                {0}\n'
right_example_with_while = '\ndef function():\n    def some():\n        while a < b:\n            if a == 5:\n                {0}\n'
wrong_try_example = '\ndef function():\n    for element in range(10):\n        try:\n            ...\n        except:\n            ...\n        finally:\n            {0}\n'
wrong_try_example_with_while = '\ndef function():\n    while first_element < second_element:\n        try:\n            ...\n        except:\n            ...\n        finally:\n            {0}\n'

@pytest.mark.parametrize('statement', ['break', 'continue'])
@pytest.mark.parametrize('code', [right_example_with_for, right_example_with_while, right_try_example_with_for, right_try_example_with_while])
def test_right_finally(assert_errors, parse_ast_tree, code, statement, default_options, mode):
    statement = 'break'
    code = right_example_with_for
    assert_errors = assert_errors()
    parse_ast_tree = parse_ast_tree()
    default_options = default_options()
    mode = mode()
    'Testing that regular loops and loops with `try` are allowed.'
    tree = parse_ast_tree(mode(code.format(statement)))
    visitor = WrongTryExceptVisitor(default_options, tree=tree)
    visitor.run()
    assert_errors(visitor, [])

@pytest.mark.parametrize('statement', ['break'])
@pytest.mark.parametrize('code', [wrong_try_example, wrong_try_example_with_while])
def test_finally_with_break(assert_errors, parse_ast_tree, code, statement, default_options, mode):
    statement = 'break'
    code = wrong_try_example
    assert_errors = assert_errors()
    parse_ast_tree = parse_ast_tree()
    default_options = default_options()
    mode = mode()
    'Testing that `break` keyword is not allowed in `finally`.'
    tree = parse_ast_tree(mode(code.format(statement)))
    visitor = WrongTryExceptVisitor(default_options, tree=tree)
    visitor.run()
    assert_errors(visitor, [LoopControlFinallyViolation])

@pytest.mark.skipif(not PY38, reason='continue in finally works only since python3.8')
@pytest.mark.parametrize('statement', ['continue'])
@pytest.mark.parametrize('code', [wrong_try_example, wrong_try_example_with_while])
def test_finally_with_continue(assert_errors, parse_ast_tree, code, statement, default_options, mode):
    statement = 'continue'
    code = wrong_try_example
    assert_errors = assert_errors()
    parse_ast_tree = parse_ast_tree()
    default_options = default_options()
    mode = mode()
    'Testing that `continue` keyword is not allowed in `finally`.'
    tree = parse_ast_tree(mode(code.format(statement)))
    visitor = WrongTryExceptVisitor(default_options, tree=tree)
    visitor.run()
    assert_errors(visitor, [LoopControlFinallyViolation])

@pytest.mark.skipif(PY38, reason='continue in finally does not work till since python3.8')
@pytest.mark.parametrize('statement', ['continue'])
@pytest.mark.parametrize('code', [wrong_try_example, wrong_try_example_with_while])
def test_finally_with_continue_and_exception(assert_errors, parse_ast_tree, code, statement, default_options, mode):
    statement = 'continue'
    code = wrong_try_example
    assert_errors = assert_errors()
    parse_ast_tree = parse_ast_tree()
    default_options = default_options()
    mode = mode()
    'Testing using `continue` keyword in python < 3.8 raises an exception.'
    with pytest.raises(SyntaxError):
        parse_ast_tree(mode(code.format(statement)))
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
import ast
import sys
from textwrap import dedent
import pytest
from wemake_python_styleguide.transformations.ast_tree import transform

@pytest.fixture(scope='session')
def parse_ast_tree():
    """
    Function to convert code to AST.

    This helper mimics some transformations that generally
    happen in different ``flake8`` plugins that we rely on.

    This list can be extended only when there's a direct need to
    replicate the existing behavior from other plugin.

    It is better to import and reuse the required transformation.
    But in case it is impossible to do, you can reinvent it.

    Order is important.
    """

    def factory(code: str, do_compile: bool=True) -> ast.AST:
        code_to_parse = dedent(code)
        if do_compile:
            _compile_code(code_to_parse)
        return transform(ast.parse(code_to_parse))
    return factory

def _compile_code(code_to_parse: str) -> None:
    """
    Compiles given string to Python's AST.

    We need to compile to check some syntax features
    that are validated after the ``ast`` is processed:
    like double arguments or ``break`` outside of loops.
    """
    try:
        compile(code_to_parse, '<filename>', 'exec')
    except SyntaxError:
        if sys.version_info[:3] == (3, 9, 0):
            pytest.skip('Python 3.9.0 has strange syntax errors')
        raise
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
import pytest

@pytest.fixture()
def async_wrapper():
    """Fixture to convert all regular functions into async ones."""

    def factory(template: str) -> str:
        return template.replace('def ', 'async def ').replace('with ', 'async with ').replace('for ', 'async for ')
    return factory

@pytest.fixture()
def regular_wrapper():
    """Fixture to return regular functions without modifications."""

    def factory(template: str) -> str:
        return template
    return factory

@pytest.fixture(params=['async_wrapper', 'regular_wrapper'])
def mode(request):
    """Fixture that returns either `async` or regular functions."""
    return request.getfixturevalue(request.param)