#!/usr/bin/perl

# index.fcgi
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

CGI to display an HTML index page

=cut

use strict;
use Encode;
use URI::Escape;

require 'read_conf.pl';
our $Opts = read_conf();

require 'database_www.pl';
require 'layout.pl';

use DBI;
require "database_www.pl";

require Mediawiki::API;

require CGI;

my $cgi;
if ( $Opts->{'use_fastcgi'} ) {
  require CGI::Fast;
  $cgi = new CGI::Fast;
} else { 
  $cgi = new CGI;
}

require CGI::Carp; 
CGI::Carp->import('fatalsToBrowser');

my %param = %{$cgi->Vars()};

print CGI::header(-type=>'text/html', -charset=>'utf-8');      

our $dbh = db_connect_rw($Opts);

my $msg = $Opts->{'msg-homepage'};
my $umsg = $Opts->{'server-url'} . "?action=edit&title=" . uri_escape($msg);
my $pretitle = "<div class=\"editfloat\"><a href=\"$umsg\">[edit]</a></div>";

layout_header("Assessment tools", undef, undef, $pretitle);

print get_cached_wiki_page($Opts->{'msg-homepage'}, $cgi->{'purge'});

layout_footer();
exit;

