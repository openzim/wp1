#!/usr/bin/perl

use POSIX 'strftime';

print "Content-type: text/plain\n\n";

system "ssh", "login.toolserver.org", "/home/cbm/wp10.2g/alpha/status.pl";
