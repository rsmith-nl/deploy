#!/usr/bin/env python2
# vim:fileencoding=utf-8
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2013-11-20 22:08:38 +0100
# Modified: $Date$
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to check.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Script to check which files need to be installed."""

from __future__ import division, print_function
import sys
import os
import subprocess

__version__ = '$Revision$'[11:-2]


def parse(lines):
    """Generator to parse a list of lines from a filelist.USER file. The lines
    in these files have a special format. Lines where the first non-whitespace
    character is a '#' are ignored, as are blank lines and lines that have less
    than three items.

    Lines should start with a source file name, then a permission for the
    installed file and then the destination file name. The rest of the line is
    a post-install command.

    :param lines: a list of lines
    :yields: a tuple (src, perm, dest, commands)
    """
    for ln in lines:
        ln = ln.strip()
        if ln.startswith('#'):
            continue
        items = ln.split(None, 3)
        if len(items) < 3:
            continue
        if len(items) > 3:
            src, perm, dest, rem = items
            cmds = rem.split()
        else:
            cmds = None
            src, perm, dest = items
        yield src, int(perm, base=8), dest, cmds


def identical(src, dest):
    """Test whether two files are identical.

    :param src: path of the source file.
    :param dest: path of the destination file.
    :returns: True if src and dest are the same, False otherwise.
    """
    csrc = subprocess.check_output(['sha256', '-q', src])
    cdest = subprocess.check_output(['sha256', '-q', dest])
    if csrc != cdest:
        return False
    else:
        return True


def ansiprint(s, fg='', bg=''):
    """Prints a text with ansi colors.

    :param fg: optional foreground color
    :param fg: optional background color
    """
    esc = '\033[{:d}m'
    if fg:
        fg = esc.format(fg)
    if bg:
        bg = esc.format(bg)
    print(''.join([fg, bg, s, esc.format(0)]))


def main(argv):
    """Entry point for the check script.

    :param argv: command line arguments
    """
    if '-h' in argv:
        print('Usage: {} [-h][-d][-v]'.format(argv[0]))
        print('-h: Help.')
        print('-d: (diff); Print the diff(1) output for different files.')
        print('-l: (long); lists all files, not just the different ones.')
        sys.exit(0)
    diffs = '-d' in argv
    verbose = '-l' in argv
    filelist = '.'.join(['filelist', os.environ['USER']])
    try:
        with open(filelist, 'r') as input:
            lines = input.readlines()
    except IOError as e:
        print(e)
        sys.exit(1)
    for src, perm, dest, cmds in parse(lines):
        if not os.path.exists(dest):
            ansiprint("'{}' does not exist.".format(dest), fg=30, bg=41)
            continue
        if not identical(src, dest):
            ansiprint("'{}' differs from '{}'.".format(src, dest), fg=31)
            if diffs:
                args = ['diff', '-u', '-d', src, dest]
                # Use Popen because diff can return 1!
                proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                out, _ = proc.communicate()
                print(out.decode())
        elif verbose:
            ansiprint("'{}' and '{}' are the same.".format(src, dest), fg=32)


if __name__ == '__main__':
    main(sys.argv)
