#!/usr/bin/env python
"""Tests for `gui_agent_loop_core` package."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gui_agent_loop_core import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
    del response


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()

    with patch("gui_agent_loop_core.cli.GuiAgentLoopCore.launch_server") as mock_launch_server:
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert "GuiAgentLoopCore" in result.output
        assert "Core logic of GUI and LLM agent bridge, including loop and controls." in result.output
        mock_launch_server.assert_called_once()

    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    print("help_result.output=", help_result.output)
    assert "--interpreter TEXT" in help_result.output
    assert "--help              Show this message and exit." in help_result.output
