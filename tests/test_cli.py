import pytest

from ctrler.cli import _check_binding_warning


@pytest.mark.parametrize("host", ["foo.bar.baz", "1.2.3.4"])
def test_check_binding_warning_no_warning(host):
    _check_binding_warning(host=host)


def test_warning_is_printed(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda *args, **kwargs: "n")

    with pytest.raises(SystemExit):
        _check_binding_warning("0.0.0.0")

    captured = capsys.readouterr()
    assert "WARNING" in captured.out


@pytest.mark.parametrize(
    "host, input_return_value, should_raise",
    [
        ("0.0.0.0", "y", False),
        ("0.0.0.0", "Y", False),
        ("0.0.0.0", "n", True),
        ("0.0.0.0", "N", True),
        ("0.0.0.0", "", True),
        ("0.0.0.0", "foo", True),
    ],
)
def test_check_binding_warning_exit(
    host, input_return_value, should_raise, monkeypatch, capsys
):
    monkeypatch.setattr("builtins.input", lambda *args, **kwargs: input_return_value)
    if should_raise:
        with pytest.raises(SystemExit):
            _check_binding_warning(host=host)
    else:
        _check_binding_warning(host=host)
    captured = capsys.readouterr().out
    assert "WARNING" in captured
