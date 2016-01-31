#!/usr/bin/perl

# table_lib.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

Library routines to create assessment summary tables

=over

=cut

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

require 'layout.pl' or die;

my $timestamp = strftime("%Y-%m-%dT%H:%M:%SZ", gmtime(time()));

my $list_url = $Opts->{'list2-url'} 
  or die "No 'list2-url' specified in configuration.\n";

my $log_url = $Opts->{'log-url'} 
  or die "No 'list2-url' specified in configuration.\n";

require 'layout.pl';

use DBI;
require "database_www.pl";
our $dbh = db_connect_rw($Opts);

require 'cache.pl';
my $cache_sep = "<!-- cache separator -->\n";

############################################################
=item B<cached_project_table>(PROJECT, [PURGE])

Get the summary table for PROJECT, using the cache and updating
the cache if needed. If PURGE is nonzero then the cache will
be forced to update. 

Returns ($html, $wikicode).

=cut

sub cached_project_table { 
  my $proj = shift;
  my $purge = shift || 0;

  my $sth = $dbh->prepare("select p_timestamp from " . db_table_prefix() . "projects "
                        . "where p_project = ?");
  
  $sth->execute($proj);
  my @row = $sth->fetchrow_array();
  my $proj_timestamp = $row[0];

  print "<!-- cache debugging  -->\n";
  print "<!-- Current time: $timestamp -->\n";
  print "<!-- Data for project $proj was last updated '$proj_timestamp'-->\n";

  my $key = "TABLE:" . $proj;
  my $data;
  my $expiry = cache_exists($key);

  if ( $purge && $expiry )  { 
    print "<!-- Purging cached output -->\n";
  } elsif ( $expiry ) { 
    print "<!-- Cached output expires " 
        . strftime("%Y-%m-%dT%H:%M:%SZ", gmtime($expiry)) 
        . "-->\n";

    $data = cache_get($key);
    my ($c_key, $c_timestamp, $c_proj_timestamp, $c_html, $c_wikicode, $c_count) = 
    split /\Q$cache_sep\E/, $data, 6;

  print "Key: '$c_key'\n";
  print "Count: '$c_count'\n";

    if ( $c_proj_timestamp eq $proj_timestamp ) {
      print "<!-- Cached output valid -->\n";
      if ( defined $ENV{'TABLE_PURGE'} ) { 
        print "<!-- regenerate anyway -->\n";
      }
      print "<!-- end cache debugging -->\n";
      return ($c_html, $c_wikicode, $c_proj_timestamp, $c_count)
        if ( ! defined $ENV{'TABLE_PURGE'} );
    } else {
      print "<!-- Cached output must be regenerated -->\n";
    }
  } else {
    print "<!-- No cached output available --> \n";
  }

  print "<!-- Regenerating output --> \n";
  print "<!-- end cache debugging --> \n";

  my ($html, $wikicode, $acount) = make_project_table($proj);

  $data = "TABLE:$proj" . $cache_sep 
        . $timestamp . $cache_sep
        . $proj_timestamp . $cache_sep 
        . $html . $cache_sep 
        . $wikicode . $cache_sep
        . $acount;

  cache_set($key, $data, 12*60*60); # expires in 12 hours

  return ($html, $wikicode, $timestamp, $acount);
}


############################################################
=item B<make_project_table>(PROJECT, CATEGORY, CATNS, TITLE, CONFIG)

Create a new table for PROJECT. Does not use the cache in any way. 

=cut

sub make_project_table { 
  my $proj = shift;
  my $cat = shift;
  my $catNS = shift;
  my $title = shift;
  my $config = shift;

  if ( defined $config->{'filterNamespace'} ) { 
    $catNS = $config->{'filterNamespace'};
  }

  my $tdata = fetch_project_table_data($proj, $cat, $catNS, $title);

  if ( ! defined $title ) { 
    $title = $proj;
    $title =~ s/_/ /g;
    $title = $title . " articles by quality and importance";
  }

  my $format = \&format_cell_pqi;

  if ( defined $cat ) { 
    $format = get_format_cell_pqi_cat($cat, $catNS);
  }

  my ($code, $acount) = make_project_table_wikicode($tdata, $title, $format, $config );

  my $r =  $api->parse($code);
  return ($r->{'text'}->{'content'}, $code, $acount);

#  my $r = "";
#  return ($r, $code);

}


############################################################
=item B<make_global_table>()

Create a new global table. Does not use the cache in any way. 

=cut

sub make_global_table { 
  my $tdata = fetch_global_table_data();
  my ($code, $total) = make_project_table_wikicode($tdata, 
                            "All rated articles by quality and importance",
                            \&format_cell_pqi_nolink  );
  my $r =  $api->parse($code);
  my $created = time();

  return ($r->{'text'}->{'content'}, $code, $created);
}

############################################################
=item B<fetch_project_table_data>(PROJECT)

Fetch info to create table for project. Returns a TDATA object.

=cut

sub fetch_project_table_data { 
  my $proj = shift;
  my $cat = shift;
  my $catNS = shift;

  printf "<!-- Fetch data for '%s' '%s' '%s' -->\n", $proj, $cat, $catNS;

  # Step 1: fetch totals from DB and load them into the $data hash
  
  my $query;
  my @qparam;

  if ( ! defined $cat ) { 
    if ( ! defined $catNS ) { 
      $query =  "
        select count(r_article), r_quality, r_importance, r_project 
        from " . db_table_prefix() . "ratings
        where r_project = ? group by r_quality, r_importance, r_project";

      push @qparam, $proj;
    } else { 
      $query =  "
        select count(r_article), r_quality, r_importance, r_project 
        from " . db_table_prefix() . "ratings
        where r_project = ? and r_namespace = ? 
         group by r_quality, r_importance, r_project";

      push @qparam, $proj;
      push @qparam, $catNS;
    }      
  } else { 

    $query =  "
      select count(r_article), r_quality, r_importance, r_project 
      from " . db_table_prefix() . "ratings
      join enwiki_p.page on page_namespace = ? 
       and page_title = r_article 
/*        and replace(page_title, '_', ' ') 
                 =  cast(r_article as char character set latin1)  */
/*                        and page_title = replace(r_article, ' ', '_') */
      join enwiki_p.categorylinks on page_id = cl_from and cl_to = ?  
      where r_project = ? and r_namespace = ? 
        group by r_quality, r_importance, r_project 
           /* SLOW_OK */";

    $cat =~ s/ /_/g;
    push @qparam, $catNS;
    push @qparam, $cat;
    push @qparam, $proj;
 
    $_ = $catNS;
    if ( 1 == $_ % 2 ) { $_ = $_ - 1; } 
    push @qparam, $_;

  } 

  my $sth = $dbh->prepare($query);

  $sth->execute(@qparam);

  my ($SortQual, $SortImp, $QualityLabels, $ImportanceLabels) 
    = get_project_categories($proj);

  my $data = {};
  my $cols = {};
  my @row;

  while ( @row = $sth->fetchrow_array ) {
    if ( ! defined $row[1] ) { $row[1] = 'Unassessed-Class'; }
    if ( ! defined $row[2] ) { $row[2] = 'Unknown-Class'; }
    if ( ! defined $data->{$row[1]} ) { $data->{$row[1]} = {} };

    # The += here is for 'Unssessed-Class' classifications, which 
    # could happen either as a result of an actual category or as 
    # the result of the if statements above
    $data->{$row[1]}->{$row[2]} += $row[0];
    $cols->{$row[2]} = 1;
  }

  # Step 2 - remove any rows or columns that shouldn't be displayed

  my $col;
  foreach $col ( keys %$cols ) {
    if ( ! defined $SortImp->{$col} ) { 
      print "<!-- skip col $col -->\n";
      delete $cols->{$col};
    }
  }

  my $row;
  foreach $row ( keys %$data ) { 
    if ( ! defined $SortQual->{$row} ) { 
      print "skip row $row\n";
      delete $data->{$row};
    }
  }

  return { 'proj' => $proj, 
           'cols' => $cols,
           'data' => $data,
           'SortImp' => $SortImp,
           'SortQual' => $SortQual,
           'ImportanceLabels' => $ImportanceLabels,
           'QualityLabels' => $QualityLabels };

} 

##############################################################
=item B<make_project_table_wikicode>(TDATA, TITLE, FORMAT, CONFIG)

Create wikicode for a table using data from TDATA. The overall
title is TITLE. The FORMAT function is used to format the table
cells. It is invoked as:

&{$FORMAT}(project, quality, importance, value)

where quality and/or importance will be undefined for the
cells corresponding to the Total row and column.

CONF is a hash used to set formatting settings for the table

=cut

sub make_project_table_wikicode { 
  my $tdata = shift;
  my $title = shift;
  my $format_cell = shift;
  my $config = shift;

  if ( ! defined $config) { 
    $config = {}; 
  } else { 
    if ( defined $ENV{'DEBUG'})  { 
      print Dumper($config);
    }
  }

  my $proj = $tdata->{'proj'};
  my $cols = $tdata->{'cols'};
  my $data = $tdata->{'data'};
  my $SortImp = $tdata->{'SortImp'};
  my $SortQual = $tdata->{'SortQual'};
  my $ImportanceLabels = $tdata->{'ImportanceLabels'};
  my $QualityLabels = $tdata->{'QualityLabels'};

  # The 'assessed' data is generated dynamically
  if ( ! defined $config->{'noassessed'} ) { 
    $data->{'Assessed'} = {};
  }

  # These, along with the totals, will appear in the final table. 
  # The important step here is the sorting. 
  my @PriorityRatings = sort { $SortImp->{$b} <=> $SortImp->{$a} } 
                             keys %$cols;
  my @QualityRatings =  sort { $SortQual->{$b} <=> $SortQual->{$a} } 
                             keys %$data; 

  use RatingsTable;
  my $table = RatingsTable::new();

  my $TotalWikicode = "style=\"text-align: center;\" | '''Total'''";
  $QualityLabels->{'Total'} = $TotalWikicode;
  $ImportanceLabels->{'Total'} = $TotalWikicode;
 
  $table->proj($proj);
  $table->title($title);

  $table->columnlabels($ImportanceLabels);  
  $table->rowlabels($QualityLabels);

  if ( defined $config->{'importance-header'} ) { 
    $table->columntitle($config->{'importance-header'});
  } else { 
    $table->columntitle("'''Importance'''");
  }

  if ( defined $config->{'quality-header'} ) { 
    $table->columntitle($config->{'quality-header'});
  } else { 
    $table->rowtitle("'''Quality'''");
  }

  # Temporary arrays used to hold lists of row resp. column names
  my @P = (@PriorityRatings, "Total");
  my @Q = (@QualityRatings,"Total");


  $table->rows(\@Q);

  # If there are just two columns, they have the same data
  # So just show the totals

  if ( 2 < scalar @P ) { 
      $table->columns(\@P);
  } else { 
      $table->columns(["Total"]);
      my $projt = $proj;
      $projt =~ s/_/ /g;
      $table->title("$projt pages by quality");
      $table->unset_columntitle();
      $TotalWikicode = "style=\"text-align: center;\" | '''Total pages'''";
      $ImportanceLabels->{'Total'} = $TotalWikicode;
  }

  my $priocounts = {};  # Used to count total articles by priority rating
  my $qualcounts = {};  # same, for each quality rating
  my $cells;

  my $total;
  
  $table->clear();

  my $qual;
  my $prio;
  my $total = 0;
  my $totalAssessed = {};  # To count 'Assessed' articles

  # Next step: fill in table data using the $data hash

  foreach $qual ( @QualityRatings ) {
      $qualcounts->{$qual}=0;
  }

  foreach $prio ( @PriorityRatings ) { 
      $priocounts->{$prio} = 0;
  }

  foreach $qual ( @QualityRatings ) {
      next if ( $qual eq 'Assessed' );  # nothing in $data for this

      foreach $prio ( @PriorityRatings ) { 
#      print "<!-- q '$qual' p '$prio' -->\n";

	  if (  (defined $data->{$qual}->{$prio}) 
              && $data->{$qual}->{$prio} > 0 ) { 
            $table->data($qual, $prio, 
                         &{$format_cell}($proj, $qual, $prio, 
                                         $data->{$qual}->{$prio}) );

	  } else { 
	      $table->data($qual, $prio, "");
	  }
# print "<!-- qual '$qual' prio '$prio' -->\n";
	  if ( defined $data->{$qual}->{$prio} ) { 
	      $qualcounts->{$qual} += $data->{$qual}->{$prio};
	      $priocounts->{$prio} += $data->{$qual}->{$prio};    
	      $total += $data->{$qual}->{$prio};    
	  }

	  if ( ! ($qual eq 'Unassessed-Class' ) ) { 

             if ( ! defined $data->{$qual}->{$prio}  ) { 
 		 $data->{$qual}->{$prio}  = 0;
	     }

             if ( ! defined $totalAssessed->{$prio} ) { 
                 $totalAssessed->{$prio} = 0;
             }

             $totalAssessed->{$prio} += $data->{$qual}->{$prio};
             $totalAssessed->{'Total'} += $data->{$qual}->{$prio};
	  }
      }
  }

  foreach $qual ( @QualityRatings ) {
    next if ( ($qual eq 'Assessed' ) && defined $config->{'noassessed'} );
    $table->data($qual,  "Total",
                 &{$format_cell}($proj, $qual, undef, $qualcounts->{$qual}));
  }


  foreach $prio ( @PriorityRatings ) { 
    $table->data("Total", $prio, 
                 &{$format_cell}($proj, undef, $prio, $priocounts->{$prio}));

    if ( ! defined $config->{'noassessed'} ) { 
      $table->data("Assessed", $prio, 
                   &{$format_cell}($proj, "Assessed", $prio, 
                                 $totalAssessed->{$prio}));
    }
  }

  $table->data("Total", "Total", &{$format_cell}($proj, undef, undef, $total));

  if ( ! defined $config->{'noassessed'} ) { 
      $table->data("Assessed", "Total", 
                 &{$format_cell}($proj, "Assessed", undef, 
                                 $totalAssessed->{'Total'} || "0"));
  }

  if ( defined $config->{'transpose'} ) { 
    $table->transpose();
  }

  my $code = $table->wikicode();
  $total = $totalAssessed->{'Total'} || 0;
  print "<!-- Total: $total -->\n";
  return ($code, $total);
}

################################################################
=item B<get_project_categories>(PROJECT)

Internal function to fetch info about assessment categories for PROJECT 
from the database. 

=cut

sub get_project_categories { 
  my $project = shift;

  my $MA = "$project articles";

  my $data = {};

  my $sortQual = {};
  my $sortImp = {};
  my $qualityLabels = {};
  my $importanceLabels = {};
  my $categories = {};

  my $sth = $dbh->prepare(
      "SELECT c_type, c_rating, c_ranking, c_category FROM " . db_table_prefix() . "categories " . 
      "WHERE c_project = ?" );

  $sth->execute($project);

  my @row;

  while ( @row = $sth->fetchrow_array() ) {
    if ( $row[0] eq 'quality' ) { 
      $sortQual->{$row[1]} = $row[2];
      if ( $row[1] eq $NotAClass ) { 
        $qualityLabels->{$row[1]} = 
               " style=\"text-align: center;\" | '''Other'''";
      } else { 
        $qualityLabels->{$row[1]} = "{{$row[1]|category=Category:$row[3]}}";
      }
    } elsif ( $row[0] eq 'importance' ) { 
      $sortImp->{$row[1]} = $row[2];

      if ( $row[1] eq $NotAClass ) { 
        $importanceLabels->{$row[1]} = "Other";
      } else { 
        $importanceLabels->{$row[1]} = "{{$row[1]|category=Category:$row[3]}}";
      }
    }
  }

  if ( ! defined $sortImp->{'Unassessed-Class'} ) { 
    $sortImp->{'Unassessed-Class'} = 0;
    $importanceLabels->{'Unassessed-Class'} = "'''None'''";
  } else { 
    $importanceLabels->{'Unassessed-Class'} =~ s/Unassessed-Class/No-Class/;
  }

  if ( ! defined $sortQual->{'Unassessed-Class'} ) { 
    $sortQual->{'Unassessed-Class'} = 0;
    $qualityLabels->{'Unassessed-Class'} = "'''Unassessed'''";
  }

  if ( ! defined $sortQual->{'Assessed'} ) { 
    $sortQual->{'Assessed'} = 20;
    $qualityLabels->{'Assessed'} = "{{Assessed-Class}}";
  }

  return ($sortQual, $sortImp, $qualityLabels, $importanceLabels);
}

################################################################
=item B<get_global_table_data>())

Get assessment data from the global table. Returns a TDATA object.

=cut

sub fetch_global_table_data { 

  # Step 1: fetch totals from DB and load them into the $data hash

  my $query = 
"select count(distinct a_article), grq.gr_rating, gri.gr_rating /* SLOW_OK */
from " . db_table_prefix() . "global_articles
join " . db_table_prefix() . "global_rankings as grq 
  on grq.gr_type = 'quality' and grq.gr_ranking= a_quality
join " . db_table_prefix() . "global_rankings as gri 
  on gri.gr_type = 'importance' and gri.gr_ranking= a_importance
group by grq.gr_rating, gri.gr_rating ";

  my $sth = $dbh->prepare($query);
  
  $sth->execute();

  my ($SortQual, $SortImp, $QualityLabels, $ImportanceLabels) 
    = get_global_categories();

  my $data = {};
  my $cols = {};
  my @row;

  while ( @row = $sth->fetchrow_array ) {
    if ( ! defined $row[1] ) { $row[1] = $NotAClass; }
    if ( ! defined $row[2] ) { $row[2] = $NotAClass; }
    if ( ! defined $data->{$row[1]} ) { $data->{$row[1]} = {} };

    # The += here is for 'NotA-Class' classifications, which 
    # could happen either as a result of an actual category or as 
    # the result of the if statements above
    $data->{$row[1]}->{$row[2]} += $row[0];
    $cols->{$row[2]} = 1;
  }

  # Step 2 - remove any rows or columns that shouldn't be displayed

  my $col;
  foreach $col ( keys %$cols ) {
    if ( ! defined $SortImp->{$col} ) { 
      print "skip col $col\n";
      delete $cols->{$col};
    }
  }

  my $row;
  foreach $row ( keys %$data ) { 
    if ( ! defined $SortQual->{$row} ) { 
      print "skip row $row\n";
      delete $data->{$row};
    }
  }

  return { 'proj' => undef, 
           'cols' => $cols,
           'data' => $data,
           'SortImp' => $SortImp,
           'SortQual' => $SortQual,
           'ImportanceLabels' => $ImportanceLabels,
           'QualityLabels' => $QualityLabels };
}

################################################################
=item B<get_global_categories>())

Internal function to Get info about global assessments from
database.

=cut

sub get_global_categories { 

  my $Assessed = "Assessed";
  my $Assessed_Class = "Assessed-Class";
  my $Unassessed_Class = "Unassessed-Class";
  my $Unknown_Class = "Unknown-Class";

  my $sortQual = { 'FA-Class' => 500, 'FL-Class' => 480, 'A-Class' => 425, 
                   'GA-Class' => 400, 'B-Class' => 300, 'C-Class' => 225, 
              'Start-Class'=>150, 'Stub-Class' => 100, 'List-Class' => 80, 
              $Assessed => 20, $NotAClass => '11', 
              'Unknown-Class' => '10',  $Unassessed_Class => 0};

  my $sortImp= { 'Top-Class' => 400, 'High-Class' => 300, 
                 'Mid-Class' => 200, 'Low-Class' => 100, 
                 $NotAClass => 11, $Unknown_Class => 10, 
                  $Unassessed_Class => 0};

  my $qualityLabels = {};
  my $importanceLabels = {};

  my $k;
  foreach $k ( keys %$sortQual ) { 
    $qualityLabels->{$k} = "{{$k}}";
  }

  $qualityLabels->{$Assessed} = "'''$Assessed'''";

  foreach $k ( keys %$sortImp ) { 
    $importanceLabels->{$k} = "{{$k}}";
  }

  $importanceLabels->{'Unassessed-Class'} =~ s/Unassessed-Class/No-Class/;

  return ($sortQual, $sortImp, $qualityLabels, $importanceLabels);
}

################################################################
=item B<cached_global_ratings_table>([PURGE])

Gets the global ratings table, using the cache and updating
the cache if needed. If PURGE is nonzero then the cache
will be forced to update. 

Returns ($html, $wikicode).

=cut

sub cached_global_ratings_table { 
  my $force_regenerate = shift || 0;

  print "<!-- global table - purge: '$force_regenerate' -->\n";

  my $key = "GLOBAL:TABLE";
  my ($expiry, $data);

  if ( ($expiry = cache_exists($key)) && ! $force_regenerate ) { 
    print "<!-- Debugging output -->\n";
    print "<!-- Current time: $timestamp --> \n";

    $expiry =~ s/\0//g;

    print "<!-- Cached output expires: " 
       . strftime("%Y-%m-%dT%H:%M:%SZ", gmtime($expiry)) 
       . " -->\n";

    $data = cache_get($key);

#print "D: '$data'\n";

    my ($c_key, $c_html, $c_wikicode, $c_created) = 
          split /\Q$cache_sep\E/, $data, 4;

    return ($c_html, $c_wikicode, $c_created);
  }

  if ( ! $force_regenerate ) { 
# no data available
      return;
  }

  print "<!-- Regenerating global table -->\n";
  print "<!-- Current time: $timestamp -->\n";
  my $ts = time();
  
  my ($html, $wikicode, $createdtime) = make_global_table();


  $ts = time() - $ts;
  $ts = int(0.5 + $ts / 60);
  print "<!-- Regenerated in $ts minutes -->\n";

  $data = "GLOBAL:TABLE" 
        . $cache_sep . $html 
        . $cache_sep . $wikicode
        . $cache_sep . $createdtime;

  cache_set($key, $data, 7*24*60*60); # expires in 1 week

  return ($html, $wikicode, $createdtime);
}

################################################################
=item B<format_cell_pqi_nolink>(PROJECT, QUALITY, IMPORTANCE, VALUE)

Create a formatted table cell entry. There is no link.
If either QUALITY or IMPORTANCE is undefined, the cell is bold.
=cut

sub format_cell_pqi_nolink { 
  my $proj = shift;
  my $qual = shift;
  my $prio = shift;
  my $value = shift;

  my $bold = "";
  if ( (! defined $qual) || (! defined $prio ) ) { 
    $bold = "'''";
  }

  my $str = $bold . commify($value) . $bold ;

  return $str;
}

################################################################
=item B<format_cell_pqi>(PROJECT, QUALITY, IMPORTANCE, VALUE)

Create a formatted table cell entry. The entry links to the article
list for PROJECT, with approprate query values preset. 

=cut

sub format_cell_pqi { 
  my $proj = shift;
  my $qual = shift;
  my $prio = shift;
  my $value = shift;

  my $bold = "";
  if ( (! defined $qual) || (! defined $prio ) ) { 
    $bold = "'''";
  }

  my $str = $bold . '[' . $list_url . "?run=yes";

  if ( defined $proj ) { 
    $str .= "&projecta=" . uri_escape($proj) ;
  }

  if ( defined $prio ) { 
    $str .= "&importance=" . uri_escape($prio) ;
  }

  if ( defined $qual ) { 
    $str .= "&quality=" . uri_escape($qual)  ;
  }

  $str .=  ' ' . commify($value) . "]" . $bold ;

  return $str;
}

################################################################
################################################################
=item B<get_format_cell_pqi_cat>(CATEGORY, NAMESPACE)

Return a subroutine reference for tables limited to a particular category

=cut

sub get_format_cell_pqi_cat { 
  my $cat = shift;
  my $catNS = shift;

  my $ns = $catNS;

  my $catparam = 'category';

  if ( 1 == ($catNS % 2) ) { 
    $catparam = 'categoryt';
    $ns--;
  }

  return sub { 

    my $proj = shift;
    my $qual = shift;
    my $prio = shift;
    my $value = shift;

    my $bold = "";
    if ( (! defined $qual) || (! defined $prio ) ) { 
      $bold = "'''";
    }

    my $str = $bold . '[' . $list_url . "?run=yes";

    $str .= "&filterCategory=on&namespace=$ns";
    $str .= "&" . $catparam . "=" . uri_escape($cat);

    if ( defined $proj ) { 
      $str .= "&projecta=" . uri_escape($proj) ;
    }

    if ( defined $prio ) { 
      $str .= "&importance=" . uri_escape($prio) ;
    }

    if ( defined $qual ) { 
      $str .= "&quality=" . uri_escape($qual)  ;
    }

    $str .=  ' ' . commify($value) . "]" . $bold ;

    return $str;
  }
}

################################################################

=pod

=back 

=cut

#Load successfully
1;
