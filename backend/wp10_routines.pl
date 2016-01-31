#!/usr/bin/perl

# wp10_routines.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

use strict vars;
use Data::Dumper;
our $global_timestamp;
our $global_timestamp_wiki;
=head1 SYNOPSIS

Routines to update the local database from information on the wiki

=head1 FUNCTIONS

=over 

=item Standard parameters:

=over 

=item PROJECT

The name of a rated project

=item EXTRA

The hash ref returned by B<get_extra_assessments>()

=back

=cut

######################################################################
# i18n

# These two really should never change, regardless of which wiki it is
my $categoryNS = 14;
my $talkNS = 1;

my $Category = get_conf('category_ns');
my $Articles = get_conf('articles_label');
my $By_quality = get_conf('by_quality');
my $By_importance = get_conf('by_importance');
my $By_importance_alt = get_conf(by_importance_alt);

# XXX remove these after new schema is in place
$By_quality =~ s/ /_/g;
$By_importance =~ s/ /_/g;
$By_importance_alt =~ s/ /_/g;

my $Lang = get_conf('language');
my $Root_category = get_conf('root_cat');

my $Class = get_conf('class');
my $No_Class = get_conf('no_class');
my $Unassessed_Class = get_conf('unassessed_class');
my $Assessed_Class = get_conf('assessed_class');

my %Quality=%{get_conf('quality')};
my %Importance=%{get_conf('importance')};
my $ReviewCats=get_conf('review');

my @Months=("January", "February", "March", "April", "May", "June",
            "July", "August",  "September", "October", "November", 
            "December");

our $Opts;
my $NotAClass = $Opts->{'not-a-class'};

######################################################################

=item B<download_project_list>()

Download list of all participating projects from wiki

Returns array ref 
=cut

sub download_project_list {
  my ($projects, $res, $cat);

  $res = pages_in_category($Root_category,$categoryNS);

  $projects = [];

  foreach $cat ( @$res ) { 
    next unless ( $cat =~ m/\Q$By_quality\E/ );
    next if ( $Lang eq 'en' 
              && $cat =~ /\Q$Category\E:Articles \Q$By_quality\E/); 

    $cat =~ s/^\Q$Category\E://;
    $cat =~ s/_\Q$Articles\E_\Q$By_quality\E//;

    push @$projects, $cat;
  }

  return $projects;
}

#################################################################
=item B<download_project>(PROJECT)

Update assessment data for PROJECT

=cut

sub download_project {
  my $project = shift;

# Re-enabled bio projects on Oct 3, 2012 now that the system will use the API 
# to fetch their article lists (and also for any other "large" project)
#
# Keep an eye on email to see if the query killer is killing any of the 
# queries that cannot be done on the API
#
#  next if ( ( ! defined $ENV{'DO_BIO'}) && ($project =~ /biography/i));

  db_reconnect();

  if ( ! db_lock("PROJECT:$project") ) { 
    print "Cannot get lock for $project, exiting.\n";
    return;
  }

  print "\n-- Download ratings data for '$project'\n";
  my ($homepage, $parent, $extra, $shortname, $timestamp);

  my ($lt, $dt);

  eval {
# XXX - performance testing; will remove later
$lt = time();

    update_timestamps();

$dt = time() - $lt;
$lt = time();
#print "==> update_timestamps $dt sec\n";

    ($homepage, $parent, $extra, $shortname) = 
      get_extra_assessments($project);

$dt = time() - $lt;
$lt = time();
#print "==> get_extra_assessments $dt sec\

    $timestamp = db_get_project_timestamp($project);

$dt = time() - $lt;
$lt = time();
#print "==> get_project_timestamp $dt sec\n";

    download_project_assessments($project, $extra, $timestamp,'quality');

$dt = time() - $lt;
$lt = time();
print "==> download quality assessments $dt sec\n";

    download_project_assessments($project, $extra, $timestamp,'importance');

$dt = time() - $lt;
$lt = time();
print "==> download importance assessments $dt sec\n";

    db_cleanup_project($project);

$dt = time() - $lt;
$lt = time();
#print "==> db_cleanup_project $dt sec\n";

    update_project($project, $global_timestamp, $homepage,
                   $parent, $shortname);

$dt = time() - $lt;
$lt = time();
#print "==> update project $dt sec\n";

        # Update release version scores for this project
        # This assumes that the count of articles with an assessed
        # importance is accurate; it's ser via update_project()
        # Also this requires the ratings table is accurate, of course

    update_project_scores($project);

$dt = time() - $lt;
$lt = time();
#print "==> update project scores $dt sec\n";

        # This updates the global articles table
        # This must come after update_project because update_project
        # sets up the ratings for unassessed articles, which have to 
        # be right before this runs

    update_articles_table($project);

$dt = time() - $lt;
$lt = time();
#print "==> update articles table $dt sec\n";

if ( defined $ENV{'DRY_RUN'} ) { 
  print "DRY RUN - not committing changes\n";
} else { 
    db_commit();
}
$dt = time() - $lt;
$lt = time();
#print "==> commit $dt sec\n";

  };

  if ($@) {
    print "Transaction aborted (updating '$project'): $@  dbi:err: $DBI::err dbi::errstr: $DBI::errstr";
    db_rollback();
  }

  db_unlock("PROJECT:$project");

  return 0;
}

#################################################################

=item B<get_project_quality_categories>(PROJECT, EXTRA)

Make list of categories storing quality data for project

Each returned rating is a key in %Quality or a value in EXTRA

Returns hash ref: C<rating> => C<category>

=cut

sub get_project_quality_categories {
  my $project = shift;
  my $extra = shift;
  my $qcats = {};
  my $qual;

  print "--- Get project categories for $project by quality\n";

  # This line may need to be modified, depending on the naming convention
  # adopted by a particular wiki
  my $cat = $Category . ":" . $project . "_" . $Articles. "_" . $By_quality;

  my $cats = pages_in_category($cat, $categoryNS);
  my $value;
  my $replaces;

  print "$project $Articles\n";

#print Dumper(%Quality);

  foreach $cat ( @$cats ) { 
    print "SCAN '$cat'\n";

    if ( defined $extra->{$cat} ) { 
      $qual = $extra->{$cat}->{'title'};
      $qcats->{$qual} = $cat;
      $value = $extra->{$cat}->{'ranking'}; 
      $replaces = $extra->{$cat}->{'replaces'};
      print "\tCat (1) $qual $value $cat (extra)\n";
    } elsif ( $cat =~ /([A-Za-z]+)[\- _]/ ) {
      $qual=$1 . '-' . $Class; # e.g., FA-Class
      next unless (defined $Quality{$qual});
      $qcats->{$qual} = $cat;
      $value = $Quality{$qual};
      $replaces = $qual;
      print "\tCat (2) $qual $value $cat \n";
    } else {
      print "\tSkip qual '$cat'\n";
      next;
    }

    update_category_data( $project, $qual, 'quality', $cat, 
                          $value, $replaces);
  }

#exit; 
  return $qcats;
}

#################################################################

=item B<get_project_importance_categories>(PROJECT, EXTRA)

Make list of categories storing importance data for project

Each returned rating is a key in %Importance or a value in EXTRA

Returns hash ref: C<rating> => C<category>

=cut

sub get_project_importance_categories {
  my $project = shift;
  my $extra = shift;
  my $icats = {};
  my $imp;

  print "--- Get project categories for $project by importance\n";

  my $cat = $Category . ":" . $project. "_" . $Articles. "_" . $By_importance;

  my $cats = pages_in_category($cat, $categoryNS);
  my $value;

  # If 'by importance' is empty, the category tree might be under 
  # 'by priority', so we need to check there
  if ( 0 == scalar @$cats ) { 
    print "Fall back to 'priority' naming\n";
    $cat = $Category .":" . $project. "_" . $Articles. "_" . $By_importance_alt;
    $cats = pages_in_category($cat, $categoryNS);
  }

  foreach $cat ( @$cats ) { 
    if ( defined $extra->{$cat} ) { 
      $imp = $extra->{$cat}->{'title'};
      $icats->{$imp} = $cat;
      $value = $extra->{$cat}->{'ranking'};
      print "\tCat $imp $value $cat (extra)\n";
    } elsif ($cat =~ /([A-Za-z]+)[\- _]/) { 
      $imp=$1 . '-' . $Class; # e.g., Top-Class
      next unless (defined $Importance{$imp});
      $icats->{$imp} = $cat;
      $value = $Importance{$imp};
      print "\tCat $imp $value $cat \n";
    } else {
      print "Skip imp '$cat'\n";
      next;
    }
    update_category_data($project, $imp, 'importance', $cat, $value);
  }

  return $icats;
}

#################################################################

=item B<download_project_assessments>(PROJECT, EXTRA, TIMESTAMP, TYPE)

Download assessments for project and update database. 

TYPE is either C<quality> or C<importance>.

=cut

sub download_project_assessments {
  my $project = shift;
  my $extra = shift;
  my $timestamp = shift;
  my $type = shift;

  if ( $type ne 'quality' && $type ne 'importance' ) {
    die "Bad type '$type'";
  }

  print "Get stored $type ratings for $project\n";
  my $oldrating = get_project_ratings($project, $type);
  my $newrating = [];

  my $old_count  = scalar keys %$oldrating;
  my $large_project = 0;

  if (   ( defined $Opts->{'large_project_cutoff'}) 
      && ( 0 < $Opts->{'large_project_cutoff'})
      && ( ! defined $ENV{'BYPASS_LARGE_PROJECT_CHECK'} )  
      && ( $old_count < $Opts->{'large_project_cutoff'} ) ) { 
    $large_project = 1;
  }

  if ( $large_project == 1 ) { 
    print "Large project - using API to fetch article lists\n"; 
  }

  my $seen = {};
  my $moved = {};
  my $qcats;

  if ( $type eq 'quality' ) { 
    $qcats = get_project_quality_categories($project, $extra);
  } else { 
    $qcats = get_project_importance_categories($project, $extra);
  }

  my ($cat, $tmp_arts, $qual, $art, $d);

  if ( 0 == scalar keys %$qcats ) { 
    print "Project $project has no $type categories. Skipping them.\n";
    return;
  }

  foreach $qual ( keys %$qcats ) { 
    print "\nFetching list for $type $qual\n";

    $tmp_arts = pages_in_category_detailed($qcats->{$qual}, '*', $large_project);

    my $count = scalar @$tmp_arts;
    my $i = 0;

    foreach $d ( @$tmp_arts ) {
       $i++;
       $d->{'ns'}--;  # Talk pages are tagged, 
                      # we want the NS of the article itself
       next unless (acceptable_namespace($d->{'ns'}));

if ( $d->{'title'} =~ /incompleteness/ ) { 
  print "SEE: " . $d->{'title'} . "\n";
}

       $art = $d->{'ns'} . ":" . $d->{'title'};
       $seen->{$art} = 1;

       if ( ! defined $oldrating->{$art} ) {
         $d->{'art'} = $art;
         $d->{'rating'} = $qual;
         push @$newrating, $d;
         next;
       }

       if ( $oldrating->{$art} eq $qual ) {
         # No change
       } else {
         update_article_data($global_timestamp, $project,
                             $d->{'ns'}, $d->{'title'}, $type,
                             $qual, $d->{'timestamp'}, $oldrating->{$art} );
       }
    }
  }

  my ($ns, $title, $new_ns, $new_title, $new_timestamp, $new_art);

  my $totalArts = scalar keys %$oldrating;
  print "Total old arts: $totalArts\n";
  my $curArt = 0;
  foreach $art ( keys %$oldrating ) {
    $curArt++;
    next if ( exists $seen->{$art} );
    next if ( $oldrating->{$art} eq $NotAClass );

    # I believe the next thing will only happen on the
    # first run. Prove me wrong. 

    next if ( $type eq 'importance' && $oldrating->{$art} eq '' ); 

    print "NOT SEEN ($type: $curArt / $totalArts) '$art' " 
          . $oldrating->{$art} . "\n"; 

    ($ns, $title) = split /:/, $art, 2;

    ($new_ns, $new_title, $new_timestamp)
                      = get_new_name($ns, $title, $timestamp);

    if ( defined $new_ns ) {
      print "Moved to '$new_ns':'$new_title' at '$new_timestamp'\n";
      update_article_moved($global_timestamp, $project, $ns, $title,
                           $new_ns, $new_title, $new_timestamp);

      $new_art = $new_ns . ":" . $new_art;
      $moved->{$new_art} = 1;
#      next;
    }

    update_article_data($global_timestamp, $project, 
                        $ns, $title, $type,
                        $NotAClass, $global_timestamp_wiki, 
                        $oldrating->{$art});
  }

  # At this point, we are aware of which articles have been
  # moved since the last update of this project

   print "Total new arts: " . (scalar @$newrating) . "\n";

  $curArt = 0;
  foreach $d ( @$newrating ) {
   $curArt++;
    if ( 0 == $curArt % 500) { print "\t$curArt\n"; }

#    if ( ! defined $moved->{$d->{$art}} ) {
#         print "New: ". Dumper($d);
         update_article_data($global_timestamp, $project,
                             $d->{'ns'}, $d->{'title'}, $type,
                             $d->{'rating'}, $d->{'timestamp'}, 
                             $NotAClass);
#         exit;
#       }
  }

  return 0;
}

###################################################################

=item B<get_extra_assessments>(PROJECT)

Parse the ReleaseVersionParameters template from the main
category page for PROJECT

=cut

sub get_extra_assessments { 
  my $project = shift;

  my $cat = $Category. ":" . $project . "_" . $Articles . "_" . $By_quality;
  my $txt = content_section($cat, 0);

  print "See '$txt'\n";

  my @lines = split /\n+/, $txt;

  my $Starter = get_conf('template_start');
  my $Ender = get_conf('template_end');

  my ($homepage, $parent, $shortname, $line, $param, 
      $replaces, $num, $left, $right);
  my $extras = {};
  my $data = {};

  my $state = 0;
  # 0 - outside the template
  # 1 - inside the template
  # Can alternate back and forth

  # General parsing strategy is to assemble partial information into
  # the $extras hash, and then verify at the end that the info is
  # complete. If it is complete, it is added to $data to be returned

  foreach $line ( @lines ) {
    if ( $state == 0 ) { 
      if ( $line =~ /^\s*\Q$Starter\E\s*/ ) { 
        $state = 1;
      }
      next;
    } elsif ( $state == 1) { 
      if ( $line =~ /\s*}}/) { 
        $state = 0;
        next;
      }

      next unless ( $line =~ /\s*\|([^|=]*)\=([^|]*)$/ ); 
      $left = $1;
      $right = $2;

      if ( $left eq 'homepage') { 
        $homepage = substr($right, 0, 255);
      }

      if ( $left eq 'parent') { 
        $parent = substr($right, 0, 255);
      }

      if ( $left eq 'shortname') { 
        $shortname = substr($right, 0, 255);
      }

      if ( $left =~ /^extra(\d+)-(\w+)$/ ) {
        $num = $1;
        $param = $2;
        if ( ! defined $extras->{$num} ) { 
           $extras->{$num} = {};
        }
        $extras->{$num}->{$param} = $right;
      }       
      next;
    } else { 
      die "bad state $state\n";
    }
  }

  print "--\nWikiProject information from $Starter$Ender\n";

  if ( defined $homepage) { 
    print "Homepage: '$homepage'\n";
  }

  if ( defined $parent) { 
    print "Parent project: '$parent'\n";
  }

  if ( defined $shortname) { 
    print "Display name: '$shortname'\n";
  }

  print "Extra assessments:\n";

  foreach $num ( keys %$extras ) { 
    next unless ( defined $extras->{$num}->{'title'} );
    next unless ( defined $extras->{$num}->{'type'} );
    next unless ( defined $extras->{$num}->{'category'} );
    next unless ( defined $extras->{$num}->{'ranking'} );

    next unless ( $extras->{$num}->{'type'} eq 'quality'
                 || $extras->{$num}->{'type'} eq 'importance' );

#    if ( ! ( $extras->{$num}->{'category'} =~ /^Category:/ ) ) { 
#      $extras->{$num}->{'category'} = "Category:" .  
#                                       $extras->{$num}->{'category'};
#    }

   $extras->{$num}->{'category'} =~ s/^Category://;

   $extras->{$num}->{'category'} =~ s/ /_/g;

    $data->{$extras->{$num}->{'category'}} = $extras->{$num};
    print Dumper($extras->{$num}); 
  }

  return ($homepage, $parent, $data, $shortname);
}

#######################################################################

=item B<download_review_data>()

Download review data from wiki, which concerns FA, GA, etc. Update database.

=cut

sub download_review_data { 
  eval {
  print "HERE\n";
    download_review_data_internal();
    db_commit();
  };

  if ($@) {
    print "Transaction aborted (getting review data): $@  dbi:err: $DBI::err dbi::errstr: $DBI::errstr";
    db_rollback();
  }
}

#######################################################################

=item B<download_review_data_internal>()

Download review data from database. This function does not commit the
database.

=cut

sub download_review_data_internal {
  my (%rating);

  # Get older featured and good article data from database
  my ($oldrating) = get_review_data();

  my $seen = {};
  my $qcats = $ReviewCats;

  my ($cat, $tmp_arts, $qual, $art, $d);

  foreach $qual ( keys %$qcats ) { 
    print "\nFetching list for $qual\n";

    $tmp_arts = pages_in_category_detailed($qcats->{$qual});

    my $count = scalar @$tmp_arts;
    my $i = 0;

    foreach $d ( @$tmp_arts ) {
      $i++;
      $art = $d->{'title'};
      next unless ( $d->{'ns'} == $talkNS );
      $seen->{$art} = 1;

      # New entry
      if ( ! defined $oldrating->{$art} ) { 
        update_review_data($global_timestamp, $art, $qual, 
                           $d->{'timestamp'}, 'None');
        next;
      }

      # Old entry, although it could have been updated, so we need to check
      if ( $oldrating->{$art} eq $qual ) {
  # No change
      } else {
        update_review_data($global_timestamp, $art, $qual, 
                           $d->{'timestamp'}, $oldrating->{$art});
      } 
    }
  } 
  
  # Check if every article from the old listing is available
  foreach $art ( keys %$oldrating ) { 
    next if ( exists $seen->{$art} );   
#   print "NOT SEEN ($oldrating->{$art}) '$art' \n";
    remove_review_data($art, 'None', $oldrating->{$art});
  }
  return 0;
}

#######################################################################

=item B<download_release_data>()

Download release data from wiki, which is about release
versions such as WP 0.5. Update database.

=cut

sub download_release_data { 
  eval {
    download_release_data_internal();
    db_cleanup_releases();
    db_commit();
  };

  if ($@) {
    print "Transaction aborted (getting release data): $@  dbi:err: $DBI::err dbi::errstr: $DBI::errstr";
    db_rollback();
  }
}

#######################################################################

=item B<download_release_data_internal>()

Download release data from the database. This function does not
commit the database.

=cut

sub download_release_data_internal {
  my $cat = "Version 0.5 articles by category";
  my $suffix = " Version 0.5 articles";

  my $oldArts = db_get_release_data();
#  print Dumper($oldArts);

  my $res = pages_in_category($cat, $categoryNS);

  my ($type, $r, $page);
  my $seen = {};

  foreach $cat ( @$res ) {
    print "$cat\n";
    $type = $cat;
    $type =~ s/\Q$suffix\E$//;
    $type =~ s/^\Q$Category\E://;
    my $res = pages_in_category_detailed($cat);

    foreach $r ( @$res ) {
      next unless ( $r->{'ns'} == $talkNS);
      $page = $r->{'title'};

      if ( defined $oldArts->{$page}
           && $oldArts->{$page}->{'0.5:category'} eq $type ) {
      } else { 
#        print "New: $page // $type\n";
        db_set_release_data($page, '0.5', $type, $r->{'timestamp'});
      }
      $seen->{$page} = 1;
    }
  }

  foreach $page ( keys %$oldArts ) { 
    if ( ( ! defined $seen->{$page} )
        && $oldArts->{$page}->{'0.5:category'} ne 'None' ) { 
#      print "NOT SEEN: $page\n";
      db_set_release_data($page, '0.5', 'None', $global_timestamp_wiki);
    }
  }

}
#######################################################################

=item B<update_timestamps>( )

Update the internal timestamp variables to the current time.

=cut

sub update_timestamps {
  my $t = time();
  $global_timestamp = strftime("%Y%m%d%H%M%S", gmtime($t));
  $global_timestamp_wiki = strftime("%Y-%m-%dT%H:%M:%SZ", gmtime($t));
}

#######################################################################

=item B<get_new_name>(NS, TITLE, TIMESTAMP) 

Tryto get the current location of NS:TITLE, as if it 
has been moved or has become a redirect. Ignores any
moves before TIMESTAMP.

=cut

sub get_new_name { 

  my $ns = shift;
  my $title = shift;
  my $timestamp = shift;

  # First try to use move log
#print "GET MOVE LOG\n";
  my $moves = api_get_move_log($ns, $title);
#print "BACK\n";
  my $move;
  my $m_timestamp;
  foreach $move ( @$moves ) { 
#    print Dumper($move);

    $m_timestamp = $move->{'timestamp'};
    $m_timestamp =~ s/[-T:Z]//g;
    if ( $m_timestamp > $timestamp ) { 
      return ($move->{'dest-ns'}, $move->{'dest-title'}, 
              $move->{'timestamp'});
    }
  }

  # Second check for redirect
  my ($r_ns, $r_title, $r_timestamp) = api_resolve_redirect($ns, $title);
  if ( defined $r_ns ) { 
    return ($r_ns, $r_title, $r_timestamp);
  }

  return undef;

}

#######################################################################

=item B<acceptable_namespace>(NS) 

Used to blacklist undesired namespaces. 

Returns 1 if NS is an acceptable namespace for an assessed page,
for example namespace 0. Returns 0 for non-acceptable namespaces.

=cut

sub acceptable_namespace { 
  my $ns = shift;

  return 0 if ( $ns < 0 );
  return 0 if ( $ns == 2 );
  return 0 if ( 1 == $ns % 2 );

  return 1;
}

# Load successfully
1;

__END__
