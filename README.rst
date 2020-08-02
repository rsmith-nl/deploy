Managing configuration files with ‘deploy’
##########################################

:author: Roland Smith
:date: 2020-08-01
:tags: python 3, deploying, installer

Classification
==============

The following `PyPI classifiers`_ apply:

* Development Status :: 5 - Production/Stable
* Environment :: Console
* Intended Audience :: Developers
* Intended Audience :: System Administrators
* License :: MIT
* Natural Language :: English
* Operating System :: POSIX
* Programming Language :: Python :: 3.6
* Programming Language :: Python :: 3.7
* Topic :: System :: Installation/Setup
* Topic :: System :: Systems Administration
* Topic :: Utilities

.. _PyPI classifiers: https://pypi.python.org/pypi?%3Aaction=list_classifiers


History
=======

This script grew out of my need for a multi-functional installer for
configuration files. I tend to keep those files in a separate git repository
rather than changing my $HOME into a git repository.

On UNIX, there is the venerable install_ program initially meant to install
binaries. While this works well it didn't completely fit my needs. Because
next to purely installing a file somewhere, I wanted to be able to check for
and view differences between the files in the repository and those in the
installed location. Additionally I wanted to have the option to run commands
after a file was installed. I could of course do this with a makefile_ and this
approach would be extremely flexible, but writing and maintaining such a Makefile
for every repo would be quite cumbersome.

.. _install: https://www.freebsd.org/cgi/man.cgi?query=install
.. _makefile: http://en.wikipedia.org/wiki/Make_%28software%29

Initially I developed a couple of perl scripts for this, ``check.pl`` and
``install.pl``. You can still find these in the ``attic`` subdirectory.
Later I combined them and expanded them in a single Python
script called ``deploy.py``. The user-interface was changed to enable
sub-commands and the ability to color diffs was added.


How it works
============

The ``deploy`` command is meant to be run from a color terminal; it uses `ANSI
escape codes`_ to color its output.

.. _ANSI escape codes: http://en.wikipedia.org/wiki/ANSI_escape_code

It is meant to be used from the root of e.g. a git repository.  When started,
``deploy`` looks for and reads the file named ``filelist.<HOSTNAME>.$USER`` in
the directory from which ``deploy`` is run.  So when run by a user named
“jdoe” on the host ``foo.yourplace.home`` it would look for a file
``filelist.foo.jdoe``.  This is suitable for installing files in the directory
tree owned by ``jdoe``. For installing files system wide (e.g. in ``/etc`` or
``/usr/local/etc``), create ``filelist.root`` and run ``deploy`` as the root
user.


File format
-----------

In these file lists, lines that have a ‘#’ as the first non-whitespace
characters are skipped as comments. The first non-comment line must contain a
list of fully qualified host names for which this file is valid. If the name
of the host where ``deploy`` is run is not in that list, it will quit.

The other non comment lines all have the same format::

    <source path> <mode> <destination path> <post-install commands>

* The *source path*  is path relative from the directory where ``deploy`` is called
  from. It may not contain whitespace.
* The *mode* is an octal number indicating the permissions of the destination
  file, see chmod(1).
* The *destination path* should be an absolute path including the name of
  the installed file. It *may not* contain whitespace. The reason for including
  the filename is so that you can e.g. install a file ``profile`` as
  ``/home/jdoe/.profile``.
* The rest of the line is considered the *post-install commands*. This may be
  empty and may contain spaces.


Commands
--------

The ‘deploy’ program has tree sub-commands or modes;

* *check*: Generate a list of files that are different from the installed
  files. If the verbose option (``-v``) is used, it lists for all files if they
  need installing or not.
* *status*: Equivalent to *check* with the ``-v`` option.
* *diff*: Generate a colored diff between the files in the repository and the
  installed files.
* *install*: Install the files in their destinations and run the post-install
  commands.


Examples
--------

The file ``filelist.jdoe`` in a ``setup`` directory contains the following
lines among others;

.. code-block:: console

    ../shared/fetchmailrc  400 /home/jdoe/.fetchmailrc

This installs the configuration file for ``fetchmail`` and makes sure that
only the owner can read it. Note how a relative path is used for the source,
and an absolute path is used for the destination. The first is for
convenience, the second for preventing mistakes.

The following line is an example of using post-install commands;

.. code-block:: console

    Xresources  644  /home/jdoe/.Xresources  xrdb -load /home/jdoe/.Xresources

This reloads the X resources into the X server after installing them.

Below is a usage example;

.. code-block:: console

    rlyeh:~/setup/rlyeh> ./deploy check
    The file '../shared/muttrc' differs from '/home/jdoe/.muttrc'.

    rlyeh:~/setup/rlyeh> ./deploy diff
    The file '../shared/muttrc' differs from '/home/jdoe/.muttrc'.
    --- /home/jdoe/.muttrc
    +++ ../shared/muttrc
    @@ -1,5 +1,5 @@
     # /home/jdoe/.muttrc
    -# $Date: 2014-12-19 00:46:55 +0100 $
    +# $Date: 2014-12-29 02:07:58 +0100 $

     #
     # Settings
    @@ -76,12 +76,11 @@
     set crypt_replyencrypt = yes
     set crypt_replysign = yes
     set crypt_replysignencrypted = yes
    -set crypt_use_gpgme = yes
     set crypt_verify_sig = yes
     set pgp_good_sign="^gpgv?: Good signature from "
     set pgp_sign_as = E9AF27B1
     set pgp_timeout = 3600
    +set pgp_use_gpg_agent=yes

     #
     # S/MIME stuff.

    rlyeh:~/setup/rlyeh> ./deploy install
    File '../shared/muttrc' was successfully installed as '/home/jdoe/.muttrc'.


Requirements
============

The ``deploy`` program was written for Python 3.6+ (developed and tested with
``python3.7``). It has no dependencies outside of Python's standard library.

For running the checks with ``make check``, pylama_ is required.

For running the tests in ``tests.py``, py.test_ is required.

.. _pylama: https://github.com/klen/pylama
.. _py.test: http://pytest.org/latest/


Installation
============

.. Note::

    If your system doesn't have ``\usr\bin\env``, or if your Python 3 is not
    in your $PATH, modify the first line of the `deploy` program to point to
    the location of the Python 3 program *before* installing it.

For a system-wide installation (UNIX-like systems):

* Make sure you don't already have an identically named program installed!
* Use ``make`` to install the script;

.. code-block:: console

    # make install

If you want to install it locally, just copy it to where you need it and make
it executable.

Removing the program can be done by running

.. code-block:: console

    # make uninstall
