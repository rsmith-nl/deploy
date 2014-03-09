#!/usr/bin/env python2
# vim:fileencoding=utf-8
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2013-11-20 22:08:38 +0100
# Modified: $Date$
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to deploy.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Script to check which files need to be installed."""

from __future__ import division, print_function
import sys
import os
import subprocess
from shutil import copyfile

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


def compare(src, dest):
    """Compare two files.

    :param src: path of the source file.
    :param dest: path of the destination file.
    :returns: 0 if src and dest are not the same, 1 if they are,
    2 if dest doesn't exist.
    """
    if not os.path.exists(dest):
        return 2
    csrc = subprocess.check_output(['sha256', '-q', src])
    if os.path.exists(dest):
        cdest = subprocess.check_output(['sha256', '-q', dest])
    else:
        cdest = ''
    if csrc == cdest:
        return 1
    return 0


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


def do_install(src, perm, dest, cmds, verbose):
    """Install src into dest and execute post-install commands.

    :param src: location of the source file
    :param perm: permissions of the destination file
    :param dest: location of the destination file
    :param cmds: post-install commands
    :param verbose: report on successful installs.
    """
    try:
        copyfile(src, dest)
        os.chmod(dest, perm)
        if cmds and subprocess.call(cmds) is not 0:
            s = 'Post-install commands for {} failed.'.format(dest)
            ansiprint(s, fg=31)
    except Exception as e:
        s = "Installing '{}' as '{}' failed: {}".format(src, dest, e)
        ansiprint(s, fg=31)
    if verbose:
        s = "File '{}' was successfully installed as '{}'.".format(src, dest)
        ansiprint(s, fg=32)


def main(argv):
    """Entry point for the check script.

    :param argv: command line arguments
    """
    ne = "The file '{}' does not exist."
    df = "The file '{}' differs from '{}'."
    sm = "The files '{}' and '{}' are the same."
    if '-h' in argv:
        print('Usage: {} [-h][-d|-i][-v]'.format(argv[0]))
        print('-h: help')
        print('-d: print the diff(1) output for different files')
        print('-i: install files')
        print('-v: verbose; report if files are the same')
        sys.exit(0)
    diffs = '-d' in argv
    verbose = '-v' in argv
    install = '-i' in argv
    if install:
        diffs = False
    filelist = '.'.join(['filelist', os.environ['USER']])
    try:
        with open(filelist, 'r') as input:
            lines = input.readlines()
    except IOError as e:
        print(e)
        sys.exit(1)
    for src, perm, dest, cmds in parse(lines):
        rv = compare(src, dest)
        if rv == 2:
            if install:
                do_install(src, perm, dest, cmds, verbose)
            else:
                ansiprint(ne.format(dest), fg=30, bg=41)
        if rv == 0:
            if install:
                do_install(src, perm, dest, cmds, verbose)
            else:
                ansiprint(df.format(src, dest), fg=31)
                if diffs:
                    args = ['diff', '-u', '-d', src, dest]
                    # Use Popen because diff can return 1!
                    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
                    out, _ = proc.communicate()
                    print(out.decode())
        elif rv == 1 and verbose:
            ansiprint(sm.format(src, dest), fg=32)


if __name__ == '__main__':
    main(sys.argv)
