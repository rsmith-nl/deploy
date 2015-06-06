# file: tests.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-05 23:17:04 +0200
# Last modified: 2015-06-07 00:41:36 +0200

"""Nose tests for deploy.py

Run with: ‘nosetests-3.4 -v dptests.py’

"""

from shutil import rmtree

from deploy import parsefilelist, compare


# def test_pfl():
#     rv = parsefilelist('filelist.rsmith')
#     assert rv[0] == ('deploy.py', 493, '/home/rsmith/src/scripts/deploy',
#                      None)


def test_compare():
    assert compare('deploy.py', 'deploy.py') == 1
    assert compare('deploy.py', 'tests.py') == 0
    assert compare('deploy.py', 'foo') == 2
    assert compare('bar', 'foo') == 3


def teardown():
    rmtree('__pycache__')
