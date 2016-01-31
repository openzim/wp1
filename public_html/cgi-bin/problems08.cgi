#!/usr/bin/perl
use strict;
use lib  '/home/cbm/perl/share/perl/5.10.0/';
use URI::Escape;

print STDERR "$]\n";

my $SelectedFile = 
  "/home/cbm/public_html/release-data/2008-9-13/HTML/CSV/Selected.txt";

use CGI;
print CGI::header(-type=>'text/html', -charset=>'utf-8');      

my $cgi = new CGI;
my %Param = %{$cgi->Vars()};

require Cache::File;
my $CacheDir = "/home/project/e/n/w/enwp10/www-cache";
my $cacheFile = Cache::File->new( cache_root => $CacheDir);

use DBI;
my $db = DBI->connect("DBI:mysql:host=sql-s1" 
                    . ":database=enwiki_p" 
                    . ":mysql_read_default_file=/home/project/e/n/w/enwp10/.my.cnf",
                    "", "") or die;

my $key = '0.8PROBLEMS';

if ( $cacheFile->exists($key) && ! exists $Param{'purge'} ) { 
  print $cacheFile->get($key);
} else { 
  my $HTML = generate_list($db);
  $cacheFile->set($key, $HTML, '1 hour');
  print $HTML;
}

exit;

#####################################################################

sub generate_list { 

my $db = shift;

my $HTML = "";

my %Selected;
my %Problems;
my %Sort;
my @parts;
my %Projects;
my %ProjectCount;

my %Members;

my %Abbrev =  ('All_pages_needing_cleanup' => 'cleanup',
   'All_pages_lacking_sources' => 'unreferenced',
   'All_articles_that_may_contain_original_research' => 'original research',
   'Pages_needing_expert_attention' => 'expert',
   'Wikipedia_articles_needing_clarification' => 'clarify',
   'All_articles_needing_style_editing' => 'style',
   'Wikipedia_articles_needing_style_editing' => 'style',
   'NPOV_disputes' => 'NPOV',
   'All_articles_with_unsourced_statements' => 'fact',
   'All_articles_needing_copy_edit' => 'copyedit',
   'All_NPOV_disputes' => 'NPOV');

my $sth = $db->prepare("select ws_article, r_project from 
p_enwp10.workingselection join p_enwp10.ratings on r_namespace = 0 
and r_article = ws_article");

$sth->execute();

while ( @parts = $sth->fetchrow_array() ) { 
  $Selected{$parts[0]} = 1;

  if ( ! defined $Projects{$parts[1]} ) { 
    $Projects{$parts[1]} = [];
  }
  push @{$Projects{$parts[1]}}, $parts[0];

  if ( ! defined $Members{$parts[0]} ) { 
    $Members{$parts[0]} = [];
  }
  push @{$Members{$parts[0]}}, $parts[1];
}
close IN;


my $query = << "HERE";
select cl_to, page_namespace, page_title
from page join categorylinks on cl_from = page_id 
where cl_to in 
  ('All_pages_needing_cleanup',
   'All_pages_lacking_sources',
   'All_articles_that_may_contain_original_research',
   'Pages_needing_expert_attention',
   'Wikipedia_articles_needing_clarification',
   'All_articles_needing_style_editing'
   'Wikipedia_articles_needing_style_editing',
   'All_articles_needing_copy_edit',
   'NPOV_disputes',
   'All_NPOV_disputes')
HERE

# for fact tags
#   'All_articles_with_unsourced_statements',

my $sth = $db->prepare($query);

print STDERR "q2\n";
$sth->execute();
print STDERR "back\n";

my $count = 0;
my $p;
while ( @parts = $sth->fetchrow_array() ) { 
  next unless ( ($parts[1] == 1) || ($parts[1] == 0));
  if ( exists $Selected{$parts[2]} ) { 
    $count++;

    foreach $p ( @{$Members{$parts[2]}} ) { 
      if ( ! defined $ProjectCount{$p} ) { 
        $ProjectCount{$p} = {};
      }
      $ProjectCount{$p}->{$parts[2]} = 1;
    }

    if ( ! defined $Problems{$parts[2]} ) {
      $Problems{$parts[2]} = [];
    }
    push @{$Problems{$parts[2]}}, $parts[0];

    $Sort{$parts[0]} ++;
  }
}
close IN;

my $date = `/bin/date`;
chomp $date;

my @Articles = sort {$a cmp $b} keys %Problems;
my @ProjectNames = sort {$a cmp $b} keys %ProjectCount;

my $proj;
my $projenc;
my $art;
my $artenc;
my $url = "http://en.wikipedia.org/wiki";

$HTML .= << "HERE";
<html>
<head>
<title>Wikipedia 0.8 selected articles with maintenance tags</title>
<style type="text/css">
body { padding-top: 0px; 
       margin-top: 0px; 
       margin-left: 0px; 
       margin-right: 0em;
     }
h1 { font-size: 12pt; 
     background:#2f4564; 
     border-top: 6px solid black;
     color: white;
     padding-left: 1em;
     padding-bottom: .3em;
   }
h2 { font-size: 12pt; 
      border-top: 1px solid black; 
      padding-left: 1em;
   }
div.index { 
  padding-left: 1em;
}

</style>
</head>
<body>
<h1>Wikipedia 0.8 articles with maintenance tags</h1>
<ul>
<li><b>Updated on demand at most once per hour.</b></li>
<li><b>Last updated:</b> $date</li>
HERE

$HTML .= "<li><b>Articles with maintenance tags:</b> ";
$HTML .= (scalar keys %Problems) . "</li>\n<ul>\n";

foreach $_ ( sort {$a cmp $b} keys %Sort ) { 
  $HTML .= "<li>" . $_ . " " . $Sort{$_} . "</li>\n";
}
$HTML .= "</ul>\n</ul>\n";

# $HTML .= << "HERE";
# <form method="post">
# <input type="hidden" name="purge" value="yes">
# <input type="submit" value="Regenerate">
# </form>
# HERE

$HTML .= "<h2>Project index</h2>\n<div class=\"index\">";


foreach $proj ( @ProjectNames ) { 
  $projenc = $proj;
  $projenc =~ s/[^A-Za-z ]//g;
  $projenc =~ s/ /_/g;
  $HTML .= "<a href=\"#$projenc\">$proj</a> &middot; ";
}

$HTML .= "</div>\n";

my $c;
foreach $proj ( @ProjectNames ) { 
  $projenc = $proj;
  $projenc =~ s/[^A-Za-z ]//g;
  $projenc =~ s/ /_/g;
  $c = scalar keys %{$ProjectCount{$proj}};

$HTML .= << "HERE";
<h2 id="$projenc">$proj ($c)</h2>
<ul>
HERE
  foreach $art ( sort {$a cmp $b} @{$Projects{$proj}} ) { 
    next unless ( exists $Problems{$art});
    $artenc = uri_escape($art);
    $HTML .= "<li><a href=\"$url/$artenc\">$art</a>: ";
    $HTML .= (join " &middot; ", map { $Abbrev{$_} } @{$Problems{$art}});
    $HTML .= "</li>\n";
  }
  $HTML .= "</ul>\n\n";

}

$HTML .= << "HERE";
</body>
</html>
HERE

return $HTML;
}

#####################################################################

__END__
