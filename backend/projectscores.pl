#!/usr/bin/perl

# utility.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

A maintenance script to update the wikiproject scores

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

if ( !  ( ( -r $ARGV[0])  && (-r $ARGV[1]) )) { 
  die "usage: $0 ArticlesFile SubprojectsFile\n";
}

insert_from_file($dbh, $ARGV[0]);
insert_subprojects($dbh, $ARGV[1]);

$dbh->commit();

exit;

##################################################################

sub insert_from_file {
  my $count = 0;
  my $dbh = shift;
  my $file = shift;

  my $sthdata = $dbh->prepare("select sd_langlinks, sd_pagelinks, sd_hitcount 
                            from selection_data where sd_article = ?");

  my $sthupdate = $dbh->prepare("update projects set p_scope = ? 
                           where p_project = ?");

  my $line;
  my @parts;
  my $project;
  my $article;
  my @data;
  my ($n, $score, $article);
  open IN, "<", $file;
  while ( $line = <IN> ) { 
    $count++;
    my $c_hitcount = 0;
    my $c_langlinks = 0;
    my $c_pagelinks = 0;

    chomp($line); 
    @parts = split /\t/, $line;
    $project = shift @parts;
   
    while ( $article = shift @parts ) { 
#      $article =~ s/_/ /g;
      $sthdata->execute($article);
      $n = @data = $sthdata->fetchrow_array();
      print "ART $article " . (join " ", @data) . "\n";
      if ( $n == 0 ) { 
        print "### Missing article $article\n"; 
      }
      
      $c_langlinks += $data[0];
      $c_pagelinks += $data[1];     
      $c_hitcount += $data[2];
    }
    
    $score =    50 * log10($c_hitcount) 
             + 100 * log10($c_pagelinks) 
             + 250 * log10($c_langlinks) ;

    $score = int($score);

    print "PRO $project\tLL $c_langlinks\tPL $c_pagelinks\tHC $c_hitcount\tSCORE $score\n"; 

    $project =~ s/_/ /g;
    $n = $sthupdate->execute($score, $project);
    print "UPD $n $project\n\n";
  }
}

##################################################################

sub insert_subprojects {
  my $count = 0;
  my $dbh = shift;
  my $file = shift;

  my $sthdata = $dbh->prepare("select p_scope from projects where p_project = ?");

  my $sthupdate = $dbh->prepare("update projects set p_scope = ? 
                           where p_project = ?");

  open IN, "<", $file;
  my ($project, $subproject, $n, $m, $score, $line);
  my @data;
  while ( $line = <IN> ) { 
    chomp $line;
    ($subproject, $project) = split /\t/, $line, 2;
    $n = $sthdata->execute($project);
    @data = $sthdata->fetchrow_array();
    $score = $data[0];
    $m = $sthupdate->execute($score, $subproject);
    print "SUB $subproject -> $project $score  / $n $m\n";
  }
}

##################################################################

sub count_rows() { 
  my $dbh = shift;
  my $sth = $dbh->prepare("select count(sd_article) from selection_data");
  my $r = $sth->execute();
  my @r = $sth->fetchrow_array();
  return $r[0];
}



sub log10 {
  my $n = shift;
  return 0 if ( 1 > $n ) ;
  return log($n)/log(10);
}

