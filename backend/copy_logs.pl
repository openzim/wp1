#!/usr/bin/perl

# copy_logs.pl
# Copy logs of project assessment changes to the wiki

# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

select STDOUT;
$| = 1;

use strict;

use Time::HiRes qw ( time  );

require 'read_conf.pl';
require 'database_www.pl';
require 'api_routines.pl';

use utf8;
use encoding 'utf8';

my $Opts = read_conf();

if ( ! defined $Opts->{'max-log-page-size'} ) { 
  die "Must define max-log-page-size in wp10.conf";
}
my $MaxLogPageSize = $Opts->{'max-log-page-size'};

my $NotAClass = $Opts->{'not-a-class'};

my $chunkMessageBottom = << "HERE";

This log entry was truncated because it was too long. The entry
continues in the previous revision of this log page.
HERE

my $chunkMessageTop = << "HERE";

This log entry was truncated because it was too long. This entry
is a continuation of the entry in the next revision of this log page.

HERE

my @Months = ('Null', 'January', 'February', 'March', 'April', 'May',
              'June', 'July', 'August', 'September', 'October',
              'November', 'December');

my %MonthsRev = ( 
   'January' => '01',
   'February' => '02',
   'March' => '03',
   'April' => '04',
   'May' => '05',
   'June' => '06',
   'July' => '07',
   'August' => '08',
   'September' => '09',
   'October' => '10',
   'November' => '11',
   'December' => '12'  );

###################################################3
use DBI;
our $dbh = db_connect_ro($Opts);
my $Namespaces = db_get_namespaces();

our $wiki_dbh = toolserver_connect($Opts);

use POSIX 'strftime';
use URI::Escape;

my $project = $ARGV[0];

# Instrumenting
my @i_latest;
my @i_log;
my @i_process;
my @i_moves;
my @i_edit;
my @i_revlink;
my @i_revids;
my @i_key;

if ( $project eq '--all' ) { 
  my $sth = $dbh->prepare("select p_project from " . db_table_prefix() . "projects");
  my @r;
  my $i;
  my $count = $sth->execute();
  
  while ( @r = $sth->fetchrow_array() ) { 
    $i++;
    if ( defined $ENV{'CLEAR'} ) { 
      system("clear");
    }
    print "\n--- $i / $count : $r[0] \n";
    instrument();
    do_project($r[0]);
  }
} else { 
  if ( $project eq '' ) { usage(); } 
  do_project($project);
}

instrument();

exit;

############################################################
############################################################


sub do_project { 
  my $project = shift;

  $dbh->disconnect(); # So if one project is killed by the query cleaner
                      # We can pick up with the next one. It's inefficient to 
                      # reconnect every time but I don't have a workaround yet
  $dbh = db_connect_ro($Opts);


  my $stime = time();
  my ($hist,$max)  = get_log_history($project);
  my $etime = time();
  push @i_latest, ($etime - $stime);

  my $timestamp = $max . "250000";  # to skip to next day

  if ( defined $ARGV[1]) { 
     $timestamp = $ARGV[1] . "250000";
  }

  print "Most recent log entry for $project: $max\n";

  $hist = {};
  get_ratings($project, $timestamp, $hist);

}
############################################################

sub get_ratings {
  my $project = shift;
  my $timestamp = shift;
  my $hist = shift;

  my ($p, $art, $ns, $key, $action, $log_ts, $old, $new, $rev_ts);

  my $project_db = $project;
#  $project_db =~ s/ /_/g;

  my $sth = $dbh->prepare("select p_timestamp from " . db_table_prefix() . "projects 
                             where p_project = ?");
  $_ = $sth->execute($project_db);

  if ($_ eq '0E0' ) { 
      die "I don't see a project named '$project_db'\n";
  }

  my $query = "
    SELECT * FROM " . db_table_prefix() . "logging 
    WHERE l_project = ?
      AND l_timestamp > ?";

  print "T: '$timestamp'\n";

  $sth = $dbh->prepare($query);

  my $stime = time();
  $sth->execute($project_db, $timestamp);
  my $etime = time();
  print "Fetched assessment logs for $project  in " . ($etime - $stime) 
          . " seconds\n"; 

  push @i_log, ($etime - $stime);
  my $r;
  my $dates = {};

  while ( $r = $sth->fetchrow_hashref() ) { 
    $key = substr($r->{l_timestamp}, 0, 8);

# Commented out 2012-11-17 
#   print "--\n". (Dumper($r)) . "\n";

    if ( ! exists $dates->{$key} ) { 
      $dates->{$key} = [];
    }
    push @{$dates->{$key}}, $r;
  }

  my $processed = {};
  my ($year, $month, $mname, $day);

  foreach $key ( sort {$a <=> $b } keys %$dates ) { 
    print "K '$key' size: " . scalar @{$dates->{$key}} . "\n";

    if ( defined $hist->{$key} ) { 
      print " already done\n";
      next;
    }

    if ( 100000 < scalar @{$dates->{$key}} ) { 
      $processed->{$key} = "The log for today is too huge to upload to the wiki.\n"
    } else {  
      $processed->{$key} = process_log($dates->{$key});
    }
 
    $key =~ /(....)(..)(..)/;
    $year = $1;
    $month = $2;
    $day = $3;

    $day =~ s/^0//;
    $month =~ s/^0//;
    $mname = $Months[$month];

    my $header = sprintf "=== %s %s, %s ===\n", 
                           $Months[$month], $day, $year;

    $processed->{$key} = $header . $processed->{$key};
    if ( defined $ENV{'DRY_RUN'} && (1 == $ENV{'DRY_RUN'}) ) { 
      print $processed->{$key}; 
      sleep 30;
    } else { 
      do_edit($project, $processed->{$key}, "$mname $day, $year");
      exit if ( defined $ENV{'DRY_RUN'} && (2 == $ENV{'DRY_RUN'}));
    
    }
  }
}

############################################################

sub process_log { 
  my $rawdata = shift;

  my ($r, $key);

  my $stime = time();

  my $move_to = {};
  my $move_from = {};
  my $reassess = {};
  my $no_qual = {};
  my $no_imp = {};

  my $errors = "";
  my $move_log = [];
  my $remove_log = [];
  my $reassess_log = [];
  my $assess_log = [];
  my $line;

  my $rawcount = scalar @$rawdata;

  foreach $r ( @$rawdata ) {
 
    $key = sprintf "%04d:%s", $r->{'l_namespace'}, $r->{'l_article'};

    if ( $r->{'l_action'} eq 'moved' ) {
      my $dkey = move_target($r->{'l_namespace'},
                             $r->{'l_article'},
                             $r->{'l_revision_timestamp'});

      $move_to->{$key} = $dkey;
      $move_from->{$dkey} = $key;
  
    } elsif ( $r->{'l_action'} eq 'importance' ) { 
      if ( ! defined $reassess->{$key} ) { 
        $reassess->{$key} = {};
      }

      $reassess->{$key}->{'imp_old'} = $r->{'l_old'};
      $reassess->{$key}->{'imp_new'} = $r->{'l_new'};
      $reassess->{$key}->{'imp_ts'} = $r->{'l_revision_timestamp'};

      if ( $r->{'l_new'} eq $NotAClass ) { 
        $no_imp->{$key} = 1;
      }    

    } elsif ( $r->{'l_action'} eq 'quality' ) { 

      if ( ! defined $reassess->{$key} ) { 
        $reassess->{$key} = {};
      }

      $reassess->{$key}->{'qual_old'} = $r->{'l_old'};
      $reassess->{$key}->{'qual_new'} = $r->{'l_new'};
      $reassess->{$key}->{'qual_ts'} = $r->{'l_revision_timestamp'};

      if ( $r->{'l_new'} eq $NotAClass ) { 
        $no_qual->{$key} = 1;
      }    

    } else { 
      $errors .= "" . Dumper($r) . "\n--\n";
    }
  }

  print "\n";

  foreach $key ( keys %$move_to ) { 
    $line =  "'''[[" . key_to_name($key)  . "]]'''" 
        . " renamed to " 
        . "'''[[" . key_to_name($move_to->{$key}) . "]]'''.";
    push @$move_log, $line;
  } 

  my ($okey, $imp_ok, $qual_ok, $name, $talk);
  my ($rev_page, $rev_talk, $reassessed);    

  my $z = 0;
  foreach $key ( sort {$a cmp $b} keys %$reassess ) { 
    $z++;
    if ( 0 == ($z % 50) ) { 
      print "   $z\n";
    }

    my $data = $reassess->{$key};

    # If both of these become 1, it means the article was just
    # moved, so the log entry for reassessing will be skipped
    $imp_ok = 0;
    $qual_ok = 0;

    # was this article moved somewhere else
    # without any change in ratings ? 
    if ( exists $move_to->{$key}  ) { 
      $okey = $move_to->{$key};
      if ( defined $reassess->{$okey} ) {

        if ($reassess->{$key}->{'imp_old'} 
            eq $reassess->{$okey}->{'imp_new'} ) {
              $imp_ok = 1;
        }
        if ($reassess->{$key}->{'qual_old'} 
            eq $reassess->{$okey}->{'qual_new'} ) {
              $qual_ok = 1;
        }
      }
    }

    # was this article moved from somewhere else
    # without any change in ratings ? 
    if ( exists $move_from->{$key}  ) { 
      $okey = $move_from->{$key};
      if ( defined $reassess->{$okey} ) {

        if ($reassess->{$key}->{'imp_new'} 
            eq $reassess->{$okey}->{'imp_old'} ) {
              $imp_ok = 1;
        }
        if ($reassess->{$key}->{'qual_new'} 
            eq $reassess->{$okey}->{'qual_old'} ) {
              $qual_ok = 1;
        }
      }
    }

    $name = key_to_name($key);
    $talk = key_to_talk($key);

    if ( (! $imp_ok) || (!$qual_ok) ) {   # this eliminates renamed articles

      if ( ((! defined $data->{'qual_old'}) 
             || ($data->{'qual_old'} eq $NotAClass ))  
          && ((! defined $data->{'imp_old'} ) 
              || ($data->{'imp_old'} eq $NotAClass ))) { 
          $reassessed = 'assessed';
  
      } elsif ( ((! defined $data->{'qual_new'}) 
              || ($data->{'qual_new'} eq $NotAClass ))  
          &&  ((! defined $data->{'imp_new'} ) 
              || ($data->{'imp_new'} eq $NotAClass ))) { 
        $reassessed = 'removed';
      } else { 
        $reassessed = 'reassessed';
      }

      $line = "'''[[$name]]''' ([[$talk|talk]]) $reassessed.";

      if ( $reassessed eq 'removed' ) {
        if ( defined $data->{'qual_old' } ) {
          ($rev_page, $rev_talk) = get_revid($key, $data->{'qual_ts'});
          $line .= " Quality rating was " 
                 . format_old_rating($data->{'qual_old'})
                 . " <span style=\"white-space: nowrap;\">(" 
                 . rev_link($key, $rev_page, "rev") 
                 . " &middot; " . rev_link($key, $rev_talk, "t") . ").</span>"
	}

        if ( defined $data->{'imp_old' } ) {
          ($rev_page, $rev_talk) = get_revid($key, $data->{'imp_ts'});
          $line .= " Importance rating was " 
                 . format_old_rating($data->{'imp_old'})
                 . " <span style=\"white-space: nowrap;\">(" 
                 . rev_link($key, $rev_page, "rev") 
                 . " &middot; " . rev_link($key, $rev_talk, "t") . ").</span>"
	}

      } else {  

        if ( defined $data->{'qual_old' } ) {
          ($rev_page, $rev_talk) = get_revid($key, $data->{'qual_ts'});

          if ( $data->{'qual_old'} eq $NotAClass ) { 
            $line .= " Quality assessed as ";
          } else { 
            $line .= " Quality rating changed from "
                  . format_old_rating($data->{'qual_old'}) 
                  . " to ";
          }

          $line .= format_new_rating($data->{'qual_new'})
                 . " <span style=\"white-space: nowrap;\">(" 
                 . rev_link($key, $rev_page, "rev") 
                 . " &middot; " . rev_link($key, $rev_talk, "t") . ").</span>"
        }

        if ( defined $data->{'imp_old'} ) { 
          ($rev_page, $rev_talk) = get_revid($key, $data->{'imp_ts'});

          if ( $data->{'imp_old'} eq $NotAClass ) { 
            $line .= " Importance assessed as ";
          } else { 
            $line .= " Importance rating changed from "
                  . format_old_rating($data->{'imp_old'} )
                  . " to ";
          }
          $line .=  format_new_rating($data->{'imp_new'} )
                  . " <span style=\"white-space: nowrap;\">(" 
                  . rev_link($key, $rev_page, "rev") 
                  . " &middot; " . rev_link($key, $rev_talk, "t") 
                  . ").</span>"
        }   
      }
      if ( $reassessed eq 'reassessed') { 
        push @$reassess_log, $line;
      } elsif ( $reassessed eq 'removed') { 
	  if ( ! defined $move_to->{$key} ) {
	      # if the ratings are changed when the page is moved,
	      # the tests above don't notice the move. So force
	      # if not to display here
            push @$remove_log, $line;
	  }
      } else { 
        push @$assess_log, $line;    
      }
    }
  }

#  print "\n";
    
  my $output;
  
  if ( 0 < scalar @$move_log ) { 
    $output .= "==== Renamed ====\n";
    foreach $line ( @$move_log ) { 
      $output .= "* $line\n";
    }
  }

  if ( 0 < scalar @$reassess_log ) { 
    $output .= "==== Reassessed ====\n";
    foreach $line ( @$reassess_log ) { 
      $output .= "* $line\n";
    }
  }

  if ( 0 < scalar @$assess_log ) { 
    $output .= "==== Assessed ====\n";
    foreach $line ( @$assess_log ) { 
      $output .= "* $line\n";
    }
  }

  if ( 0 < scalar @$remove_log ) { 
    $output .= "==== Removed ====\n";
    foreach $line ( @$remove_log ) { 
      $output .= "* $line\n";
    }
  }

  my $etime = time();
  push @i_process, ($etime - $stime);

  print "::: Processed $rawcount in " . ($etime - $stime) . "\n";

  return $output;
}

############################################################

sub move_target {
  my $ns = shift;
  my $art = shift;
  my $ts = shift;

  my $stime = time();

  my $sth = $dbh->prepare("select m_new_namespace, m_new_article
                           from " . db_table_prefix() . "moves
                           where m_old_namespace = ? 
                             and m_old_article = ? 
                             and m_timestamp = ?");

  $sth->execute($ns, $art, $ts);

  my $etime = time();
  push @i_moves, ($etime - $stime);

  my @r = $sth->fetchrow_array();
  return $r[0] . ":" . $r[1];
}

############################################################

sub key_to_name { 
  my $key = shift;
  my ($ns, $title) = split /:/, $key, 2;

  push @i_key, 0;

  $ns =~ s/^0*(\d)/$1/;

  $title =~ s/_/ /g;

  if ( $ns == 0 ) { 
    return $title; 
  } else { 
    return ":" . $Namespaces->{$ns} . ":" . $title;
  }
}

sub key_to_talk { 
  my $key = shift;
  my ($ns, $title) = split /:/, $key, 2;

  $ns =~ s/^0*(\d)/$1/;

#  print "\nNS pre: '$ns' " . $Namespaces->{$ns} . "\n";
  $ns++;

#  print "\nNS post: '$ns' " . $Namespaces->{$ns} . "\n";

  return $Namespaces->{$ns} . ":" . $title;
}

############################################################

sub get_revid { 
  my $key = shift;
  my $timestamp = shift;
  $timestamp =~ s/[^0-9]//g;

  my $stime = time();

  my ($ns, $page) = split /:/, $key, 2;
  $page =~ s/ /_/g;

  my $query = 'select rev_id 
               from enwiki_p.revision join enwiki_p.page 
               on page_namespace = ? and page_title = ? 
               and rev_page = page_id 
               where rev_timestamp <= ? 
               order by rev_timestamp desc limit 1';

  my $sth = $wiki_dbh->prepare($query);

  my ($rev_page, $rev_talk);
  my @r;

  $sth->execute($ns, $page, $timestamp);

  @r = $sth->fetchrow_array();
  $rev_page = $r[0];

  $sth->execute($ns+1, $page, $timestamp);
  @r = $sth->fetchrow_array();
  $rev_talk = $r[0];


  my $etime = time();
  push @i_revids, ($etime -$stime);

  $sth->finish();
  return ($rev_page, $rev_talk);
}

############################################################

sub rev_link { 
  my $key = shift;
  my $revid = shift;
  my $title = shift;

  my $stime = time();

  my $name = key_to_name($key);

  my $link = $Opts->{'server-url'} 
                       . "?title=" . uri_escape_utf8($name) 
                       . "&oldid=$revid";

  my $etime = time();
  push @i_revlink, ($etime - $stime);

  return "[$link $title]";
}

############################################################

sub do_edit { 
  my $project = shift;
  my $newtext = shift;
  my $date = shift;
 
  my $stime = time();

  my $page = log_page($project);

  # parse old content into @sections
  my $content = api_content($page);
  my @sections;
  $sections[0] = "";
  my $sn = 0;
  my @lines = split /\n/, $content;
  my $l;
  foreach $l ( @lines ) { 
#      print "See: $l\n";

    if ( $l =~ /^===[^=]/ ) { 
      $sn++;
      $sections[$sn] = "";
    }
    $sections[$sn] .= $l . "\n";
  }
  $sections[$sn] =~ s/\n+$/\n/;

#  for ( $sn = 0; $sn < scalar @sections; $sn++ ) { 
#      print "Sec $sn: " . (length $sections[$sn] ) . "\n";
#  } 

  $newtext = $sections[0] . $newtext;

  my $revision = $Opts->{'svn-revision'};
  my $edit_summary = "Log for $date (2G r$revision)";

  # If the new content is to big, we will split it. 
  # Otherwise, keep as much of the old stuff as possible

  if ( $MaxLogPageSize < length $newtext ) { 
    print "Need to split new text\n";
    my @chunks;
    my $cn = 0;
    $chunks[0] = "";

    @lines = split /\n/, $newtext;
    foreach $l ( @lines ) { 
      if ( $MaxLogPageSize < length $chunks[$cn] ) { 
        $chunks[$cn] .= $chunkMessageBottom;
        $cn++;
        $chunks[$cn] = $chunkMessageTop;
      }
      $chunks[$cn] .= $l . "\n";
    }
    $chunks[$cn] =~ s/\n+$/\n/;

    my $count = scalar @chunks;
    my $m;
    $cn = $count - 1;
    while ( $cn >= 0 ) { 
      $m = " [chunk " . ($cn+1) . " of $count]";
      print " .. $m\n";
      api_edit($page, $chunks[$cn], $edit_summary . $m );
      $cn--;
   }

  } else { 
    print "Don't need to split new text\n";
    $sn = 1;

    while ( $sn < (scalar @sections) ) { 
#      print "Check section $sn\n";
#      print " Text: " . (length $newtext) . "\n";
#      print " Section $sn: " . (length $sections[$sn]) . "\n";
      last if ( $MaxLogPageSize <
                  ((length $newtext) + (length $sections[$sn])) ) ;
      $newtext .= $sections[$sn];
      $sn++;
    }
#    print "Final length: " . (length $newtext) . "\n\n";

    api_edit($page, $newtext, $edit_summary);
  }

  my $etime = time();
  push @i_edit, ($etime - $stime);
}

############################################################

sub log_page { 
  my $project = shift;
  my $type = shift;

  my $title = "Version 1.0 Editorial Team/"
      . $project . " articles by quality log";

  if ( ! defined $type ) { 
    return "Wikipedia:$title";
  } elsif ( $type = "db" ) { 
      $title =~ s/ /_/g;
      return (4,$title);
  }
}

############################################################

sub get_log_history { 
  my $project = shift;
  my ($ns, $page) = log_page($project, 'db');

  my $query = "select rev_comment 
               from enwiki_p.revision 
               join enwiki_p.page on page_id = rev_page
               where page_namespace = ? and page_title = ?
               order by rev_timestamp desc limit 250";

  my $sth = $wiki_dbh->prepare($query);
  $sth->execute($ns, $page);

  my $hist = {};

  my @r;
  my ($year, $mname, $month, $day, $key);
  my $max = 0;
  while ( @r = $sth->fetchrow_array ) { 
    if ( $r[0] =~ /Log for (.*) (\d+), (\d+)/ ) { 
      $mname = $1;
      $day = $2;
      $year = $3;
      if ( defined $MonthsRev{$mname} ) { 
        $key = sprintf("%d%02d%02d",  $year , $MonthsRev{$mname}, $day);
        $hist->{$key} = 1;
        if ( $key > $max ) { 
	    $max = $key;
        }
      }
    }
  }

  $sth->finish();
  return ($hist, $max);
}

############################################################

sub format_old_rating { 
  my $text = shift;
  return "'''$text'''";
}

sub format_new_rating { 
  my $text = shift;
  return "'''$text'''";
}


############################################################


sub usage { 
  print << "HERE";
Usage:

* Copy logs for a single project

  $0 [PROJECT] [TIMESTAMP]

If TIMESTAMP is specified, only logs newer than that are uploaded

* Copy logs for all projects

  $0 --all


HERE
exit;

}

############################################################

sub instrument { 
   i_total("latest edit", \@i_latest);
   i_total("fetching logs", \@i_log);
   i_total("processing logs", \@i_process);
   i_total("move logs (inside process logs)", \@i_moves);
   i_total("rev links (inside process logs)", \@i_revlink);
   i_total("rev ids", \@i_revids);
   i_total("edits", \@i_edit);
   i_total("key to name (count only)", \@i_key);

}


sub i_total { 
  my $caption = shift;
  my $data = shift;
  my $count = scalar @$data;
  my $total = 0;
  foreach $_ ( @$data ) { 
    $total += $_;
  }

  print "I: $caption : $count in $total sec\n";
}
