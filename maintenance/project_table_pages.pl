#!/usr/bin/perl

# utility.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

A maintenance script to check/create pages to hold 
project tables

=cut

use strict;
use Encode;
use Data::Dumper;
use POSIX;
use Getopt::Long;

use utf8;
use encoding 'utf8';

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

my $fix = 0;
if ( $ARGV[0] eq "--fix" ) { 
  $fix = 1;
  shift @ARGV;
}

my $prefix = "Wikipedia:Version 1.0 Editorial Team/";
my $suffix= " articles by quality statistics";

my $i = 0;
my $edits = 0;
my $Limit = 2000;
my $t;

foreach $project ( sort {$a cmp $b} keys %$project_details ) {
   $i++;

   next unless ( $project =~ /\Q$ARGV[0]\E/);
   print "\n$project\n";

   my $content = api_content($prefix . $project . $suffix);
   print "Content: " . length($content). "\n";

   if ( length($content) == 0) { 
     print " -- empty / nonexistent\n";
     fix_page($project);
   } elsif ( $content =~ /User:WP 1.0 bot/ ) { 
     print " -- good\n";
   } else { 
     print " -- bad\n";
     fix_page($project) if ( $fix );
   }
    
   progress($start_time, $i, $count);
}

#########################################################

sub fix_page { 
  my $project = shift;
  my $content = << "HERE";
{{User:WP 1.0 bot/Tables/Project/$project}}
<noinclude>[[Category:$project articles by quality]]</noinclude>
HERE

  print "Fixing...\n=======\n$content=====\n";

  my $page = $prefix . $project . $suffix;

  api_edit($page, $content, "Setting this page to transclude bot-generated table");

  $edits++;
  if ($edits >= $Limit) { 
    print "\nLimit reached, stopping\n"; 
    exit; 
  }

}


#########################################################

sub progress { 
  my $end_time = time();
  my $start_time = shift;
  my $i = shift;
  my $count = shift;
  my $elapsed = $end_time - $start_time;

  my $left = $count - $i;
  my $rate = $i / (1 + $elapsed);
  my $timeleft = int($left / $rate);
  printf "-------------------";
  printf "done $i / $count in " . 
           format_time($elapsed) 
         . " (%4.4f /sec) : " 
       .  format_time($timeleft) 
       . "\n", $rate;
}


sub format_time { 
  my $time = shift;
  my $secs = $time % 60;
  $time = int($time / 60);
  my $mins = $time % 60;
  $time = int($time / 60);
  return sprintf "%4sh %2sm %2ss", $time, $mins, $secs;
}
