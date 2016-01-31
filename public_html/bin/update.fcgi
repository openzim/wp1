#!/usr/bin/perl

# update.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

CGI program to update data for a project

=cut

use strict;
use Encode;

require 'read_conf.pl';
our $Opts = read_conf();

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

my $list_url = $Opts->{'list2-url'} 
 or die "No 'list2-url' specified in configuration.\n";

my $log_url = $Opts->{'log-url'} 
 or die "No 'list2-url' specified in configuration.\n";

########################

use DBI;
require "database_www.pl";
our $dbh = db_connect_rw($Opts);

require 'cache.pl';
my $cache_sep = "<hr/><!-- cache separator -->\n";

########################

require CGI;
use CGI;
use CGI::Carp qw(warningsToBrowser fatalsToBrowser); 

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

  select STDOUT;
  $| = 1;
 
  $cgi->nph(1);

  my %param = %{$cgi->Vars()};

#print "A: '$ARGV[0]' \n";

  if ( defined $Opts->{'disable_web_update'} ) { 
    if ( ! defined $ARGV[0] ) { 
      layout_header('Updates temporarily disabled');
      print "<b>This tool has been temporarily disabled.</b><br/> Additional information: ";
      print $Opts->{'disable_web_update'};
      print "</body></html>";
      exit;
    }  
  }
### Log file
  my $p;
  my $logFile = "update." . time() . "." . $$;
  my $logEntry = $logFile;

  foreach $p ( keys %param ) { 
    $param{$p} =~ s/^\s*//;
    $param{$p} =~ s/\s*$//;
    $logEntry .= "&" . uri_escape($p) . "=" . uri_escape($param{$p});
  }

  if ( defined $Opts->{'log-dir'} 
       && -d $Opts->{'log-dir'} ) { 
    open LOG, ">", $Opts->{'log-dir'} . "/" . $logFile;
    print LOG $logEntry . "\n";
    close LOG;
  }


  print CGI::header(-type=>'text/html', -charset=>'utf-8');      

  my $proj = $param{'project'} || $ARGV[0] ;

  my $prog = $Opts->{'download-program'} || die "No program\n";

  if ( defined $proj ) { 
    layout_header("Updating project data for $proj");
    print << "HERE";
      <p class="updatewait" id="wait">
        Please wait for the data to be updated.</p>
      <p class="updatedone" id="done" style="display: none;">
        Data has been updated; you may now leave this page.</p>
    <hr/>
    <pre class="updatepre">
    Running $prog

HERE
#   $proj =~ s/'/\'/g;

#  print "Project before running: \"$proj\"<br/>\n";

    open PIPE, "-|", $prog, $proj or print "Error: $!<br/>\n";
    while ( <PIPE> ) { 
      print;
    }
    close PIPE;
  
    print "</pre>\n";
    print "<hr/>\n";
    print "<p class=\"updatedone\">Data has been updated; you may now leave this page.</p>\n";

print << "HERE";
<script type="text/javascript">
  document.getElementById("wait").style.display="none";
  document.getElementById("done").style.display="inline";
</script>
HERE

  } else { 
    layout_header('Update project data');
    input_html();
  }

  $loop_counter++;
  layout_footer("Debug: PID $$ has handled $loop_counter requests");

# XXX
  exit;

  if ( $loop_counter >= $Opts->{'max-requests'} ) { exit; }
}

############################################################

sub input_html { 

  my $sth = $dbh->prepare("SELECT p_project FROM " 
                     . db_table_prefix() . "projects");
  $sth->execute();
  my @row;
  my $projects = {};

  while ( @row = $sth->fetchrow_array ) { 
    $projects->{$row[0]} = 1;
  }

  print << "HERE";
  <p>WP 1.0 bot is ready to serve you. </p>
    <form>
      <fieldset class="inner">
        <legend>Update project</legend>
<select id="projectsel" name="projectselect" 
onchange="projectSelected();">
<option value="">Select a project or enter its name below</option>
HERE

  my $p;
  foreach $p ( sort { $a cmp $b} keys %$projects) { 
      print "<option value=\"" . $p . "\">" . $p . "</option>\n";
  }

  print << "HERE";

</select>
<hr/>
          Project to update: <input type="text" id="projectname" 
name="project" size="30"><br/>
          <input type="submit" value="Go">
      </fieldset>
    </form>
HERE
}

