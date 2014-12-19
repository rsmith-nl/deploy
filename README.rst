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

It is meant to be used from the root of e.g. a git repository.
When started, `deploy` looks for and reads the file named `filelist.$USER` in
the directory from which `deploy` is run. So for a user named “jdoe” it would
look for a file `filelist.jdoe`.


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

Requirements
============

It requires the following programs

* Python 3 (developed and tested with `python3.4`)
* `diff` (tested with the diff from GNU duffutils)
* `sha256` (tested with the FreeBSD version)


