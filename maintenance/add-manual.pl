#!/usr/bin/perl

# utility.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

A maintenance script to update the selection data table

=cut

binmode STDOUT, ":utf8";

use strict;
use Encode;
use Data::Dumper;
use POSIX;
use Getopt::Long;

select STDOUT;
$| = 1;

#############################################################
# Define global variables and then load subroutines

require 'read_conf.pl';
our $Opts = read_conf(); # Also initializes library paths

require 'database_routines.pl';
require 'wp10_routines.pl';
require 'api_routines.pl';

my $start_time = time();

my $dbh = database_handle();

my $file = $ARGV[0];
my $type = "release";
my $reason = $ARGV[1];
my $user = "WP 1.0 bot";

if ( ( $file eq "") || ($reason eq "") || ( ! -r $file) ) { 
  die "Usage: $0 FILE REASON\n";
}

my $sthart = $dbh->prepare("INSERT INTO manualselection VALUES (?,?,?) 
                              ON DUPLICATE KEY UPDATE ms_article = ms_article");
my $sthlog = $dbh->prepare("INSERT INTO manualselectionlog
                                VALUES (?,?,?,?,?,?)");

my $timestamp = strftime("%Y%m%d%H%M%S", gmtime(time()));

my ($r1, $r2, $r3, $art);
open IN, "<", $file;
while ( $art = <IN> ) { 
  chomp $art;

  my $error = "";

  $r1 = $sthart->execute($art,$type,$timestamp);
                               
  if ( 1 == $r1 ) {
    $r2 = $sthlog->execute($art, $type, $timestamp, "add", $user, $reason);
    if ( 1 != $r2 ) {
      $error = "Failed step 2: $r2";
    } 
  } elsif ( $r1 == 2) { 
    print "Duplicate: $art\n";
  } else {
    $error = "Failed step 1: $r1";
  } 

  if ( $error ne "") { 
    die "Error: $error\n";
  }
  print "$art -- $r1 $r2\n";

}


my $r3 = $dbh->commit();
print "Commit -- $r3\n";

