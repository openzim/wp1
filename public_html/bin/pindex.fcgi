#!/usr/bin/perl

# pindex.fgci
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

CGI to display index of all projects

=cut

use strict;
use Encode;
use URI::Escape;
use Data::Dumper;

require 'read_conf.pl';
our $Opts = read_conf();

require 'database_www.pl';
require 'layout.pl';

use DBI;
require "database_www.pl";
our $dbh = db_connect_rw($Opts);

require Mediawiki::API;

require CGI;

require CGI::Carp; 
CGI::Carp->import('fatalsToBrowser');

require POSIX;
POSIX->import('strftime');

my $loop_counter = 0;

my $cgi;
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

  my $iletter = $param{'sec'} || $ARGV[0] || "";

  my $projects = db_get_project_details();
  my $table = sort_projects($projects);
  my $count;

  print CGI::header(-type=>'text/html', -charset=>'utf-8');      

  layout_header("Project index");

  if ( $iletter eq '[All]' ) { 
      $count = scalar keys %$projects;
      nav_box($iletter, $count, $table);
      letter_index($projects, $table, $iletter);
  } elsif ( defined $table->{$iletter} ) { 
      $count = scalar keys %{$table->{$iletter}};
      nav_box($iletter, $count, $table);
      letter_index($projects, $table, $iletter);
  } else { 
      $count = scalar keys %$projects;
      nav_box("", $count, $table);
  }            

  $loop_counter++;
  layout_footer("Debug: PID $$ has served $loop_counter requests");
  if ( $loop_counter > $Opts->{'max-requests'} ) { 
      exit;
  }
}

#####################################################################

sub nav_box { 
  my $iletter = shift;
  my $count = shift;
  my $table = shift;
  my $table2url = $Opts->{'table2-url'};

  print "<div class=\"navbox\">\n";

  print "There are <b>$count</b> participating projects";

  if ( ($iletter ne "" ) &&  ( $iletter ne '[All]' ) ) { 
      print " in section <b>$iletter</b>";
  } else { 
      print " overall";
  }

  print ".<br/>\n";

  if ( $iletter eq "" ) { 
      print "Please select a section of the index to view.<br/>\n";
  } else { 
    print " <b>Section:</b> ";
  }

  my $letter;
  foreach $letter ( sort {$a cmp $b} keys %$table ) {
    if ( $letter eq $iletter ) { 
       print   "<b><a href=\"" . $Opts->{'index-url'}  . "?sec=" 
        . uri_escape($letter) . "\">$letter</a></b> \n";
    } else { 
       print   "<a href=\"" . $Opts->{'index-url'}  . "?sec=" 
        . uri_escape($letter) . "\">$letter</a> \n";
    }
  }

  if ( $iletter eq '[All]') { 
    print "<b><a href=\"" . $Opts->{'index-url'}  
        . "?sec=[All]" . "\">[All]</a></b> \n";
  } else { 
     print "<a href=\"" . $Opts->{'index-url'} 
         . "?sec=[All]" . "\">[All]</a> \n";
  }

  print "</div>\n";
}

#####################################################################

sub letter_index { 
  my $projects = shift;
  my $table = shift;
  my $iletter = shift;

  my $letter;

  my $project_count = scalar keys %{$table->{$iletter}};

  print "<center><table class=\"wikitable\">\n";

  foreach $letter ( sort {$a cmp $b} keys %$table ){
    next if ( ($iletter ne "[All]") && ($letter ne $iletter));

    print << "HERE";
    <tr>
      <th colspan="5" style="text-align: center; padding-top: 1em;">
         &mdash;&nbsp;<B>$letter</B>&nbsp;&mdash;<a name="$letter"/>
      </th>
    </tr>
    <tr>
        <th>Project</th>
        <th>Articles</th>
        <th>Data</th>
        <th>Quality<br/>ratings</th>
        <th>Importance<br/>ratings</th>
   </tr>
HERE

    my $project;
    foreach $project ( sort {$a cmp $b} keys %{$table->{$letter}} ){
      project_index_link($project, $projects->{$project});
    }
    print "</td></tr>\n";
  }

  print "</table></center>\n";
}

#####################################################################

sub project_index_link { 
  my $project = shift;
  my $data = shift;

  my $listp = make_list_link({'projecta'=>$project});
  my $tablep = make_table_link($project);
  my $logp = make_log_link({'project'=>$project});
  my $catp = "/wiki/Category:" . uri_escape($project)
             . " articles by quality";
  
  my $name = $project;
  if ( defined $data->{'p_shortname'} ) { 
    $name = $data->{'p_shortname'};
  }

  $name =~ s/_/ /g;

  if ( defined $data->{'p_wikipage'} ) { 
    $name =  "<a href=\"http://en.wikipedia.org/w/index.php?title=" 
            . uri_escape($data->{'p_wikipage'}) . "\">$name</a>";
  }

  my $line =  "<tr><td><b>$name</b></td>"
            . "<td style=\"text-align: right;\">"  
            . commify($data->{'p_count'}) . "</td>" 
            . "<td>&nbsp;<a href=\"$tablep\">table</a>, "
            . "<a href=\"$listp\">list</a>, "
            . "<a href=\"$logp\">log</a>, "
            . "<a href=\"$catp\">cat</a>";
  $line .= "</td>";

  if ( $data->{'p_count'} != 0 ) { 
    $line .= "<td>";
    $line .= print_progress_bar(($data->{'p_qcount'} 
                / $data->{'p_count'}) * 100);
    $line .= "</td><td>";

    $line .= print_progress_bar(($data->{'p_icount'} 
                / $data->{'p_count'}) * 100);
    $line .= "</td>";
  }
  
  $line .= "</tr>\n";
  print $line;
}

#####################################################################

sub print_progress_bar {
  my $number = shift;

  # Special case: if none at all are assessed, that means the project
  # just doesn't do that sort of assessment (particularly with 
  # importance ratings)
  if ( $number == 0 ) { return "";}
    
  # Get the color of the bar
  my $color = get_bar_color($number);
  
  # Round down to nearest integer. We want 100% to mean "everything",
  # so that it is easy to distinguish "everything" from "not everything"
  my $rounded = int($number); 
  
  return << "HERE";
    <div class="progress_cell" style="">
    <div class="progress_bar" style="background:#$color; width:$rounded%;">
    <div class="progress_text" style="">$rounded&#160;%</div></div></div>
HERE
}

#####################################################################

sub sort_projects { 
  my $projects= shift;

  my $table = {};

  my ($p, $name, $letter);

  foreach $p ( keys %$projects ) {
    $name = $p;
    if ( defined $projects->{$p}->{'p_shortname'} ) { 
      $name = $projects->{$p}->{'p_shortname'};
    }

    # The following gets the first character of $name,
    # which may be a multibyte character in utf8
    $letter = substr(decode("utf8", $name), 0, 1) ;
    $letter = encode("utf8", $letter);

    if ( ! ( $letter =~ /[A-Z]/ ) ) { 
#      if ( $letter =~ /[0-9]/ ) { 
#        $letter = '0&ndash;9';
#      } else { 
        $letter = "[Other]";
#      }
    }

    if ( ! defined $table->{$letter} ) { 
      $table->{$letter} = {};
    }

    $table->{$letter}->{$p} =  $projects->{$p};
  }

  return $table;
}

#####################################################################

sub commify {
  # commify a number. Perl Cookbook, 2.17, p. 64
  my $text = reverse $_[0];
  $text =~ s/(\d\d\d)(?=\d)(?!\d*\.)/$1,/g;
  return scalar reverse $text;
}

#####################################################################
