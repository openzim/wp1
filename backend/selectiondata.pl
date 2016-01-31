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

print "Old rows: " . count_rows($dbh) . "\n";

delete_all($dbh);

insert_from_stdin($dbh);

print "New rows: " . count_rows($dbh) . "\n";

$dbh->commit();

exit;

##################################################################

sub insert_from_stdin {
  my $dbh = shift;
  my $sth = $dbh->prepare("insert into selection_data values (?,?,?,?,?)");

  print "Inserting new data\n";

  my @parts;
  my $count;
  my $line;
  my ($hc, $pl, $ll, $ei); # hitcount, pagelinks, langlinks, external interest score
  while ( $line = <STDIN> ) { 
    $count++;
    if ( 0 == $count %  10000 ) { print "."; }
    if ( 0 == $count % 100000 ) { print " $count\n"; $dbh->commit(); }
      # The previous line should not call commit(), so that the entire job
      # can post as a single transaction. But that causes the database to reject
      # the job for being too big. So this is a hack to get it to complete. 

    chomp $line;
    @parts = split / /, $line, 4;

#    $parts[0] =~ s/_/ /g;


    $ll = $parts[1];
    $pl = $parts[2];
    $hc = $parts[3];
    $ei =   ( $hc > 0 ?  50*log10($hc) : 0) 
           + ( $pl > 0 ? 100*log10($pl) : 0)
           + ( $ll > 0 ? 250*log10($ll) : 0);
    $ei = floor($ei);

    $sth->execute($parts[0], $ll, $pl, $hc, $ei);

  }
  print " $count\n";


}

##################################################################


sub delete_all {
  my $dbh = shift;
  my $sth = $dbh->prepare("delete from selection_data");
  my $r = $sth->execute();
  print "Deleted  $r rows\n";
  return $r;
}


##################################################################

sub count_rows() { 
  my $dbh = shift;
  my $sth = $dbh->prepare("select count(sd_article) from selection_data");
  my $r = $sth->execute();
  my @r = $sth->fetchrow_array();
  return $r[0];
}

