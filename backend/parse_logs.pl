#!/usr/bin/perl

# parse_logs.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information


binmode STDOUT, ":utf8";

use strict;
use lib '/home/project/e/n/w/enwp10/VeblenBot';
use Date::Parse;
use POSIX 'strftime';

use Mediawiki::API;
my $api = new Mediawiki::API;
$api->base_url('http://en.wikipedia.org/w/api.php');
$api->debug_level(3);
$api->maxlag(2000);
$api->login_from_file('/home/project/e/n/w/enwp10/api.credentials.wp10');

use Data::Dumper;

my $project = $ARGV[0] || 'Mathematics';

my $ptmp = $project;
$ptmp =~ s/ /_/g;
$ptmp =~ s/\//./g;

open LOG, ">Logs/$ptmp";
binmode LOG, ":utf8";
print "open Logs/$ptmp\n";

my $query = [ 'action' => 'query',
              'prop'   => 'revisions',
              'titles' => "Wikipedia:Version_1.0_Editorial_Team/" 
                          . $project . "_articles_by_quality_log",
              'rvprop' => 'user|timestamp|content',
              'rvdir' => 'older', 
              'rvlimit' => '25',
              'format' => 'xml' ];

my $timestamp =  '2008-12-30T10:00:00Z';

my $continue = 1;

my $log = {};
 
while ($continue ) { 

  print "T: $timestamp\n";
#  sleep 1;

  my $res = $api->makeXMLrequest([ @$query, 
                               'rvstart', $timestamp], ['rev']);

  $res = $res->{'query'}->{'pages'}->{'page'}->{'revisions'}->{'rev'};

  my $rev;
  foreach $rev ( @$res ) { 
    $timestamp = $rev->{'timestamp'};
    print "T: " . $rev->{'timestamp'} . "\n";
    handle_content($rev->{'content'}, $log);   
    print "\n\n";
  }

  print "--\n $timestamp\n";
  sleep 2;

  last if ( 2 > scalar @$res );

}

exit;

#########################################################################


sub handle_content { 
  my $content = shift;
  my $data = shift;

  my @lines = split /\n/, $content;
  my ($line, $page, $old_value, $new_value, $action, $qual,
      $imp, $oqual, $oimp, $new, $date);

  foreach $line ( @lines) { 
#    print "@ '$line' \n";
    print ".";

    $line =~ s/No-Class/NotA-Class/g;

    if ( $line =~ /^===(.*)===$/ ) {
      $date = $1;
      $date =~ s/[[\]]//g;
      $date = strftime("%Y-%m-%dT%H:%M:%SZ", gmtime(str2time($date, 'UTC0')));
      print "\n\t$date";
    } elsif ( $line =~ /^==\[\[(.*)]], \[\[(\d\d\d\d)]]==$/ ) {
      $date = $1 . " " . $2;
      $date =~ s/[[\]]//g;
      $date = strftime("%Y%m%d%H%M%S", gmtime(str2time($date, 'UTC0')));
      print "\n\t$date";
#      print "\nDATE EXCEPTION 1\n";
#      sleep 3;
 
    } elsif ( $line =~ /noinclude/ ) { 
      next;
    } elsif ( $line =~ /\{\{Log\}\}/ ) {
      next;

    } elsif ( $line =~ /\*.*\[\[[^]]*]].*(added)|(removed)/ ) { 
      if ( $line =~ /\[\[([^]]*)]] \(\[\[Talk:.*\|talk]]\) ([A-Za-z-]*) \(([A-Za-z-]*)\) (\w+)/ ) { 
        $page = $1;
        $qual = $2;
        $imp = $3;
        $action = $4;
        print LOG "$date| $project| $action| $page| $qual| $imp\n";
      } elsif ( $line =~ /\[\[([^]]*)]] \(\[\[Talk:.*\|talk]]\) added, as ([A-Za-z-]*) \(([A-Za-z-]*)\)/ ) { 
        $page = $1;
        $qual = $2;
        $imp = $3;
        $action = 'added';
        print LOG "$date| $project| $action| $page| $qual| $imp\n";
#        print  "$date| $project| $action| $page| $qual| $imp\n";
#        print "\t$line\n";
#        print "EXCEPTION 1\n";
#        sleep 1;

      } elsif ( $line =~ /\[\[([^]]*)]] \(\[\[Talk:.*\|talk]]\) added/ ) { 
        $page = $1;
        $qual = '-';
        $imp = '-';
        $action = 'added';
        print LOG "$date| $project| $action| $page| $qual| $imp\n";
#        print  "$date| $project| $action| $page| $qual| $imp\n";
#        print "\t$line\n";
#        print "EXCEPTION 1b\n";
#        sleep 1;
      } elsif ( $line =~ /\[\[([^]]*)]] \(\[\[Talk:.*\|talk]]\) removed, was in ([A-Za-z-]*)/ ) { 
        $page = $1;
        $qual = $2;
        $imp = '-';
        $action = 'removed';
        print LOG "$date| $project| $action| $page| $qual| $imp\n";
#        print  "\n$date| $project| $action| $page| $qual| $imp\n";
#        print "\t$line\n";
#        print "EXCEPTION 1d\n";
#        sleep 1;
      } elsif ( $line =~ /\[\[([^]]*)]] \(\[\[Talk:.*\|talk]]\)removed/ ) { 
        $page = $1;
        $qual = '-';
        $imp = '-';
        $action = 'removed';
        print LOG "$date| $project| $action| $page| $qual| $imp\n";
#        print  "\n$date| $project| $action| $page| $qual| $imp\n";
#        print "\t$line\n";
#        print "EXCEPTION 1e\n";
#        sleep 1;
     } else { 
       print "\t$line\n";
       print "\tERROR 1\n";
       sleep 5;
     }


    } elsif ( $line =~ /\*.*renamed to/ ) { 
      if ( $line =~ /\[\[([^]]*)]] \(\[\[Talk:.*\|talk]]\) ([A-Za-z-]*) \(([A-Za-z-]*)\) renamed to \[\[([^]]*)]]/ ) { 
        $page = $1;
        $qual = $2;
        $imp = $3;
        $action = 'renamed';
        $new_value = $4;
        print LOG "$date| $project| $action| $page| $qual| $imp| $new_value\n";
      } elsif ( $line =~ /\[\[([^]]*)]] \(\[\[Talk:.*\|talk]]\) renamed to \[\[([^]]*)]]/ ) { 
        $page = $1;
        $qual = "-";
        $imp = "-";
        $action = 'renamed';
        $new_value = $2;
        print LOG "$date| $project| $action| $page| $qual| $imp| $new_value\n";
#        print "\n$date| $project| $action| $page| $qual| $imp| $new_value\n";
#        print "\t$line\n";
#        print "EXCEPTION 3\n";
#        sleep 1;
      } else { 
        print "\t$line\n";
        print "\tERROR 2\n";
        sleep 5;
      }


    } elsif ( $line =~ /\*.*moved to/ ) { 
      if ( $line =~ /\[\[([^]]*)]] \(\[\[Talk:.*\|talk]]\) moved to \[\[([^]]*)]]/ ) {
        $page = $1;
        $qual = '-';
        $imp = '-';
        $action = 'renamed';
        $new_value = $2;
        print LOG "$date| $project| $action| $page| $qual| $imp| $new_value\n";
#        print  "\n$date| $project| $action| $page| $qual| $imp| $new_value\n";
#        print "\t$line\n";
#        print "EXCEPTION 6\n";
#        sleep 1;
      } else { 
        print "\t$line\n";
        print "\tERROR 6\n";
        sleep 5;
      }

    } elsif ( $line =~ /\*.*reassessed from/ ) { 
      if ( $line =~ /\[\[([^]]*)]] reassessed from ([A-Za-z-]*) \(([A-Za-z-]*)\) to ([A-Za-z-]*) \(([A-Za-z-]*)\)/ ) {
        $page = $1;
        $qual = $2;
        $imp = $3;
        $action = 'reassessed';
        $oqual = $4;
        $oimp = $5;
        print LOG "$date| $project| $action| $page| $qual| $imp| $oqual| $oimp\n";
      } else { 
        print "\t$line\n";
        print "\tERROR 3\n";
        sleep 5;
      }


    } elsif ( $line =~ /\*.*moved from/ ) { 
      if ( $line =~ /\[\[([^]]*)]] moved from ([A-Za-z-]*) \(([A-Za-z-]*)\) to ([A-Za-z-]*) \(([A-Za-z-]*)\)/ ) {
        $page = $1;
        $qual = $2;
        $imp = $3;
        $action = 'reassessed';
        $oqual = $4;
        $oimp = $5;
        print LOG "$date| $project| $action| $page| $qual| $imp| $oqual| $oimp\n";
#        print  "\n$date| $project| $action| $page| $qual| $imp| $oqual| $oimp\n";
#        print "\t$line\n";
#        print "EXCEPTION 2\n";
#        sleep 1;
      } elsif ( $line =~ /\[\[([^]]*)]] \(\[\[Talk:.*\|talk]]\) moved from ([A-Za-z-]*) \(([A-Za-z-]*)\) to ([A-Za-z-]*) \(([A-Za-z-]*)\)/ ) {
        $page = $1;
        $qual = $2;
        $imp = $3;
        $action = 'reassessed';
        $oqual = $4;
        $oimp = $5;
        print LOG "$date| $project| $action| $page| $qual| $imp| $oqual| $oimp\n";
#        print  "\n$date| $project| $action| $page| $qual| $imp| $oqual| $oimp\n";
#        print "\t$line\n";
#        print "EXCEPTION 3b\n";
#        sleep 1;
      } elsif ( $line =~ /\[\[([^]]*)]] moved from ([A-Za-z-]*) to ([A-Za-z-]*)/ ) {
        $page = $1;
        $qual = $2;
        $imp = '-';
        $action = 'reassessed';
        $oqual = $3;
        $oimp = '-';
        print LOG "$date| $project| $action| $page| $qual| $imp| $oqual| $oimp\n";
#        print  "\n$date| $project| $action| $page| $qual| $imp| $oqual| $oimp\n";
#        print "\t$line\n";
#        print "EXCEPTION 3c\n";
#        sleep 1;
      } else { 
        print "\t$line\n";
        print "\tERROR 3b\n";
        sleep 5;
      }

    } elsif ( $line =~ /\(No changes today\)/ ) { 
      next;
    } elsif ( $line =~ /Log truncated as it is too huge!/ ) { 
      next;
    } elsif ( $line =~ /^\s*$/ ) { 
      next;

    } else { 
       print "\n\t'$line'\n";
       print "\tERROR 4\n";
       sleep 5;
    }

  }


}
