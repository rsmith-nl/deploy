# /usr/bin/env python2
# vim:fileencoding=utf-8
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2013-11-20 22:08:38 +0100
# Modified: $Date$
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to install.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Script to install files."""

from __future__ import division, print_function
import sys
import os
import subprocess
from shutil import copyfile
import check

__version__ = '$Revision$'[11:-2]


def main(argv):
    """Entry point for this script.
    """
    if '-h' in argv:
        print('Usage: {} [-h][-v]'.format(argv[0]))
        print('-h: Help.')
        print('-v: Verbose; report if files are successfully installed.')
        sys.exit(0)
    verbose = '-v' in argv
    filelist = '.'.join(['filelist', os.environ['USER']])
    try:
        with open(filelist, 'r') as input:
            lines = input.readlines()
    except IOError as e:
        print(e)
        sys.exit(1)
    for src, perm, dest, cmds in check.parse(lines):
        if not check.identical(src, dest):
            try:
                copyfile(src, dest)
                os.chmod(dest, perm)
                if subprocess.call(cmds) is not 0:
                    s = 'Post-install commands for {} failed.'.format(dest)
                    check.ansiprint(s, fg=31)
            except Exception as e:
                s = "Installing '{}' as '{}' failed: {}".format(src, dest, e)
                check.ansiprint(s, fg=31)
                continue
            if verbose:
                s = "'{}' successfully installed as '{}'.".format(src, dest)
                check.ansiprint(s, fg=32)
        elif verbose:
                s = "'{}' is already installed.".format(src)
                check.ansiprint(s, fg=32)


if __name__ == '__main__':
    main(sys.argv)
