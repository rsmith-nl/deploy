#!/usr/bin/perl
# Install files according to instructions in 'filelist.$USER'.
# Time-stamp: <2010-08-13 15:19:41 rsmith>
# $Id: 38a7b30e9198dd1c548ac90f7a554e8feaa1a682 $
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to install.pl. This work is published from
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

$name = `id -u -n`;

open(RF, "filelist.$name") || die "Cannot open list file 'filelist.$name'.";

while(<RF>) {
    chomp;
    if (/^#/) {next}; # Skip comment lines.
    if (/^[ \t]*$/) {next}; # skip empty lines.
    @cmds = split;
    $src = shift @cmds;
    $perm = shift @cmds; 
    $dest = shift @cmds;
    # Skip identical files.
    if (-e $dest) {
        $msrc = `md5 -q $src`;
        $mdest = `md5 -q $dest`;
        if ($msrc eq $mdest) {next};
    }
    # Create directories if necessary
    $tdir = `dirname $dest`;
    chomp $tdir;
    if (! -d $tdir) {
	print "\e[31m";
	$rv = system "install", "-d", $tdir;
	$rv>>8;
	if ($rv == 0) {
	    printf "\e[32mCreated %s.\n\e[39m", $tdir;
	} else {print "\e[39m";}
    }
    # Install the file
    print "\e[31m";
    $rv = system "install", "-p", "-m", $perm, $src, $dest;
    $rv>>8;
    if ($rv == 0) {
	printf "\e[32mInstalled %s as %s.\n\e[39m", $src, $dest;
	# Execute post-install commands.
	if (@cmds) {
	    $rv = system @cmds;
	    $rv>>8;
	    if ($rv != 0) {
		printf "\e[31mPost-install commands for %s failed.\n\e[39m", 
		$src;
	    }
	}
    } else {print "\e[39";}
}

close(RF);
