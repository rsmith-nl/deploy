# file: tests.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-05 23:17:04 +0200
# Last modified: 2017-06-04 15:22:49 +0200
"""Nose tests for deploy.py"""

from deploy import compare


def test_compare():
    """Tests for the compare function."""
    assert compare("deploy.py", "deploy.py") == 1
    assert compare("deploy.py", "tests.py") == 0
    assert compare("deploy.py", "foo") == 2
    assert compare("bar", "foo") == 3
