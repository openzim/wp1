#!/usr/bin/perl

# table_lib.pl                                                         
# Part of WP 1.0 bot                                                
# See the files README, LICENSE, and AUTHORS for additional information   

=head1 SYNOPSIS     
                                                                              
Backend program to fetch wikitext of summary tables

=cut 

require 'read_conf.pl';
our $Opts = read_conf();

require 'tables_lib.pl';

use Getopt::Long;
use strict;

my $o_purge;
my $o_mode;
my $o_project;
my $o_category;
my $o_categoryNS;
my $o_title;
my $o_wikipage;

my $a = {};

GetOptions(
  "purge!" => \$o_purge,
  "mode=s" => \$o_mode,
  "category=s" => \$o_category,
  "categoryNS=i" => \$o_categoryNS,
  "project=s" => \$o_project ,
  "title=s" => \$o_title,
  "wikipage=s", \$o_wikipage
  );

# print "Purge: '$o_purge'\n";
# print "Mode: '$o_mode'\n";
# print "Project: '$o_project'\n";
# print "Title: '$o_title'\n";
# print "Category: '$o_category'\n";
# print "CategoryNS: '$o_categoryNS'\n";
# print "\n";

if ( (defined $o_category) ^ ($o_categoryNS) ) { 
  print "Error: --category and --categoryNS must be specified as a pair\n";
  usage();
}


my ($html, $wiki);

if ( $o_mode =~ /proj/ ) { 
  if ( ! defined $o_project ) {
    print "Error: must specify a project for mode=project\n";
    usage();
  }

  if ( defined $o_category) { 
    ($html, $wiki) = make_project_table($o_project, $o_category, 
                                        $o_categoryNS, $o_title);
  } else { 
    ( $html, $wiki) = cached_project_table($o_project, $o_purge);
  } 

 print $wiki;
 print "\n";

} elsif ( $o_mode =~ /global/ ) { 
  ( $html, $wiki) = cached_global_ratings_table($o_purge);
  print $wiki;
  print "\n";

} else { 
  print "Error: specify mode=project or mode=global\n";
  usage();
}

exit;

############################################################

sub usage() { 

  print << "HERE";
Usage:

* Output wikicode for PROJECT:
   
   $0 [--purge] --mode=project --project=PROJECT    

* Output wikicode for PROJECT articles in CATEGORY:
   
   $0 [--purge] --mode=project --project=PROJECT  \
            --category=CATEGORY --categoryNS=NSNUMBER

   NSNUMBER is the number of the namespace to look for in CATEGORY

* Output wikicode for global table:

   $0 [--purge] --mode=global

The --purge causes to table to be recreated even if it is cached.
Otherwise the cached version is returned if it is available.

HERE
exit;
}

