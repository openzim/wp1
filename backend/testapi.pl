#!/usr/bin/perl

# insert_logs.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

select STDOUT;
$| = 1;

use strict;

require 'read_conf.pl';
require 'database_www.pl';
require 'api_routines.pl';

use utf8;
use encoding 'utf8';

my $Opts = read_conf();



use Data::Dumper;

print Dumper(api_get_move_log(1, "Absoluteness (mathematical logic)"));
