#!/usr/bin/perl

# check-stats_page.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

Check that a project has a statistics table page
under Wikipedia:Version 1.0 Editorial Team/

=cut

use utf8;
use encoding 'utf8';

binmode STDOUT, ":utf8";
select STDOUT;
$| = 1;

use strict;
use Encode;

#############################################################
# Define global variables and then load subroutines

require 'read_conf.pl';
our $Opts = read_conf(); # Also initializes library paths

require 'database_routines.pl';
require 'wp10_routines.pl';
require 'api_routines.pl';

my $project = $ARGV[0];

if ( ! defined $project ) { 
  print "Usage: $0 PROJECT\n";
  exit;
}

my $tablepage = "User:WP 1.0 bot/Tables/Project/$project";
my $transpage = "Wikipedia:Version 1.0 Editorial Team/" . $project 
        . " articles by quality statistics";

my $content = api_content($transpage);
if ( 0 == length $content)  { 
   my $summary = "Transcluding assessment table\n";
   my $wiki = << "HERE";
{{$tablepage}}
<noinclude>[[Category:$project articles by quality]]</noinclude>
HERE

   if ( ! defined $ENV{'DRY_RUN'}) {
     api_edit( $transpage, $wiki, $summary);
   } else { 
     print "Need to create transclusion page\n$wiki\n--\n";
  }
} else { 
  print "Transclusion page exists\n";
}
