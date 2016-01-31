#!/usr/bin/perl

# utility.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

A maintenance script

=cut



binmode STDOUT, ":utf8";

use strict;
use Encode;
use Data::Dumper;
use POSIX;
use Getopt::Long;


#############################################################
# Define global variables and then load subroutines

require 'read_conf.pl';
our $Opts = read_conf(); # Also initializes library paths

require 'database_routines.pl';
require 'wp10_routines.pl';
require 'api_routines.pl';

my $start_time = time();

my $project_details = db_get_project_details();

my $project;

my $count = scalar keys %$project_details;

print "Count: $count\n";

my $i = 0;
my $t;
foreach $project ( sort {$a cmp $b} keys %$project_details ) {
  next unless ( $project =~ /\Q$ARGV[0]\E/);
    $i++;
    print "$i / $count $project\n";
    $t = time();
    update_articles_table($project);
    db_commit();
    print "-- " . (time() - $t) . " seconds\n";
}

