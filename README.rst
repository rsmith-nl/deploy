The ‘deploy’ program
####################

:date: 2014-12-19
:tags: python, deploying, installer
:author: Roland Smith


History
=======

This script grew out of my need for a multi-functional installer for
configuration files. I tend to keep those files in a separate git repository
rather than changing my $HOME into a git repository.

On UNIX, there is the venerable “install” program initially meant to install
binaries. While this works well it didn't completely fit my needs. Because
next to purely installing a file somewhere, I wanted to be able to check for
and view differences between the files in the repository and those in the
installed location. Additionally I wanted to have the option to run commands
after a file was installed. I could of course do this with a Makefile and this
approach would be very flexible, but writing and maintaining such a Makefile
would be quite cumbersome.


How it works
============

The `deploy` command is meant to be run from a color terminal.

It is meant to be used from the root of e.g. a git repository.  When started,
`deploy` looks for and reads the file named `filelist.$USER` in the directory
from which `deploy` is run. So when run by a user named “jdoe” it would look
for a file `filelist.jdoe`.


file format
-----------

In these file lists, lines that have a ‘#’ as the first non-whitespace
characters are skipped as comments. The first non-comment line must contain a
list of fully qualified host names for which this file is valid. If the name
of the host where ‘deploy’ is run is not in that list, it will quit.

The other non comment lines all have the same format::

    <source path> <mode> <destination path> <post-install commands>

* The *source path*  is path relative from the directory where `deploy` is called
  from. It may not contain whitespace.
* The *mode* is an octal number indicating the permissions of the destination
  file, see chmod(1).
* The *destination path* should be an absolute path including the name of
  the installed file. It may not contain whitespace. The reason for including
  the filename is so that you can e.g. install a file `profile` as
  `/home/jdoe/.profile`.
* The rest of the line is considered the *post-install commands*. This may be
  empty and may contain spaces.


commands
--------

The ‘deploy’ program has tree sub-commands or modes;

* *check*: Generate a list of files that are different from the installed
  files. If the verbose option (`-v`) is used, it lists for all files if they
  need installing or not.
* *diff*: Generate a colored diff between the files in the repository and the
  installed files.
* *install*: Install the files in their destinations and run the post-install
  commands.


Examples
--------

The file `filelist.jdoe` in a `setup` directory contains the following
lines among others::

    ../shared/fetchmailrc  400 /home/jdoe/.fetchmailrc

This installs fetchmail's configuration file and makes sure that only the
owner can read it. Note how a relative path is used for the source, but an
absolute path is used for the destination.

The following line is an example of using post-install commands::

    Xresources  644  /home/jdoe/.Xresources  xrdb -load /home/jdoe/.Xresources

This reloads the X resources into the X server after installing them.


Requirements
============

The `deploy` program is written for Python 3 (developed and tested with
`python3.4`). It has no dependencies outside of Python's standard
library.


Installation
============

UNIX-like operating systems
---------------------------

This includes Linux, all BSD variants, Apple's OS X.

For a system-wide installation:

* Make sure you don't already *have* an identically named program installed!
* Copy the `deploy.py` script to a location in your path as `deploy`
* Make it executable.

For example::

    cp -p deploy.py ~/bin/deploy
    chmod 755 ~/bin/deploy

If you want to install it locally, just copy it to where you need it and make
it executable.

.. Note::

    If your system doesn't have `\usr\bin\env`, or if your Python 3 is not not
    in your $PATH, modify the first line of the `deploy` program to point to
    the location of the Python 3 program before installing it.


Windows
-------

Copy `deploy.py` to the `scripts` directory of your Python 3 installation.
Since I do not use MS windows in my development environment I'm not able to
give more specific advice.

Instead of the standard `cmd.exe` shell, I would suggest you use e.g. the git
BASH that comes with `MSYS git`_ distribution.

.. _MSYS git: http://msysgit.github.io/
