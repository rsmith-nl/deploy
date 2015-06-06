#!/usr/bin/env python3
# vim:fileencoding=utf-8
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2013-11-20 22:08:38 +0100
# Last modified: 2015-06-06 22:26:42 +0200
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to deploy.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Script for deploying files. It can check for differences, show diffs and
install files. It will only work if a file named 'filelist.<name>' is
present, where <name> is the login name of the user."""

from difflib import unified_diff
from hashlib import sha256
from shutil import copyfile
import argparse
import os
import platform
import pwd
import subprocess
import sys

__version__ = '$Revision$'[11:-2]


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
    try:
        installs = parsefilelist(fname)
    except IOError as e:
        print(e)
        parser.print_help()
        sys.exit(1)
    except ValueError as e:
        print(e)
        parser.print_help()
        sys.exit(2)
    args = parser.parse_args(argv)
    install = False
    diffs = False
    if args.command == 'install':
        install = True
        diffs = False
    if args.verbose:
        diffs = True
    ne = "The file '{}' does not exist."
    df = "The file '{}' differs from '{}'."
    sm = "The files '{}' and '{}' are the same."
    for src, perm, dest, cmds in installs:
        rv = compare(src, dest)
        if rv == 2:
            if install:
                do_install(src, perm, dest, cmds, True)
            else:
                ansiprint(ne.format(dest), fg=30, bg=41)
        elif rv == 3:
            ansiprint(ne.format(src), fg=30, bg=41)
        elif rv == 0:
            if install:
                do_install(src, perm, dest, cmds, True)
            else:
                ansiprint(df.format(src, dest), fg=31, i=True)
                if diffs:
                    with open(src) as s, open(dest) as d:
                        srcl, destl = list(s), list(d)
                    out = unified_diff(destl, srcl, dest, src)
                    colordiff(out)
        elif rv == 1 and args.verbose:
            ansiprint(sm.format(src, dest), fg=32)


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
        0 if src and dest are not the same,
        1 if they are,
        2 if dest doesn't exist,
        3 if src doesn't exist.
    """
    xsrc, xdest = os.path.exists(src), os.path.exists(dest)
    if not xdest:
        return 2
    if not xsrc:
        return 3
    with open(src, 'rb') as s:
        csrc = sha256(s.read()).digest()
    if xdest:
        with open(dest, 'rb') as d:
            cdest = sha256(d.read()).digest()
    else:
        cdest = b''
    if csrc == cdest:
        return 1
    return 0


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
    if fg:
        fg = esc.format(fg, iv)
    if bg:
        bg = esc.format(bg, iv)
    print(''.join([fg, bg, s, esc.format(0, '')]))


def do_install(src, perm, dest, cmds, verbose):
    """
    Install src into dest and execute post-install commands.

    Arguments
        src: Location of the source file.
        perm: Permissions of the destination file.
        dest: Location of the destination file.
        cmds: Post-install commands.
        verbose: Report on successful installs.
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


def colordiff(txt):
    """
    Print a colored diff.

    Arguments:
        txt: diff list or generator to print
    """
    for line in txt:
        line = line.rstrip()
        if line.startswith(('+++ ', '--- ')):
            ansiprint(line, fg=33, i=True)
            continue
        if line.startswith('+'):
            ansiprint(line, fg=32, i=True)
            continue
        if line.startswith('-'):
            ansiprint(line, fg=31, i=True)
            continue
        if line.startswith('@@'):
            ansiprint(line, fg=35, i=True)
            continue
        print(line)


if __name__ == '__main__':
    main(sys.argv[1:])
