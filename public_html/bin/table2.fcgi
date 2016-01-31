#!/usr/bin/perl

# table2.pl
# Part of WP 1.0 bot 
# See the files README, LICENSE, and AUTHORS for more information

=head1 SYNOPSIS

CGI program to display table of global assessment info

=cut

use strict;
use Encode;

require 'read_conf.pl';
our $Opts = read_conf();
my $NotAClass = $Opts->{'not-a-class'};

require Mediawiki::API;
my $api = new Mediawiki::API;
$api->debug_level(0); # no output at all 
$api->base_url($Opts->{'api-url'});

use Data::Dumper;
use URI::Escape;

require POSIX;
POSIX->import('strftime');

require 'layout.pl';

my $timestamp = strftime("%Y-%m-%dT%H:%M:%SZ", gmtime(time()));


require 'tables_lib.pl';

#####################################################################

use DBI;
require "database_www.pl";
our $dbh = db_connect_rw($Opts);

require 'cache.pl';
my $cache_sep = "<!-- cache separator -->\n";

require CGI;
CGI::Carp->import('fatalsToBrowser');

my $cgi;
my $loop_counter = 0;
if ( $Opts->{'use_fastcgi'} ) {
  require CGI::Fast;
  while ( $cgi = CGI::Fast->new() ) { 
    main_loop($cgi);
  }
} else {
  $cgi = new CGI;
  $loop_counter = -5;
  main_loop($cgi);
}

exit;

############################################################

sub main_loop {
  my $cgi = shift;
  my %param = %{$cgi->Vars()};

  print CGI::header(-type=>'text/html', -charset=>'utf-8');      

  if ( defined $ARGV[0] && $ARGV[0] eq '--force') { 
    cached_global_ratings_table(1);
    exit;
  }
 
  layout_header('Overall summary table');

  my ($html, $wikicode, $created) = cached_global_ratings_table();
  my $currenttime = time();

  if ( (defined $html) && 0 < length $html ) { 
    print "<div class=\"navbox\">\n";
    print_header_text($created);
    print "</div>\n<center>\n";
    print $html;
    print "</center>\n";
    print "</div>\n";
  } else { 
      print << "HERE";
  <div class="navbox">
    <b>Error: no cached version of the table is available.</b><br/>
    Please contact this page\'s maintainer.
  </div>
HERE
  }

  $loop_counter++;
  layout_footer("Debug: PID $$ has handled $loop_counter requests");

  if ( $loop_counter >= $Opts->{'max-requests'} ) { exit; }
}

#####################################################################

sub print_header_text {
  my $created = shift;

  my $listURL = $Opts->{'list2-url'};
  
  print "Overall ratings data " 
      . "(<a href=\"" . $listURL . "\">lists</a> | <b>summary table</b>)\n";

  my $diff = time() - $created;

  my $suffix = "s";

  if ( $diff < 24*60*60 ) { 
    $diff = int($diff / (60*60));
    if ( $diff == 1 ) { $suffix = ""; }
    print "<br/>Updated $diff hour$suffix ago.<br/>\n";
  } else { 
    $diff = int($diff / (24*60*60));
    if ( $diff == 1 ) { $suffix = ""; }
    print "<br/>Updated $diff day$suffix ago.<br/>\n";
  }
}

#####################################################################


