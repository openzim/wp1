#!/usr/bin/perl

# table.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

CGI program to display table of assessment info for one project

=cut

use utf8;
use encoding 'utf8';

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

require 'tables_lib.pl';

my $timestamp = strftime("%Y-%m-%dT%H:%M:%SZ", gmtime(time()));

my $max_results = 500;

my $list_url = $Opts->{'list2-url'} 
 or die "No 'list2-url' specified in configuration.\n";

my $log_url = $Opts->{'log-url'} 
 or die "No 'list2-url' specified in configuration.\n";

########################

use DBI;
require "database_www.pl";
our $dbh = db_connect_rw($Opts);

require 'cache.pl';
my $cache_sep = "<!-- cache separator -->\n";

require 'tables_lib.pl';

########################

require CGI;
CGI::Carp->import('fatalsToBrowser');

my $cgi;
my $loop_counter;
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
  my %param = %{$cgi->Vars()};

  my $handle = select();
  binmode $handle, ":utf8";

  print CGI::header(-type=>'text/html', -charset=>'utf-8');      

  my $proj = $param{'project'} || $ARGV[0] || '';
  my $qual = $param{'quality'} || $ARGV[1] ||'(all)';
  my $imp = $param{'importance'} || $ARGV[2] || '(all)';
  my $sortorder = $param{'sort'} || $ARGV[3] || 'DESC';

  if ( $sortorder =~ /^ASC$/i ) { $sortorder = "ASC"; } 
  else { $sortorder = "DESC";}

  layout_header('List articles by size');
  my $projects = query_form($proj, $qual, $imp, $sortorder);

#  print "Project: '" . encode("utf8", $proj), " \n";

  if ( defined $proj && defined $projects->{$proj} ) {

    do_table($proj, $qual, $imp, $sortorder);

  }  

  $loop_counter++;
  layout_footer("Debug: PID $$ has handled $loop_counter requests");
  if ( $loop_counter >= $Opts->{'max-requests'} ) { exit; }
}


#################################

sub do_table { 
  my $proj = shift;
  my $qual = shift;
  my $imp = shift;
  my $dir = shift;

  if ( $dir =~ /^ASC/i ) { $dir = 'ASC'; } 
  else { $dir = 'DESC'; }

  my $query =  "SELECT r_namespace, r_article, page_len  FROM " 
              . db_table_prefix() . "ratings join enwiki_p.page"
              . " on r_namespace = page_namespace and r_article = page_title" 
              . " where r_project = ?";
  my @qargs;
  push @qargs, $proj;

  if ( $qual ne '(all)') { 
    $query .= " and r_quality = ?";
    push @qargs, $qual;
  }

  if ( $imp ne '(all)') { 
    $query .= " and r_importance = ?";
    push @qargs, $imp;
  }
    
  $query .= " order by page_len $dir limit $max_results";

  my $sth= $dbh->prepare($query);
  my $count = $sth->execute(@qargs);  

  my $html = "<table class=\"wikitable\">\n";
  $html .= "<tr><th>Article</th><th>Size (bytes)</th></tr>\n";

  my $i = 0;
  my $evenodd;
  my @r;
  while ( @r = $sth->fetchrow_array() ) { 
    $i++;
    if ( 0 == $i % 2 ) { $evenodd = "list-even"; } 
    else { $evenodd = "list-odd"; }    
    $r[1] = encode("utf8", $r[1]);
    $r[1] =~ s/_/ /g;



    $html .= "<tr class=\"$evenodd\"><td>" 
           . make_article_link($r[0], $r[1])
           . "</td><td class=\"resultnum\">" . $r[2] 
           . "</td></tr>\n";
  }
  $html .= "</table>\n";

  print "<div class=\"navbox\">\n";
  print_header_text($proj, $qual, $imp, $count);
  print "</div>\n<center>\n";
  print $html;
  print "\n";
  print "</center>\n";


}

#################################

sub query_form {

  my $projSelected = shift;
  my $qualSelected = shift;
  my $impSelected = shift;
  my $sortSelected = shift;

  $projSelected =  encode("utf8",$projSelected);

  my $projects = {};
  my @row;

  my $sth = $dbh->prepare("SELECT p_project FROM " . db_table_prefix() . "projects");
  $sth->execute();

  while ( @row = $sth->fetchrow_array ) { 
    $projects->{$row[0]} = 1;
  }

  print "<form>\n"; 
  print "<fieldset style=\"display: inline;\">\n";
  print "<legend>Generate table</legend>\n";
  print "<label for=\"project\">Project:</label>\n";
  print "<select name=\"project\" id=\"project\">\n";

  my $p;
  foreach $p ( sort { $a cmp $b} keys %$projects) { 
    $p = encode("utf8", $p);
    if ( $p eq $projSelected ) { 
      print "<option value=\"" . $p . "\" selected>" . $p ."</option>\n";
    } else {
      print "<option value=\"" . $p . "\">" . $p . "</option>\n";
    }
  }

  print "</select><br/>\n";

  my @Quality =  ('(all)','FA-Class','FL-Class','A-Class','GA-Class',
                  'B-Class','C-Class','Start-Class','Stub-Class',
                  'Unassessed-Class');

  print "<label for=\"quality\">Quality rating:</label>\n";
  print "<select name=\"quality\" id=\"quality\">\n";

  foreach $p ( @Quality ) { 
    if ( $p eq $qualSelected ) { 
      print "<option value=\"" . $p . "\" selected>" . $p ."</option>\n";
    } else {
      print "<option value=\"" . $p . "\">" . $p . "</option>\n";
    }
  }

  print "</select><br/>\n";

  my @Importance =  ('(all)', 'Top-Class', 'High-Class', 'Mid-Class', 
                     'Low-Class', 'Unassessed-Class');

  print "<label for=\"importance\">Importance rating:</label>\n";
  print "<select name=\"importance\" id=\"importance\">\n";

  foreach $p ( @Importance ) { 
    if ( $p eq $impSelected ) { 
      print "<option value=\"" . $p . "\" selected>" . $p ."</option>\n";
    } else {
      print "<option value=\"" . $p . "\">" . $p . "</option>\n";
    }
  }

  print "</select><br/>\n";

  print "<label for=\"importance\">Sort by:</label>\n";
  print "<select name=\"sort\" id=\"sort\">\n";

  my @Sorts = ( 'ASC', 'DESC');
  my %SortNames = ( 'ASC' => 'increasing size', 'DESC' => 'descreasing size');
  foreach $p ( @Sorts ) { 
    if ( $p eq $sortSelected ) { 
      print "<option value=\"" . $p . "\" selected>" . $SortNames{$p} ."</option>\n";
    } else {
      print "<option value=\"" . $p . "\">" . $SortNames{$p} . "</option>\n";
    }
  }
  print "</select><br/>\n";

  print "<input type=\"submit\" value=\"Make table\"/>\n";
  print "</fieldset></form>\n";
  print "\n";

  return $projects;
}

#####################################################################

sub print_header_text {
  my $project = shift;
  my $qual = shift;
  my $imp = shift;
  my $count = shift;

  my ($timestamp, $wikipage, $parent, $shortname);
 
  ($project, $timestamp, $wikipage, $parent, $shortname) = 
        get_project_data($project);

  $project = encode("utf8", $project);
  $wikipage = encode("utf8", $wikipage);

  my $listURL = $list_url;
  $listURL = $listURL . "?projecta=" . $project . "&limit=$max_results";
  
  my $logURL = $log_url;
  $logURL = $logURL . "?project=" . $project;

  if ( ! defined $wikipage)   {
    print  "Data for <b>$project</b>";
  }  elsif ( ! defined $shortname)   {
#    print `/usr/bin/hostname` . "<br>\n";
    print  "Data for <b>" . 
                        get_cached_link_from_api("[[$wikipage]]")
                    . "</b> ";	
  }  else  {
    print "Data for <b>" . 
                 get_cached_link_from_api("[[$wikipage|$shortname]]") . "</b> " ;    
  }

  print " &bull; Quality: $qual &bull; Importance: $imp";
  print " &bull; Showing $count results (max $max_results)\n";

}
