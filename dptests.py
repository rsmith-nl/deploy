# file: dptests.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-05 23:17:04 +0200
# $Date$
# $Revision$

"""Nose tests for deploy.py"""

from deploy import parsefilelist, compare


def test_pfl():
    rv = parsefilelist('filelist.rsmith')
    assert rv[0] == ('deploy.py', 493, '/home/rsmith/src/scripts/deploy',
                     None)

def test_compare():
    assert compare('deploy.py', 'deploy.py') == 1
    assert compare('deploy.py', 'filelist.rsmith') == 0
    assert compare('deploy.py', 'foo') == 2
