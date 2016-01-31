#!/usr/bin/perl

# layout.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

Routines for the CGI programs re page layout and link formatting

=over

=cut

use strict;
use POSIX 'strftime';


our $Opts;
my $App = $Opts->{'appname'}
    or die "Error: must specify application name. Did you run this from the command line?\n";

my $Version = $Opts->{'version'}
    or die "Must specify version\n";

my $indexURL = $Opts->{'index-url'};
my $table2URL = $Opts->{'table2-url'};
my $tableURL = $Opts->{'table-url'};
my $logURL = $Opts->{'log-url'};
my $listURL = $Opts->{'list2-url'};
my $manualURL = $Opts->{'manual-url'};
my $versionURL = $Opts->{'version-url'};
my $serverURL = $Opts->{'server-url'};
my $baseURL = $Opts->{'base-url'};
my $updateURL = $Opts->{'update-url'};

my $namespaceIDs;

use DBI;
require "database_www.pl";
our $dbh = db_connect_rw($Opts);
require 'cache.pl';

my $cacheMem = {};

require Mediawiki::API;
my $api = new Mediawiki::API;
$api->debug_level(0); # no output at all 
$api->base_url($Opts->{'api-url'});

##################################################

=item B<layout_header>(TITLE, SUBHEAD, LONGTITLE, PRETITLE)

Print to STDOUT the top part of the page HTML 

=over

=item TITLE 

the title of the program running. 

=item SUBHEAD 

HTML for the second bar (light blue) on the page

=item LONGTITLE 

A longer form of the title to display as a headline

=item PRETITLE

HTML that is put in the main content area before the first headline

=back

=cut

sub layout_header {
  my $title = shift;
  my $subhead = shift || '&nbsp;';
  my $longtitle = shift;
  my $pretitle = shift || '';

  my $realtitle = $title;
  if ( defined $longtitle) { $realtitle = $longtitle; }

  my $stylesheet = $Opts->{'wp10.css'}
    or die "Must specify configuration value for 'wp10.css'\n";

  my $usableforms = $Opts->{'usableforms.js'}
    or die "Must specify configuration value for 'usableforms.js'\n";

  my $wpjavascript = $Opts->{'wp10.js'}
    or die "Must specify configuration value for 'wp10.js'\n";
  
  my $basehref = $Opts->{'base-url'} || "";
  my $toolserverurl = $Opts->{'toolserver-home-url'} || "";
  my $toolserverbutton = $Opts->{'toolserver-button-url'} || "";
  my $homepage = $Opts->{'homepage'} || "";

  print << "HERE";
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" dir="ltr">
<head>
  <base href="$basehref">
  <title>$title - $App</title>
  <style type="text/css" media="screen">
     \@import "$stylesheet";
  </style>
<script type="text/javascript"  src="$usableforms"></script>
<script type="text/javascript"  src="$wpjavascript"></script>
</head>
<body>

<div id="container">
    <div class="tsbutton">
       <div class="tsbuttoninner">
         <a href="$toolserverurl">
           <img id="poweredbyicon" alt="Hosted by Wikimedia Labs"
                src="$toolserverbutton" />
<span class="hide">Hosted by Wikimedia Labs</span>
        </a>
      </div>
    </div>

  <div id="head">
    <h1><a href="$homepage">$App</a></h1>
  </div>

  <div id="subhead">
  $subhead
  </div>

<div class="clear"> </div>

</div>
HERE

  layout_leftnav($title);

  print << "HERE";
</div>
<div id="content">
$pretitle
<h2>$realtitle</h2>
HERE

}

#######################################################################
# Internal: write the left-side navbox for layout_header

sub layout_leftnav { 
  my $title = shift;

  my @AssessmentData = (
     "Project index" =>          $indexURL,
     "Overall summary table" =>  $table2URL,
     "Project summary tables" => $tableURL,
     "Article lists" =>          $listURL,
     "Assessment logs" =>        $logURL
#     "Update project data" =>    $updateURL
    );


  my @ManualSelection = (
     "List manual selection" => $manualURL . "?mode=list",
     "Add articles" =>          $manualURL . "?mode=add",
     "Changelog" =>             $manualURL . "?mode=logs",
     "Log in" =>                $manualURL . "?mode=login"
    );

  my @Interaction = ( 
    "Guide " => $Opts->{'guide-url'},
    "FAQ " => $Opts->{'faq-url'},
    "Discussion & bug reports " =>  $Opts->{'discussion-page'}
  );

  print << "HERE";
<div id="leftnav">
<h5 class="menu1 menu1start">Assessment data</h5>
HERE

  nav_list($title, \@AssessmentData);


  print << "HERE";
<h5 class="menu1 later">Manual selection</h5>
HERE

  nav_list($title, \@ManualSelection);


  print << "HERE";
<h5 class="menu1 later">Interaction</h5>
HERE

  nav_list($title, \@Interaction);


}
#######################################################################

# internal: format a navigation list in the navbox

sub nav_list { 
  my $title = shift;
  my $items = shift;

  print "<ul>\n";

  my ($i, $j, $selected);
  $i = 0;
  while ( $i < scalar @{$items} ) { 
    $j = $i + 1;
    $selected = "";
    if ( $title eq $items->[$i] ) { 
      $selected = "selected";
    }

    print "<li class=\"$selected\">" 
          . "<a href=\"" . $items->[$j] . "\">"
         . $items->[$i] . "</a></li>\n";

    $i += 2;
  }

  print "</ul>\n";

}

#######################################################################

=item B<layout_header>(TITLE, SUBHEAD, LONGTITLE)

Print to STDOUT bottom top part of the page HTML 

=cut

sub layout_footer {
  my $debug = shift;

  my $version = $Opts->{'version'};
  my $discussionPage = $Opts->{'discussion-page'} 
     || die "Must specify discussion-page in configuration file\n";
  my $bugPage = $Opts->{'bug-page'} 
     || die "Must specify bug-page in configuration file\n";

  print << "HERE";
</div>
<div id="footerbar">&nbsp;</div>

<div id="footer">
This is the web interface of the WP 1.0 bot 
&middot <a href="$discussionPage">Discussion page</a> 
&middot; <a href="$bugPage">Bug reports</a><br/>
<div class="version">
Current version: $Version<br/>
New schema branch<br/>
$debug
</div>
HERE

# system "ssh", "login.toolserver.org", "/home/cbm/wp10.2g/alpha/revinfo.pl";

  print << "HERE";
</div>
</body>
</html>
HERE

}

#######################################################################
# Generates colors for the progress bar. The two endpoints are
# 0%: #D10000 = (209, 0, 0) and 100%: 33CC00 = (51, 204, 0).
# There's probably a more efficient way of doing this...
sub get_bar_color {  
  my $percent = shift; 
  my $color;
  
  if ($percent >= 0) { $color='D10000' }
  if ($percent >= 2.5) { $color='F10000' }
  if ($percent >= 7.5) { $color='FF1600' }
  if ($percent >= 12.5) { $color='FF3700' }
  if ($percent >= 17.5) { $color='FF6500' }
  if ($percent >= 22.5) { $color='FF8F00' }
  if ($percent >= 27.5) { $color='FFB900' }
  if ($percent >= 32.5) { $color='FFD800' }
  if ($percent >= 37.5) { $color='FFE500' }
  if ($percent >= 42.5) { $color='FFF600' }
  if ($percent >= 47.5) { $color='FCFF00' }
  if ($percent >= 52.5) { $color='D3FF00' }
  if ($percent >= 57.5) { $color='D3FF00' }
  if ($percent >= 62.5) { $color='BEFF00' }
  if ($percent >= 67.5) { $color='92FF00' }
  if ($percent >= 72.5) { $color='99FF00' }
  if ($percent >= 77.5) { $color='39FF00' }
  if ($percent >= 82.5) { $color='0BFF00' }
  if ($percent >= 87.5) { $color='16E900' }
  if ($percent >= 92.5) { $color='33CC00' }
  if ($percent >= 97.5) { $color='33CC00' }
  if ($percent > 100) { $color='000000' }
  return $color;
}

#######################################################################
# Rounding function 
sub round {
  my $n = shift;
    return int($n + .5);
}

#######################################################################

=item B<make_table_link>(PROJECT)

Make the URL to link to the project table for PROJECT

=cut

sub make_table_link {
  my $project = shift;
  return $tableURL . "?project=" . uri_escape($project,  "^A-Za-z" );
}

#######################################################################

=item B<make_list_link>(ARGS)

Make the URL to link to the article list. ARGS is a hash
of KEY => VALUE pairs to be sent as arguments the list program

=cut

sub make_list_link { 
  my $opts = shift;
  my @encoded;

  my $key;
  foreach $key ( sort keys %$opts ) { 
    push @encoded, $key . "=" . uri_escape($opts->{$key});
  }
  
  return $listURL . "?" . (join "&", @encoded);
}

#######################################################################

=item B<make_log_link>(ARGS)

Make the URL to link to the article list. ARGS is a hash
of KEY => VALUE pairs to be sent as arguments the list program

=cut

sub make_log_link { 
  my $opts = shift;
  my @encoded;

  my $key;
  foreach $key ( sort keys %$opts ) { 
    push @encoded, $key . "=" . uri_escape($opts->{$key});
  }
  
  return $logURL . "?" . (join "&", @encoded);
}

#######################################################################

=item B<make_article_link>(NS, PAGE)

Make HTML for links to wiki pages about NS:PAGE

=cut

sub make_article_link {

  my $ns = shift;
  my $a = shift;
  my $pagename = make_page_name($ns, $a);
  my $talkname = make_talk_name($ns, $a);

  my $loguri = $logURL;

  return "<a href=\"$serverURL?title=" . uri_escape($pagename,  "^A-Za-z" )
       . "\">$pagename</a>"
         . " (<a href=\"$serverURL?title=" . uri_escape($talkname, "^A-Za-z" )
         . "\">t</a>"
         . " &middot; "
         . "<a href=\"$serverURL?title=" . uri_escape($pagename,  "^A-Za-z" )
         . "&action=history\">h</a>"
         . " &middot; "
         . "<a href=\"$logURL?pagename=" . uri_escape($a,  "^A-Za-z"  )
         . "&ns=" . uri_escape($ns)
         . "\">l</a>)";
}

###########################################################################

=item B<make_history_link>(NS, PAGE, TIMESTAMP, LONG, TALKLINK)

Make the URL to link to the revision of NS:PAGE at TIMESTAMP

=over

=item LONG

If this is nonzero, the timestamp will be displayed with seconds. 
Otherwise, only the year, month, and day are displayed in the link text.

=item TALKLINK

If this is nonzero, the HTML also includes a link to the revision of the
corresponding talk page at TIMESTAMP

=back

=cut

sub make_history_link {
  my $ns = shift;
  my $title = shift;
  my $ts = shift;
  my $long = shift || "";
  my $talktoo = shift || "";

  my $d = $ts;

  my $art = make_page_name($ns, $title);

  if ( $long eq 'l' ) {
    $d =~ s/T/ /;
    $d =~ s/Z/ /;
  } else {
    $d =~ s/T.*//;
  }

  my $result = 
       "<a href=\"" . $versionURL . "?article=" . uri_escape($art, "^A-Za-z" )
       . "&timestamp=" . uri_escape($ts) . "\">$d</a>&nbsp;";

  if ( $talktoo ) { 
    my $talk = make_talk_name($ns, $title);
    $result .=
       "(<a href=\"" . $versionURL . "?article=" . uri_escape($talk, "^A-Za-z" )
       . "&timestamp=" . uri_escape($ts) . "\">t</a>)&nbsp;";
  }

  return $result;
}

###########################################################################

=item B<make_page_name>(NS, PAGE)

Returns the formatted name of NS:PAGE, replacing the numeric NS with
the text version 

=cut

sub make_page_name {
  my $ns = shift;
  my $title = shift;

  if ( ! defined $namespaceIDs ) {
      $namespaceIDs = init_namespaces();
  }

  if ( $ns == 0 ) {
    return $title;
  } else {
    return $namespaceIDs->{$ns} . $title;
  }
}


=item B<make_talk_name>(NS, PAGE)

Returns the formatted name of the talk page 
corresponding to NS:PAGE. Talk pages correspond
to themselves, for other pages NS is incremented by 1. 

=cut

sub make_talk_name {
  my $ns = shift;
  my $title = shift;

  if ( 1 == $ns % 2) {
    return $title;
  } else {
    return make_page_name($ns+1, $title);
  }

}

###########################################################################

# internal function to load list of namespaces

sub init_namespaces {

  my $namespaces = db_get_namespaces();
  my $n;
  foreach $n ( keys %$namespaces ) {
    if ( $n ne '0') { $namespaces->{$n} .= ":";}
  }

  return $namespaces;
}

###########################################################################

=item B<get_cached_link_from_api>(CLASS)

Returns the formatted HTML for a CLASS-Class table cell

=cut

sub get_cached_link_from_api { 
  my $text = shift;

  if ( defined $cacheMem->{$text} ) { 
    print "<!-- hit $text in memory cache -->\n";
    return $cacheMem->{$text};
  }

  my $key = "LINK:" . substr($text, 0, 200);
  my ($data, $expiry);

  if ( $expiry = cache_exists($key) ) { 
     print "<!-- hit $key in database cache, expires " 
           . strftime("%Y-%m-%dT%H:%M:%SZ", gmtime($expiry))
           . " -->\n";
    $data = cache_get($key);
    $cacheMem->{$text} = $data;
    return $data;
  }

  $data = get_link_from_api($text);

  cache_set($key, $data, 12*60*60); # expires in 12 hours
  $cacheMem->{$text} = $data;
  return $data;
}



###########################################################################

=item B<get_link_from_api>(TEXT)

Parses TEXT using the API and returns the parsed HTML.

=cut

sub get_link_from_api {
  my $text = shift;
  my ($target, $desc);

  $text =~ s/^\[\[//;
  $text =~ s/]]$//;

  if ( $text =~ /\|/ ) { 
    ($target, $desc) = split /\|/, $text, 2;
  } else { 
    $target = $text;
    $desc = $text; 
  }

  return "<a href=\"" . $serverURL . "?title=" 
         . uri_escape_utf8($target,  "^A-Za-z" ) . "\">" . $desc . "</a>";

  # Previously, this was taken from the API. I'm not sure why anymore.

  my $r =  $api->parse($text);
  my $t = $r->{'text'}->{'content'};

  # TODO: internationalize this bare URL
  $t =~ s!^<p>!!;
  my @t = split('</p>',$t);
  $t = @t[0];

  @t = split('"',$t,2);
  $t = @t[0] . "\"" . $baseURL .  @t[1];

  print "<!-- link '$t' -->\n";

  return $t;
}

###########################################################################

=item B<list_projects>()

Returns a list reference of all projects in the database

=cut

sub list_projects { 
  my $dbh = shift;
  my @row;
  my $projects = {};

  my $sth = $dbh->prepare("SELECT p_project FROM " . db_table_prefix() . "projects");
  $sth->execute();

  while ( @row = $sth->fetchrow_array ) { 
    $projects->{$row[0]} = 1;
  }

  return $projects;
}

###########################################################################

=item B<get_cached_td_background>(CLASS)

Returns the formatted HTML for a CLASS-Class table cell

=cut

sub get_cached_td_background { 
  my $class = shift;

  if ( defined $cacheMem->{$class} ) { 
    print "<!-- hit $class in memory cache -->\n";
    return $cacheMem->{$class};
  }

  my $key = "CLASS:" . $class;
  my ($data, $expiry);

  if ( $expiry = cache_exists($key) ) { 
     print "<!-- hit $class in database cache, expires " 
           . strftime("%Y-%m-%dT%H:%M:%SZ", gmtime($expiry))
           . " -->\n";
    $data = cache_get($key);
    $cacheMem->{$class} = $data;
    return $data;
  }

  $data = get_td_background($class);

  cache_set($key, $data, 12*60*60); # expires in 12 hours
  $cacheMem->{$class} = $data;
  return $data;
}

###########################################################################

# internal function to get td background from the wiki

sub get_td_background { 
  my $class = shift;
#  return "<td>$class</td>";  # to disable api parsing

  my $r =  $api->parse('{{' . $class . '}}');
  my $t = $r->{'text'}->{'content'};

  $t =~ s/\|.*//s;
  $t =~ s!^<p>!!;
  $class =~ s/-Class//;
  $t = "<td $t><b>$class</b></td>";

  # XXX hack
  $t =~ s/Bplus/B+/;
  $t =~ s/NotA/----/;

  return $t;
}

###########################################################################

=item B<get_cached_wiki_page>(PAGE)

Returns the formatted HTML for PAGE on the wiki

=cut

sub get_cached_wiki_page { 
  my $page = shift;
  my $purge = shift;

  my $key = "PAGE:" . $page;

  if ( (! defined $purge) && defined $cacheMem->{$key} ) { 
    print "<!-- hit $key in memory cache -->\n";
    return $cacheMem->{$key};
  }

  my ($data, $expiry);
  $expiry = cache_exists($key);

#XXX - broken DB somehowH
  $expiry =~ s/\0//g;

  if ( (! defined $purge) && $expiry) { 
     print "<!-- hit $expiry $key in database cache, expires " 
           . strftime("%Y-%m-%dT%H:%M:%SZ", gmtime($expiry))
           . " -->\n";
    $data = cache_get($key);
    $cacheMem->{$key} = $data;
    return $data;
  }

  if ( defined $purge ) { 
    print "<!-- purging $key in cache -->\n";
  } else { 
    print "<!-- missed $key in cache -->\n";
  }

  $data = get_wiki_page($page);

  cache_set($key, $data, 12*60*60); # expires in 12 hours
  $cacheMem->{$key} = $data;
  return $data;
}

###########################################################################

# internal function to get html for a page from the wiki

sub get_wiki_page { 
  my $page = shift;
#  return $page;  # To disable API parsing

  my $r =  $api->parse('{{' . $page . '}}');
  my $t = $r->{'text'}->{'content'};
  return $t;
}


###########################################################################

=item B<get_cached_review_icon>(REVIEWCLASS)

Gets formatted HTML for a table cell for a REVIEWCLASS article,
including the icon for that REVIEWCLASS. 

=cut

sub get_cached_review_icon { 
  my $class = shift;
  
  if ( defined $cacheMem->{$class . "-icon"} ) { 
    print "<!-- hit {$class}-icon in memory cache -->\n";
    return $cacheMem->{$class . "-icon"};
  }
  
  my $key = "CLASS:" . $class . "-icon";
  my ($expiry, $data);
  
  if ( $expiry = cache_exists($key) ) { 
    print "<!-- hit {$class}-icon in database cache, expiry " 
    . strftime("%Y-%m-%dT%H:%M:%SZ", gmtime($expiry))
    . " -->\n";
    $data = cache_get($key);
    $cacheMem->{$class} = $data;
    return $data;
  }
  
  $data = get_review_icon($class);
  
  cache_set($key, $data, '12 hours');
  $cacheMem->{$class . "-icon"} = $data;
  return $data;
}

###########################################################################

# internal function to get review icon from API

sub get_review_icon { 
  my $class = shift;
#  return "<td> $class</td>";  # To disable API parsing

  my $r =  $api->parse('{{' . $class . '-Class}}');
  my $t = $r->{'text'}->{'content'};
  my $f =  $api->parse('{{' . $class . '-classicon}}');
  my $g = $f->{'text'}->{'content'};
  
  $t =~ s/\|.*//s;
  $t =~ s!^<p>!!;
  $g =~ s/<\/p.*//;
  $g =~ s!^<p>!!;
  # Perl doesn't want to get rid of the rest of the lines in the 
  # multi-line string, so remove them the hard way
  my @str = split(/\n/,$g);
  $g = @str[0];
  undef(@str);
  $class =~ s/-Class//;
  $t = "<td $t><b>$g&nbsp;$class</b></td>";
  
  return $t;
}

###########################################################################

=item B<make_wp05_link>(CAT)

Returns a link to the Wikipedia 0.5 page for review category
CAT (which coult be Arts, Geography, etc.)

=cut

sub make_wp05_link { 
  my $cat = shift;
  my $linka = "http://en.wikipedia.org/wiki/Wikipedia:Wikipedia_0.5";
  my $linkb = "http://en.wikipedia.org/wiki/Wikipedia:Version_0.5";
  my $abbrev = {  'Arts' => 'A',
      'Engineering, applied sciences, and technology' => 'ET',
      'Everyday life' => 'EL',
      'Geography' => 'G',
      'History' => 'H',
      'Language and literature' => 'LL',
      'Mathematics' => 'Ma',
      'Natural sciences' => 'NS',
      'Philosophy and religion' => 'PR',
      'Social sciences and society' => 'SS',
      'Uncategorized'  => 'U'};

  return "<a href=\"$linka\">0.5</a> ";
}

###########################################################################

=item B<make_review_link>(REVIEWCLASS)

Returns formatted HTML for a table cell for REVIEWCLASS

=cut

sub make_review_link { 
  my $type = shift;
  return get_cached_td_background($type . "-Class") ;
}

###########################################################################

=item B<make_workingselection_html>(SELECTED) 

Returns HTML to tag whether an article is part of a pending selection.
SELECTED is either 0 (not selected) or 1 (selected).

=cut

sub make_workingselection_html { 

  my $sel = shift;
  my $title = shift || "Default";

  if ( $Opts->{'show_working_selection'} == 0) { 
    return '';
  }

  if ( defined($sel) ) { 
    if ( $sel == 0 ) { 
      return "&nbsp;&diams;";
    }  else { 
    return '&nbsp;<a href="' . $serverURL 
                              . '?title=' . $title 
                              . '&oldid=' . $sel 
                              . '">&diams;</a>';
    }
  } else { 
    return "";
  }
}

###########################################################################

# internal function to munge timestamps

sub fix_timestamp { 
  my $t = shift;

  return substr($t, 0, 4) . "-" . substr($t, 4, 2) . "-"
           . substr($t, 6, 2) . "T" . substr($t, 8, 2) 
           . ":" . substr($t, 10, 2) . ":" . substr($t, 12, 2)  . "Z";
}

###########################################################################

sub commify {
  # commify a number. Perl Cookbook, 2.17, p. 64
  my $text = reverse $_[0];
  $text =~ s/(\d\d\d)(?=\d)(?!\d*\.)/$1,/g;
  return scalar reverse $text;
}

###########################################################################

# Load successfully
1;
