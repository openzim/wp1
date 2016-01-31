#!/usr/bin/perl
use Encode;
use Data::Dumper;

use utf8;
use encoding 'utf8';

require 'read_conf.pl';
our $Opts = read_conf(); # Also initializes library paths

require 'database_routines.pl';
require 'wp10_routines.pl';
require 'api_routines.pl';

my $count = `wc -l $ARGV[0]`;
$count =~ s/ .*//;

open IN, "<", $ARGV[0];
$c = 0;

while ( $page = <IN> ) { 
$c++;
print "--- $c / $count\n";

  chomp $page;
  $page = "Talk:$page";
  print "P: $page\n";

  do_categories($page);

  my $t = api_content($page);
#  print $t;
  print "\n--\n";
  api_edit($page, $t, "null edit");

  do_categories($page);

 if ( ! defined $ENV{'AUTO'} ) {
    print "-- press enter\n";
    $next = <STDIN>;
  } else { 
    sleep 2;
  }
}



sub do_categories { 

  my $p = shift;
  my $client = get_api_object();

  my $r =  $client->makeXMLrequest(['action'=>'query',
                                    'prop'=>'categories',
                                    'titles'=>$p,
                                    'format'=>'xml']);

  print 
    Dumper($r->{'query'}->{'pages'}->{'page'}->{'categories'}->{'cl'});

}
