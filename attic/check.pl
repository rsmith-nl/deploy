#!/usr/bin/perl
# Check for changes in files according to instructions in 'filelist.$USER'.
# Time-stamp: <2010-08-13 15:20:51 rsmith>
# $Id: 2088790e9bde79f4476a003adc6c9b58dc8f1aa5 $
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to check.pl. This work is published from
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

use Getopt::Std;

getopts('ldh');

if ($opt_h == 1) {
    print "Usage: ./check.pl [-hld]\n";
    print "-l\t(long); lists all files, not just the different ones.\n"; 
    print "-d\t(diff); Print the diff(1) output for different files.\n"; 
    exit 0;
}

$name = `id -u -n`;

open(RF, "filelist.$name") || die "Cannot open list file 'filelist.$name'.";

while(<RF>) {
    chomp;
    if (/^#/) {next}; # skip comment lines.
    if (/^[ \t]*$/) {next}; # skip empty lines.
    ($src,$perm,$dest) = split;
# For debugging.
#    printf("src: \'%s\', perm: %d, dest: \'%s\'\n", $src,$perm,$dest); 
    if (-r $dest) {
	$msrc = `md5 -q $src`;
	$mdest = `md5 -q $dest`;
	if ($msrc ne $mdest) {
	    printf "\e[31m%s differs from %s\n\e[0m", $src, $dest; 
	    if ($opt_d == 1) {
		system "diff", "-u", $dest, $src;
	    }
	} elsif ($opt_l == 1) {
	    printf "\e[32m%s matches %s\n\e[0m", $src, $dest;
	}
    } else {
	printf "\e[41m\e[30m%s cannot be read.\n\e[0m", $dest;
    }
}

close(RF);
