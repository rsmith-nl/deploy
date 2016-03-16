#!/usr/bin/env python3
# vim:fileencoding=utf-8
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2013-11-20 22:08:38 +0100
# Last modified: 2016-03-16 19:35:34 +0100
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to deploy.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Script for deploying files. It can check for differences, show diffs and
install files. It will only work if a file named 'filelist.<name>' is
present, where <name> is the login name of the user."""

from difflib import unified_diff
from enum import IntEnum
from hashlib import sha256
from shutil import copyfile
import argparse
import os
import platform
import pwd
import stat
import subprocess
import sys

__version__ = '0.13.0'
ne = "The {} file '{}' does not exist."


# Standard ANSI colors
class Color(IntEnum):
    black = 0
    red = 1
    green = 2
    yellow = 3
    blue = 4
    magenta = 5
    cyan = 6
    white = 7


# File comparison result
class Cmp(IntEnum):
    differ = 0  # source and destination are different
    same = 1  # source and destination are identical
    nodest = 2  # destination doesn't exist
    nosrc = 3  # source doesn't exist


def main(argv):
    """
    Entry point for the deploy script.

    Arguments:
        argv: All command line arguments save the name of the script.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='also report if files are the same')
    parser.add_argument('-V', '--version', action='version',
                        version=__version__)
    parser.add_argument('command', choices=['check', 'diff', 'install'])
    fname = '.'.join(['filelist', pwd.getpwuid(os.getuid())[0]])
    args = parser.parse_args(argv)
    fn = check
    verbose = False
    if args.command == 'install':
        fn = install
    elif args.command == 'diff':
        fn = diff
    if args.verbose:
        verbose = True
    try:
        install_data = parsefilelist(fname)
    except IOError as e:
        print(e)
        parser.print_help()
        sys.exit(1)
    except ValueError as e:
        print(e)
        parser.print_help()
        sys.exit(2)
    for src, perm, dest, cmds in install_data:
        cv = compare(src, dest)
        fn(src, perm, dest, cmds, cv, verbose)


def parsefilelist(name):
    """
    Parse a install file list.

    An install file list should have the FQDN for the hosts on the first
    non-comment line. This should include the string returned by
    platform.node().

    Arguments
        name: The name of a file to parse.

    Returns:
        A list of (src, perm, dest, commands) tuples.
    """
    with open(name, 'r') as infile:
        lines = infile.readlines()
    lines = [ln.strip() for ln in lines]
    lines = [ln for ln in lines if len(ln) and not ln.startswith('#')]
    hostnames = lines[0]
    pn = platform.node()
    if pn not in hostnames:
        ve = "First line from '{}' doesn't include '{}'".format(name, pn)
        raise ValueError(ve)
    lines = lines[1:]
    installs = []
    for ln in lines:
        items = ln.split(None, 3)
        if len(items) < 3:
            continue
        if len(items) > 3:
            src, perm, dest, rem = items
            cmds = rem.split()
        else:
            cmds = None
            src, perm, dest = items
        installs.append((src, int(perm, base=8), dest, cmds))
    return installs


def compare(src, dest):
    """
    Compare two files.

    Arguments
        src: Path of the source file.
        dest: Path of the destination file.

    Returns:
        Cmp enum
    """
    xsrc, xdest = os.path.exists(src), os.path.exists(dest)
    if not xsrc:
        return Cmp.nosrc
    if not xdest:
        return Cmp.nodest
    with open(src, 'rb') as s:
        csrc = sha256(s.read()).digest()
    if xdest:
        with open(dest, 'rb') as d:
            cdest = sha256(d.read()).digest()
    else:
        cdest = b''
    if csrc == cdest:
        return Cmp.same
    return Cmp.differ


def ansiprint(s, fg='', bg='', i=False):
    """
    Prints a colored text with ansi escape sequences.

    Arguments
        fg: Optional foreground color.
        bg: Optional background color.
        i: Boolean to indicate intense colors (default False)
    """
    esc = '\033[{:d}{}m'
    iv = ''
    if i:
        iv = ";1"
    if fg != '':
        fg = esc.format(30+fg, iv)
    if bg != '':
        bg = esc.format(40+bg, iv)
    print(''.join([fg, bg, s, esc.format(0, '')]))


def colordiff(txt):
    """
    Print a colored diff.

    Arguments:
        txt: diff list or generator to print
    """
    for line in txt:
        line = line.rstrip()
        if line.startswith(('+++ ', '--- ')):
            ansiprint(line, fg=Color.yellow, i=True)
            continue
        if line.startswith('+'):
            ansiprint(line, fg=Color.green, i=True)
            continue
        if line.startswith('-'):
            ansiprint(line, fg=Color.red, i=True)
            continue
        if line.startswith('@@'):
            ansiprint(line, fg=Color.magenta, i=True)
            continue
        print(line)


def check(src, perm, dest, cmds, comp, verbose=False):
    """
    Report if src and dest are different.

    Arguments
        src: Location of the source file.
        perm: Permissions of the destination file (ignored).
        dest: Location of the destination file.
        cmds: Post-install commands (ignored).
        comp: Cmp enum
        verbose: Report if files are the same.
    """
    df = "The file '{}' differs from '{}'."
    sm = "The files '{}' and '{}' are the same."
    if comp == Cmp.differ:
        ansiprint(df.format(src, dest), fg=Color.red, i=True)
    elif comp == Cmp.nodest:
        ansiprint(ne.format('destination', src), fg=Color.black, bg=Color.red)
    elif comp == Cmp.nosrc:
        ansiprint(ne.format('source', src), fg=Color.black, bg=Color.red)
    elif comp == Cmp.same and verbose:
        ansiprint(sm.format(src, dest), fg=Color.green)


def diff(src, perm, dest, cmds, comp, verbose=False):
    """
    Print the difference between src and dest.

    Arguments
        src: Location of the source file.
        perm: Permissions of the destination file (ignored).
        dest: Location of the destination file.
        cmds: Post-install commands (ignored).
        cmp: Cmp enum
        verbose: Report on successful installs (ignored).
    """
    if comp != Cmp.differ:
        return
    with open(src) as s, open(dest) as d:
        srcl, destl = list(s), list(d)
        out = unified_diff(destl, srcl, dest, src)
        colordiff(out)


def install(src, perm, dest, cmds, comp, verbose=False):
    """
    Install src into dest and execute post-install commands.

    Arguments
        src: Location of the source file.
        perm: Permissions of the destination file.
        dest: Location of the destination file.
        cmds: Post-install commands.
        cmp: Cmp enum
        verbose: Report on successful installs.
    """
    if comp == Cmp.nosrc:
        ansiprint(ne.format('source', src), fg=Color.black, bg=Color.red)
    elif comp == Cmp.same:
        return
    try:
        if os.path.exists(dest):
            os.chmod(dest, stat.S_IRUSR | stat.S_IWUSR)
        copyfile(src, dest)
        os.chmod(dest, perm)
        if cmds and subprocess.call(cmds) is not 0:
            s = 'Post-install commands for {} failed.'.format(dest)
            ansiprint(s, fg=Color.red)
    except Exception as e:
        s = "Installing '{}' as '{}' failed: {}".format(src, dest, e)
        ansiprint(s, fg=Color.red)
        return
    s = "File '{}' was successfully installed as '{}'."
    ansiprint(s.format(src, dest), fg=Color.green)


if __name__ == '__main__':
    main(sys.argv[1:])
