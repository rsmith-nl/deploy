#!/usr/bin/env python3
# file: deploy.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2014-03-09T17:08:09+01:00
# Last modified: 2020-08-01T22:58:55+0200
"""
Script for deploying files.

It can check for differences, show diffs and install files. It will only work if
a file named 'filelist.<host>.<name>' is present, where <host> is the host name
without domain, and <name> is the login name of the user.
"""

from difflib import unified_diff
from enum import IntEnum
from hashlib import sha256
from shutil import copyfile
import argparse
import os
import pwd
import stat
import subprocess
import sys

__version__ = '2.2'


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
    if comp == Cmp.differ:
        ansiprint(f"The file '{src}' differs from '{dest}'.", fg=Color.red, i=True)
    elif comp == Cmp.nodest:
        ansiprint(f"The destination file '{dest}' does not exist", fg=Color.black, bg=Color.red)
    elif comp == Cmp.nosrc:
        ansiprint(f"The source file '{src}' does not exist.", fg=Color.black, bg=Color.red)
    elif comp == Cmp.same and verbose:
        ansiprint(f"The files '{src}' and '{dest}' are the same.", fg=Color.green)


def status(src, perm, dest, cmds, comp, _):
    """
    Report the status for all files.
    Equivalent to ‘check’ with the verbose option.
    """
    check(src, perm, dest, cmds, comp, verbose=True)


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
        comp: Cmp enum
        verbose: Report on successful installs.
    """
    if comp == Cmp.nosrc:
        ansiprint(f"The source file '{src}' does not exist.", fg=Color.black, bg=Color.red)
    elif comp == Cmp.same:
        return
    try:
        if os.path.exists(dest):
            os.chmod(dest, stat.S_IRUSR | stat.S_IWUSR)
        copyfile(src, dest)
        os.chmod(dest, perm)
        if cmds and subprocess.call(cmds) != 0:
            ansiprint(f'Post-install commands for {dest} failed.', fg=Color.red)
    except Exception as e:
        ansiprint(f"Installing '{src}' as '{dest}' failed: {e}", fg=Color.red)
        return
    ansiprint(f"File '{src}' was successfully installed as '{dest}'.", fg=Color.green)


cmdset = {'check': check, 'status': status, 'diff': diff, 'install': install}


class Color(IntEnum):
    """Standard ANSI colors."""

    black = 0
    red = 1
    green = 2
    yellow = 3
    blue = 4
    magenta = 5
    cyan = 6
    white = 7


class Cmp(IntEnum):
    """File comparison result."""

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
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='also report if files are the same'
    )
    parser.add_argument('-V', '--version', action='version', version=__version__)
    parser.add_argument('command', choices=cmdset.keys())
    args = parser.parse_args(argv)
    verbose = False
    fn = cmdset[args.command]
    if args.verbose:
        verbose = True
    try:
        install_data = parsefilelist()
    except Exception as e:
        ansiprint(str(e), fg=Color.red)
        parser.print_help()
        sys.exit(1)
    for src, perm, dest, cmds in install_data:
        cv = compare(src, dest)
        fn(src, perm, dest, cmds, cv, verbose)


def parsefilelist():
    """
    Parse a install file list.

    The install file list should have the name “filelist.<hostname>.<user>”,
    where the hostname is *without* the domain.

    Returns:
        A list of (src, perm, dest, commands) tuples.
    """
    user = pwd.getpwuid(os.getuid()).pw_name
    hostname = os.environ['HOST'].split('.')[0]
    filename = '.'.join(['filelist', hostname, user])
    installs = []
    with open(filename, 'r') as infile:
        for ln in infile:
            if ln.startswith('#') or ln.isspace():
                continue
            try:
                src, perm, dest, *cmds = ln.strip().split()
            except ValueError:
                ansiprint(f'Invalid line in {filename}: “{ln}”', fg=Color.red)
                continue
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
    Print a colored text with ansi escape sequences.

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
        fg = esc.format(30 + fg, iv)
    if bg != '':
        bg = esc.format(40 + bg, iv)
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


if __name__ == '__main__':
    main(sys.argv[1:])
