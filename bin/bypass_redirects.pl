#!/usr/bin/perl

# utility.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

A maintenance script to update the wikiproject scores

=cut

#binmode STDOUT, ":utf8";

use lib '/data/project/enwp10/backend';

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

my $sth = $dbh->prepare ("select pl_title from enwiki_p.page 
                          join enwiki_p.pagelinks on
                            page_id = pl_from 
                            and pl_namespace = 0
                            and page_title = ? 
                            where page_namespace = 0 
                            and page_is_redirect = 1");

my ($a, $n, @p);
while ( $a = <STDIN> ) { 
  chomp $a;
  $a =~ s/ /_/g;
  $n = $sth->execute($a);
  if ( $n == 0 ) { 
    print "$a\n"; 
    next;
  }
  @p = $sth->fetchrow_array();
  print "$p[0]\n";
}

