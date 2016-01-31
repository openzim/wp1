#!/usr/bin/perl

# loadVersion.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

CGI program that takes a page title and timestamp and redirects
the browser to the corresponding revision on the wiki

=cut

use strict;
use Encode;
use URI::Escape;
use Data::Dumper;

require CGI;
require CGI::Carp; 
CGI::Carp->import('fatalsToBrowser');

require 'read_conf.pl';
our $Opts = read_conf();

require Mediawiki::API;
my $api = new Mediawiki::API;
$api->debug_level(0); # no output at all 

$api->base_url($Opts->{'api-url'});

my $cgi ;
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

  if ( ! defined $param{'article'} || ! defined $param{'timestamp'}) { 
    print CGI::header(-type=>'text/plain', -charset=>'utf-8');  
    print "Error: must specify an article and timestamp.\n";
    return;
  }

  if ( ! $Opts->{'server-url'} ) { 
    print CGI::header(-type=>'text/plain', -charset=>'utf-8');  
    print "Error: must specify server url in wp10.cnf\n";
    return;
  }


 
  my $rev = get_revision($api, $param{'article'} ,$param{'timestamp'});

  if ( ! defined $rev ) { 
    print CGI::header(-type=>'text/plain', -charset=>'utf-8');  
    print "Error: could not get revision id.\n";
    print "A: '" . $param{'article'} . "'\n";
    print "T: '" . $param{'timestamp'} . "'\n";
    return;
  }



  my $url = $Opts->{'server-url'} 
            . "?title=" . uri_escape($param{'article'}) 
            . "&oldid=" . $rev->{'revid'} . "\n";

  print << "HERE";
Location: $url

HERE
}

##############################################################

# XXX move this to database_www.pl and use the toolserver db

sub get_revision { 
  my $api = shift;
  my $article = shift;
  my $timestamp = shift;
  
  my $where = [ 'query',  'pages', 'page', 'revisions', 'rev'];

  my $rev = $api->makeXMLrequest([ 
      'action'  => 'query',
      'prop'    => 'revisions',
      'titles'  => encode("utf8", $article), # encoded
      'rvprop'  => 'ids|flags|timestamp|user|size|comment',
      'rvstart' => $timestamp,
      'rvlimit' => '1',
      'format'  => 'xml' ]);

  $rev = $api->child_data_if_defined($rev, $where);

  return $rev;
}




