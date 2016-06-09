# file: tests.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-05 23:17:04 +0200
# Last modified: 2016-06-09 23:46:30 +0200

"""Nose tests for deploy.py"""

from deploy import compare


# def test_pfl():
#     rv = parsefilelist('filelist.rsmith')
#     assert rv[0] == ('deploy.py', 493, '/home/rsmith/src/scripts/deploy',
#                      None)


def test_compare():
    assert compare('deploy.py', 'deploy.py') == 1
    assert compare('deploy.py', 'tests.py') == 0
    assert compare('deploy.py', 'foo') == 2
    assert compare('bar', 'foo') == 3
