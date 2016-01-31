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

insert_from_stdin($dbh);

$dbh->commit();

exit;

##################################################################

sub insert_from_stdin {
  my $dbh = shift;
  my $sth = $dbh->prepare("update automatedselection set as_revid = ? where as_article = ? ");

  print "Inserting new data\n";

  my @parts;
  my $count;
  my $line;
  my ($hc, $pl, $ll, $ei); # hitcount, pagelinks, langlinks, external interest score
  while ( $line = <STDIN> ) { 
    $count++;
    if ( 0 == $count %  1000 ) { print "."; }
    if ( 0 == $count % 10000 ) { print " $count\n"; $dbh->commit(); }
      # The previous line should not call commit(), so that the entire job
      # can post as a single transaction. But that causes the database to reject
      # the job for being too big. So this is a hack to get it to complete. 

    chomp $line;

    @parts = split /\t/, $line;

    $parts[0] =~ s/_/ /g;
    $parts[0] =~ s/^"//;
    $parts[0] =~ s/"$//;
    $parts[0] =~ s/""/"/g;

    my $c = $sth->execute($parts[2], $parts[0]);

#    print "'$parts[0]' $parts[2] $c\n";
#    sleep 1;

  }
  print " $count\n";


}

##################################################################


