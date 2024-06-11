import pytest
pytest
from bokeh.models import CustomJSTransform, Dodge, Interpolator, Jitter, StepInterpolator

def test_CustomJSTransform() -> None:
    custom_js_transform = CustomJSTransform()
    assert custom_js_transform.func == ''
    assert custom_js_transform.v_func == ''

def test_Dodge() -> None:
    dodge = Dodge()
    assert dodge.value == 0
    assert dodge.range is None

def test_Jitter() -> None:
    jitter = Jitter()
    assert jitter.mean == 0
    assert jitter.width == 1
    assert jitter.distribution == 'uniform'
    assert jitter.range is None

def test_Interpolator() -> None:
    interpolator = Interpolator()
    assert interpolator.clip == True

def test_StepInterpolator() -> None:
    stept_interpolator = StepInterpolator()
    assert stept_interpolator.mode == 'after'