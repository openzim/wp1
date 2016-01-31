#!/usr/bin/perl

# copy_count.pl
# Copy count of participating projects to the wiki

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

use DBI;
our $dbh = db_connect_ro($Opts);


###################################################


my $sth = $dbh->prepare("select count(p_project) from tmpprojects ");
$_ = $sth->execute();

my @r = $sth->fetchrow_array();
print "Count: $r[0]\n";

api_edit("User:WP 1.0 bot/Data/Count", 
         $r[0], "Updating count: $r[0] projects");
