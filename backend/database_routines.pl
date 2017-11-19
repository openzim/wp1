#!/usr/bin/perl

# database_routines.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

Routines to connect, query, and commit to the database

Note that autocommit is turned off, so C<db_commit()> must
be called to finish each transaction.

=head1 FUNCTIONS

=over 

=item Standard parameters:

=over 

=item TIMESTAMP

Current time

=item PROJECT

The name of a rated wikiproject

=item NAMESPACE

The namespace of ARTICLE

=item ARTICLE

The name of an article

=item RTYPE

Either 'quality' or 'importance'

=item RATING

A quality or importance rating name, e.g. Start-Class, Top-Class

=item REV_TIMESTAMP

A timestamp used to describe a particular revision of an article; used in 
conjunction with the ARTICLE parameter

=back

=cut

use strict vars;
use Data::Dumper;

$Data::Dumper::Sortkeys = 1;

our $Opts;
my $NotAClass = $Opts->{'not-a-class'};

use DBI;
my $dbh = db_connect($Opts);

my $TablePrefix;


#######################################################################

=item B<update_article_data>(TIMESTAMP, PROJECT, NAMESPACE,
ARTICLE, RTYPE, RATING, REV_TIMESTAMP, PREVIOUS_RATING)

Top-level routine for updating data for a single article. Updates the
I<ratings> table and I<logging> table. 

Parameters:

=over

=item PREVIOUS_RATING

Previous rating value, used for I<logging>

=back

=cut

sub update_article_data {
  my $global_timestamp = shift;
  my $project = shift;
  my $ns = shift;
  my $art = shift;
  my $table = shift;
  my $value = shift;
  my $timestamp = shift;
  my $oldvalue = shift;

  die "Bad table: $table" 
    unless ( ($table eq 'quality') || ($table eq 'importance') );

#  print "U:" . "$project // $art // $timestamp // $value // was '$oldvalue'\n";

#  $art = encode("utf8", $art);
#  $project = encode("utf8", $project);
#  $value = encode("utf8", $value);
#  $oldvalue = encode("utf8", $oldvalue);

# XXX HACK

  my $sth_insert_logging = $dbh->prepare_cached("INSERT INTO " . db_table_prefix() . "logging " . 
                                         "values (?,?,?,?,?,?,?,?) 
                                          ON DUPLICATE KEY UPDATE l_article = l_article");


#  print "U: '$project' '$art' '$ns' '$table'\n";

  $sth_insert_logging->execute($project, $ns, $art, $table, $global_timestamp,
                               $oldvalue, $value, $timestamp);


  update_article_rating_data($project, $ns, $art, $table, $value, $timestamp);
}

#######################################################################

=item B<update_article_moved>(TIMESTAMP, OLD_NAMESPACE, OLD_ARTICLE,
                              NEW_NAMESPACE, NEW_TITLE, REV_TIMESTAMP)

Top-level routine for logging that an article has been moved.
Updates the I<moves> table and the <logging> table;

Does not update any data for the for new name, only updates for old name.

=cut

sub update_article_moved {
  my $global_timestamp = shift;
  my $project = shift;
  my $old_ns = shift;
  my $old_art = shift;
  my $new_ns = shift;
  my $new_art = shift;
  my $rev_timestamp = shift;

  my ($r, $sth, @row);

#  print "N: $new_ns:$new_art\n";

  $sth = $dbh->prepare("SELECT count(*) FROM  " . db_table_prefix() . "moves       
                                WHERE m_timestamp = ? 
                                  AND m_old_namespace = ?
                                  AND m_old_article = ?");
  
  $sth->execute($rev_timestamp, $old_ns, $old_art);
  @row = $sth->fetchrow_array();
  $r = $row[0];

  if ( '0' eq $r ) { 
    print "MOVES says '$r'\n";
    $sth = $dbh->prepare("INSERT INTO " . db_table_prefix() . "moves " . 
         "values (?,?,?,?,?)");

    $r = $sth->execute($rev_timestamp, $old_ns, $old_art, $new_ns, $new_art);
    print "MOVES inserted $old_ns:$old_art => " 
        . " $new_ns:$new_art $rev_timestamp: result $r\n";
  } else { 
    print "MOVES already shows $old_ns:$old_art "
        . " => $new_ns:$new_art $global_timestamp: '$r'\n";
  }

  $sth = $dbh->prepare("SELECT count(*) FROM " . db_table_prefix() . "logging             
                                WHERE l_project = ?
                                  AND l_namespace = ?
                                  AND l_article = ? 
                                  AND l_action = ? 
                                  AND l_revision_timestamp = ?");

  $r = $sth->execute($project, $old_ns, $old_art, "moved", $rev_timestamp);
  @row = $sth->fetchrow_array();
  $r = $row[0];

  if ( '0' eq $r ) { 
    $sth = $dbh->prepare("INSERT INTO " . db_table_prefix() . "logging " . 
                                "values (?,?,?,?,?,?,?,?) on duplicate key update l_project = l_project");
 
    $r = $sth->execute($project, $old_ns, $old_art, "moved", 
                       $global_timestamp, "", "", $rev_timestamp);
  
    print "LOG inserted logging entry for move: result '$r'\n";
  } else { 
    print "LOG already has logging entry for move: '$r'\n";
  }

  # Ratings for new article will be picked up separately
}


#######################################################################

=item B<update_category_data>
(PROJECT, RATING, RTYPE, CATEGORY, RANKING, REPLACEMENT)

Update information about a rating for a project

=over

=item CATEGORY

The wikipedia category listing these articles.
e.g. C<Category:B-Class mathematics articles>

=item RANKING

A numeric sort ranking used to sort tables

=item REPLACEMENT

A standard rating (e.g. B-Class) used to replcae this rating in
global statistics

=back

=cut

sub update_category_data { 
  my $project = shift;
  my $rating = shift;
  my $type = shift;
  my $category = shift;
  my $ranking = shift;
  my $replacement = shift;

  if ( ! defined $replacement ) { 
    $replacement = $rating;
  }

  my $sth = $dbh->prepare (
       "UPDATE  " . db_table_prefix() . "categories SET c_category = ?, c_ranking = ?, c_replacement = ?
        WHERE c_project = ? and c_rating= ? and c_type = ? "
     );

  my $count = $sth->execute($category, $ranking, $replacement, 
                            $project, $rating, $type);

  if ( $count eq '0E0' ) { 
    $sth = $dbh->prepare ("INSERT INTO " . db_table_prefix() . "categories VALUES (?,?,?,?,?,?)");
    $count = $sth->execute($project, $type, $rating, 
                           $replacement, $category, $ranking);
  }

}

######################################################################
## Internal function to update the ratings table when article is 
## reassessed

=item B<update_article_rating_data>(PROJECT, ARTICLE, RTYPE, RATING, REV_TIMESTAMP)

Update I<ratings> table for a single article

=cut

sub update_article_rating_data { 
  my $project = shift;
  my $ns = shift;
  my $article = shift;
  my $type = shift;
  my $rating = shift;
  my $rating_timestamp = shift;

  if ( !( $type eq 'importance' || $type eq 'quality' ) ) { 
    die "Bad ratings type:  $type\n";
  }

  my $query = "UPDATE  " . db_table_prefix() . "ratings SET r_$type = ?, "
            . "r_" . $type . "_timestamp = ?  " 
      . "WHERE r_project = ? and r_namespace = ? and r_article = ?";

  my $sth = $dbh->prepare_cached($query);

  my $count = $sth->execute($rating, $rating_timestamp,
          $project, $ns, $article);

  if ( $count eq '0E0' ) { 
    my ($quality, $importance, $qualityTS, $importanceTS);
    if ( $type eq 'quality' ) {
      $quality = $rating; 
      $qualityTS = $rating_timestamp;
    }
    if ( $type eq 'importance' ) { 
      $importance = $rating; 
      $importanceTS = $rating_timestamp;
    }
    $sth = $dbh->prepare ("INSERT INTO " . db_table_prefix() . "ratings VALUES (?,?,?,?,?,?,?,0)");
    $count = $sth->execute($project, $ns, $article, $quality, 
                           $qualityTS, $importance, $importanceTS);
  }
}

############################################################

=item B<update_articles_table>(PROJECT)

Update I<articles> table, which stores the highest quality and
importance assigned to an article. Must be run after updating
a project, to keep database coherent. 

=cut

sub update_articles_table { 
  my $project = shift;

  my $query = "
REPLACE INTO " . db_table_prefix() . "global_articles
SELECT art, max(qrating), max(irating), max(score)
FROM
( SELECT art, qrating, irating, score
  FROM
    (SELECT a_article as art, a_quality as qrating, a_importance as irating, 
            a_score as score
       FROM " . db_table_prefix() . "global_articles
       JOIN " . db_table_prefix() . "ratings 
           ON r_namespace = 0 AND r_project = ? AND a_article = r_article
    ) AS tableone
  UNION
    (SELECT r_article as art, qual.gr_ranking as qrating, imp.gr_ranking as irating, 
            r_score as score
      FROM  " . db_table_prefix() . "ratings
      JOIN  " . db_table_prefix() . "categories as ci ON r_project = ci.c_project
        AND ci.c_type = 'importance' AND r_importance = ci.c_rating
      JOIN  " . db_table_prefix() . "categories as cq ON r_project = cq.c_project
        AND cq.c_type = 'quality' AND r_quality = cq.c_rating
      JOIN  " . db_table_prefix() . "global_rankings AS qual ON qual.gr_type = 'quality' 
                              AND qual.gr_rating = cq.c_replacement
      JOIN  " . db_table_prefix() . "global_rankings AS imp  ON imp.gr_type = 'importance' 
                                 AND imp.gr_rating = ci.c_replacement
    WHERE r_namespace = 0 and r_project = ? )
) as tabletwo
GROUP BY art /* SLOW_OK */;";

# SLOW_OK indeed

  my $sth = $dbh->prepare($query);

  print "Updating global articles table using data from $project\n";
  my $start = time();
  my $r = $sth->execute($project, $project);
  print "  Result: $r rows in "  .(time() - $start) . " seconds\n";
  return;
}

############################################################

=item B<update_project>(PROJECT, TIMESTAMP, WIKIPAGE, PARENT, SHORTNAME)

Update the project table with data for PROJECT

Parameters:

=over

=item TIMESTAMP

when PROJECT was last updated

=item WIKIPAGE

wikipedia homepage for PROJECT

=item PARENT

Parent project, or undef

=item SHORTNAME

Abbreviated name to display for PROJECT

=back

=cut

sub update_project { 
  my $project = shift;
  my $timestamp = shift;
  my $wikipage = shift;
  my $parent = shift;
  my $shortname = shift;

  my $proj_count;
  my @row;

  my $sth = $dbh->prepare("SELECT COUNT(r_article) FROM  " . db_table_prefix() . "ratings " 
                        . "WHERE r_project = ?");
  $sth->execute($project);
  @row = $sth->fetchrow_array();
  $proj_count = $row[0];

# XXX - hard coded names to detect unassessed quality and importance

  my $sth_qcount = $dbh->prepare("SELECT COUNT(r_article) FROM " . db_table_prefix() . "ratings "
          . "WHERE r_project = ? AND (r_quality = '$NotAClass' 
                                       OR r_quality= 'Unassessed-Class')");

  $sth_qcount->execute($project);
  @row = $sth_qcount->fetchrow_array();
  my $qcount = $proj_count - $row[0];
  print "Quality-assessed articles: $qcount\n";

  my $sth_icount = $dbh->prepare("SELECT COUNT(r_article) FROM " . db_table_prefix() . "ratings "
         . "WHERE r_project = ? AND (r_importance='$NotAClass' 
                     OR r_importance = 'Unknown-Class'
                     OR r_importance = 'Unassessed-Class')");
  $sth_icount->execute($project);

  @row = $sth_icount->fetchrow_array();
  my $icount = $proj_count - $row[0];
  print "Importance-assessed articles: $icount\n";
  
  my $sth = $dbh->prepare ("UPDATE  " . db_table_prefix() . "projects SET p_timestamp  = ?, "
                         . " p_wikipage = ?, p_parent = ?, p_shortname = ?," 
                         . " p_count  = ?, p_qcount = ?, p_icount  = ? "
                         . " WHERE p_project = ?" );

  my $count = $sth->execute($timestamp, $wikipage, $parent, 
                            $shortname, $proj_count, $qcount, 
          $icount, $project);

  if ( $count eq '0E0' ) { 
    $sth = $dbh->prepare ("INSERT INTO  " . db_table_prefix() . "projects VALUES (?,?,?,?,?,?,?,?,0,'00000000000000')");
    $count = $sth->execute($project, $timestamp, $wikipage, 
                           $parent, $shortname, $proj_count, $qcount, $icount);
  }

  update_category_data( $project, $NotAClass, 'quality', 
                        '', 21, 'Unassessed-Class'); 
  update_category_data( $project, $NotAClass, 'importance',
                        '', 21, 'Unknown-Class');

}

###########################################################
=item B<db_set_upload_timestamp>(PROJECT, TIMESTAMP)

Sets the upload timestamp of PROJECT to TIMESTAMP.

=cut

sub db_set_upload_timestamp { 
  my $project = shift;
  my $timestamp = shift;

  my $sth = $dbh->prepare ("UPDATE  " . db_table_prefix() . "projects SET p_upload_timestamp  = ?  "
                         . " WHERE p_project = ?" );

  my $r = $sth->execute($timestamp, $project);
  print "DB set upload timestamp for '$project' to '$timestamp': result $r\n";
}


############################################################
## Query project table for a particular project

=item B<project_exists>(PROJECT)

Returns true if PROJECT exists in the I<projects> table, false otherwise

=cut

sub project_exists {
  my $project = shift;
#  $project = encode("utf8", $project);

  my $sth = $dbh->prepare ("SELECT * FROM " . db_table_prefix() . "projects WHERE p_project = ?");
  my $r = $sth->execute($project);

  return ($r == 1 ? 1 : 0);
}

############################################################

=item B<get_project_ratings>(PROJECT, TYPE)

Fetch assessments of TYPE for PROJECT. 

Returns a hash: C<namespace:article> => C<rating>

=cut

sub get_project_ratings {
  my $project = shift;
  my $type = shift;

  if ( ! ( $type eq 'quality' || $type eq 'importance') ) { 
    die "Bad type: $type\n";
  }

  print "Getting $type ratings for $project from database\n";

#  $project = encode("utf8", $project);

  my $sth = $dbh->prepare("SELECT r_namespace, r_article, r_$type " 
                        . "FROM  " . db_table_prefix() . "ratings WHERE r_project = ?");
  $sth->execute($project);

  my $ratings = {};
  my @row;
  my $art;
  while ( @row = $sth->fetchrow_array() ) {
    $art = $row[0] . ":" . $row[1];
    $ratings->{$art} = $row[2];
  }

  print "Fetched: " . (scalar keys %$ratings) . " for type '$type' project '$project'\n";
  return $ratings;
}

###########################################################

=item B<db_commit>()

Commit current DB transaction

=cut

sub db_commit { 
  print "Commit changes to database\n";
  $dbh->commit();
  return 0;
}

############################################################

=item B<db_rollback>()

Rollback current DB transaction

=cut

sub db_rollback { 
  print "Rollback database\n";
  $dbh->rollback();
  return 0;
}

############################################################

=item B<db_cleanup_project>(PROJECT)

Deletes data for articles that were once assessed but aren't
anymore. Also gets rid of NULL values in I<ratings> table.

First, delete rows from I<ratings> table for PROJECT where
quality and importance are both nonexistent or unrecognized classes.
Then replace any NULL I<ratings> quality or importance values
with a sentinel value.

=cut

sub db_cleanup_project {
  my $proj = shift;
  print "Cleanup $proj\n";

  # If both quality and importance are NULL, that means the article
  # was once rated but isn't any more, so we delete the row

  my $sth = $dbh->prepare("delete from  " . db_table_prefix() . "ratings " 
                        . "where r_quality = '$NotAClass' " 
                        . " and r_importance = '$NotAClass' "
                        . " and r_project = ?");
  my $count = $sth->execute($proj);
  print "  Deleted articles: $count\n";

  # It's possible for the quality to be NULL if the article has a 
  # rated importance but no rated quality (not even Unassessed-Class).
  # This will always happen if the article has a quality rating that the 
  # bot doesn't recognize. Change the NULL to sentinel value.

  $sth = $dbh->prepare("update " . db_table_prefix() . "ratings set r_quality = '$NotAClass', " 
                     . "r_quality_timestamp = r_importance_timestamp "
                     . "where isnull(r_quality) and r_project = ?");
  $count = $sth->execute($proj);
  print "  Null quality rows: $count\n";

  # Finally, if a quality is assigned but not an importance, it is
  # possible for the importance field to be null. Set it to 
  # $NotAClass in this case.

  $sth = $dbh->prepare("update " . db_table_prefix() . "ratings set r_importance = '$NotAClass', " 
                     . "r_importance_timestamp = r_quality_timestamp "
                     . "where isnull(r_importance) and r_project = ?");
  $count = $sth->execute($proj);
  print "  Null importance rows: $count\n";

  return 0;
}

############################################################

=item B<db_connect>()

Connect to DB. Runs automatically when file is loaded.

Parameters:

=over

=item OPTS

The options hash returned by read_conf()

=back

=cut

sub db_connect {
  my $opts = shift;

  print "Called db_connect\n";

  $TablePrefix = $opts->{'database_table_prefix'};

  die "No database given in database conf file\n"
    unless ( defined $opts->{'database'} );

#if ( $opts->{'use_toolserver'} eq '0' ) { 
#  print "Not using toolserver\n";
#  return;
#}

  my $connect = "DBI:mysql"
           . ":database=" . $opts->{'database'};

  if ( defined $opts->{'host'} ) {
    $connect .= ";host="     . $opts->{'host'} ;
  }

  # timeouts
  $connect .= ";mysql_connect_timeout=3600;mysql_write_timeout=3600;mysql_read_timeout=3600";

  if ( defined $opts->{'credentials-readwrite'} ) {
    $opts->{'password'} = $opts->{'password'} || "";
    $opts->{'username'} = $opts->{'username'} || "";

    $connect .= ":mysql_read_default_file=" 
              . $opts->{'credentials-readwrite'};
  }

#  print "Connect: '$connect'\n";

  my $connect_max = 100;
  my $connect_count = 0;
  my $db;

  while ( 1 ) {
    $connect_count++;
    print ".. Connect to database, try $connect_count of $connect_max\n";
  
    $db = DBI->connect($connect, 
                        $opts->{'username'}, 
                        $opts->{'password'},
                       { # 'RaiseError' => 1, 'PrintError'=>0, 
                        'AutoCommit' => 0} )
       or die "Couldn't connect to database: " . DBI->errstr;

     if ( db_test_query($db) ) { 
       print ".. Successful\n";
#       sleep 5;
       last;
     } else { 
       print ".. Not successful\n";
       sleep 60;
     }
  }

#  $db->{'RaiseError'} = 'on'; # die on DB error
#  $db->{HandleError} = sub { confess(shift) };

  $db->{mysql_auto_reconnect} = 1;

  return $db;
}

############################################################

=item B<db_list_projects>()

Returns an array ref containing all projects names in
I<projects> table. They will be sorted from least recently
updated to most recently updated. 

=cut

sub db_list_projects { 
  my $projects = [];

  my $sth = $dbh->prepare("SELECT * FROM " . db_table_prefix() . "projects " 
                        . "order by p_timestamp asc;");
  $sth->execute();

  my @row;
  while ( @row = $sth->fetchrow_array ) { 
    push @$projects, $row[0];
  }

  return $projects;
}

###########################################################

=item B<db_get_project_details>()

Returns a hash reference:

 PROJECT => { 'count' => COUNT, 
              'timestamp' => TIMESTAMP }

=cut

sub db_get_project_details { 

  my $sth = $dbh->prepare("SELECT p_project, p_timestamp, p_count, p_upload_timestamp
                           FROM " . db_table_prefix() . "projects;");
  $sth->execute();

  print "GET PROJECT DETAILS\n";

  my ($proj, $count, $timestamp, $timestamp_u);

  my $data ={};

  my @row;
  while( @row = $sth->fetchrow_array() ){
    $proj = $row[0];
    $timestamp = $row[1];
    $count = $row[2];
    $timestamp_u = $row[3];

    $data->{$proj} = {};
    $data->{$proj}->{'count'} = $count;
    $data->{$proj}->{'timestamp'} = $timestamp;
    $data->{$proj}->{'upload_timestamp'} = $timestamp_u;
  }

  return $data;
}


############################################################
=item B<db_get_project_timestamp>()

Returns the last time PROJECT was updated, or undef if
project was never updated.

=cut

sub db_get_project_timestamp { 
  my $proj = shift;

  my $sth = $dbh->prepare("SELECT p_timestamp FROM " . db_table_prefix() . "projects
                           WHERE p_project = ?");
  $sth->execute($proj);
  
  my @row = $sth->fetchrow_array();
  return $row[0];
}


############################################################

=item B<update_review_data>(TIMESTAMP, ARTICLE, RATING, REV_TIMESTAMP,
PREVIOUS_RATING)

Update review status (FA, FL, GA) for ARTICLE.

=cut

sub update_review_data {
  # Process all the parameters
  my $global_timestamp = shift;
  my $art = shift;
  my $value = shift;
  my $timestamp = shift;
  my $oldvalue = shift;
  
  unless ( ($value eq 'GA') || ($value eq 'FA') || ($value eq 'FL') ) {
    print "Unrecognized review state: $value \n"; 
    return -1;
  };
    
  my $sth = $dbh->prepare ("UPDATE  " . db_table_prefix() . "reviews SET rev_value = ?, " 
  . "rev_timestamp = ? WHERE rev_article = ?");
  
  # Executes the UPDATE query. If there are no entries matching the 
        # article's name in the table, the query will return 0, allowing us 
        # to create an INSERT query instead.

  my $count = $sth->execute($value, $timestamp, $art);
  
  if ( $count eq '0E0' ) { 
    $sth = $dbh->prepare ("INSERT INTO " . db_table_prefix() . "reviews VALUES (?,?,?)");
    $count = $sth->execute($value, $art, $timestamp);
  }
  
#  print "U:" . "$art // $value // $timestamp // was '$oldvalue'\n";
  
}

############################################################
## Probably needs to be merged with update_review_data()

=item B<remove_review_data>(ARTICLE, RATING, PREVIOUS_RATING)

Removes ARTICLE from I<reviews> table. Asserts RATING='None'.

=cut

sub remove_review_data {
  # Process all the parameters
  my $art = shift;
  my $value = shift;
  my $oldvalue = shift;

  unless ( ($value eq 'None') ) {
    print "Unrecognized review state: $value \n"; 
    return -1;
  }

  my $sth = $dbh->prepare ("DELETE FROM " . db_table_prefix() . "reviews
                                  WHERE rev_value = ? AND rev_article = ?");
  # Executes the DELETE query. 
  my $count = $sth->execute($oldvalue, $art);

#  print "U:" . "$art // $value // removed // was '$oldvalue'\n";

}

############################################################

=item B<get_review_data>(RATING)

Fetch articles with review status RATING

Returns a hash ref ARTICLE => RATING

=cut

sub get_review_data {
  my $value = shift;
  my $sth;

  print "db review\n";

  if ( ! defined $value ) {
    $sth = $dbh->prepare ("SELECT rev_article, rev_value
                           FROM " . db_table_prefix() . "reviews");
    $sth->execute();
  } else {
    $sth = $dbh->prepare ("SELECT rev_article, rev_value
                           FROM " . db_table_prefix() . "reviews WHERE rev_value = ?");
    $sth->execute($value);
  }

  print "  back from db\n";

  # Iterate through the results
  my $ratings = {};
  my @row;
  while ( @row = $sth->fetchrow_array() ) {
    $ratings->{$row[0]} = $row[1];
  }

  print "db review done\n";

  return $ratings;
}

############################################################

=item B<db_get_release_data>()

Get data about released articles from I<releases>

Returns a hash reference:

 ARTICLE => { '0.5:category' => CAT,
              '0.5:timestamp' => TIMESTAMP }

=cut

sub db_get_release_data {
  my $sth;

  $sth = $dbh->prepare ("SELECT * FROM " . db_table_prefix() . "releases");
  $sth->execute();

  my @row;
  my $data = {};
  my ($art, $cat, $timestamp);

  while ( @row = $sth->fetchrow_array() ) {
    $timestamp = $row[2];
    $data->{$art} = {};
    $data->{$art}->{'0.5:category'} = $cat;
    $data->{$art}->{'0.5:timestamp'} = $timestamp;
  }

  return $data;
}

############################################################

=item B<db_set_release_data>(ARTICLE, RELEASE, CATEGORY, REV_TIMESTAMP)

<description>

Parameters:

=over

=item RELEASE

The name of the relase. Only C<0.5> is supported.

=item CATEGORY

The release category - C<Arts> etc.

=back

=cut

sub db_set_release_data { 
  my $art = shift;
  my $type = shift;
  my $cat = shift;
  my $timestamp = shift;

  if ( $type ne '0.5' ) { 
    die "Bad type: $type\n";
  }

  my $sth = $dbh->prepare("UPDATE  " . db_table_prefix() . "releases
                           SET rel_0p5_category = ?, rel_0p5_timestamp = ?
                           WHERE rel_article = ?");
  my $res = $sth->execute($cat, $timestamp, $art);

  if ( $res eq '0E0' ) { 
       $sth = $dbh->prepare("INSERT INTO  " . db_table_prefix() . "releases VALUES (?,?,?)");
       $sth->execute($art, $cat, $timestamp);
  }                     

}

############################################################

=item B<db_cleanup_releases>()

Remove articles from I<releases> table that are no longer 
included in any release versions.

=cut

sub db_cleanup_releases { 
  my $sth = $dbh->prepare("DELETE FROM  " . db_table_prefix() . "releases 
                           WHERE rel_0p5_category = 'None'");

  my $count = $sth->execute();

  print "Cleanup releases table: $count rows removed\n";
}

############################################################

=item B<db_lock>(LOCKNAME)

Gets an advisory lock from the database. Does not block.

Returns true if the lock was acquired, false otherwise.

=cut

sub db_lock {
  my $lock = shift;

  my $sth = $dbh->prepare("SELECT GET_LOCK(?,0)");
  my $r = $sth->execute($lock);
  my @row = $sth->fetchrow_array();
  return $row[0];
}

=item B<db_unlock>(LOCKNAME)

Release an advisory lock you got from C<db_lock>

=cut

sub db_unlock {
  my $lock = shift;
  my $sth = $dbh->prepare("SELECT RELEASE_LOCK(?)");
  my $r = $sth->execute($lock);
  my @row = $sth->fetchrow_array();
  return $row[0];
}

############################################################

=item B<update_project_scores>(PROJECT)

Update the release version scores for articles in a project.
Requires that the icount field in the projects table is accurate.

=cut

sub update_project_scores {
  my $project = shift;

  print "SCORES '$project'\n";

  my $query;
  my $res;  

  my $sth = $dbh->prepare("select p_icount from  " . db_table_prefix() . "projects
                           where p_project = ?");
  $res = $sth->execute($project);
  my @r = $sth->fetchrow_array();
  
  print "Updating release version scores for '$project'\n";


  if ( $r[0] > 0 ) { 
    print "  Detected that project uses importance ratings\n";

    $query = "update " . db_table_prefix() . "ratings 
      join " . db_table_prefix() . "projects on r_project = p_project 
      left join  " . db_table_prefix() . "selection_data on r_namespace = 0 
         and r_article = sd_article 
      left join  " . db_table_prefix() . "categories as cq on cq.c_project = p_project
         and cq.c_rating = r_quality and cq.c_type = 'quality'
      left join  " . db_table_prefix() . "categories as ci on ci.c_project = p_project
         and ci.c_rating = r_importance and ci.c_type = 'importance'
                  left join  " . db_table_prefix() . "global_rankings as gq on gq.gr_type = 'quality' 
                                     and gq.gr_rating = cq.c_replacement
                  left join  " . db_table_prefix() . "global_rankings as gi on gi.gr_type = 'importance' 
                                     and  gi.gr_rating = ci.c_replacement
   set r_score =  floor(
            if( isnull(gi.gr_ranking) OR gi.gr_ranking = 0, 4/3, 1)
                * (     50*if( sd_hitcount > 0, log10(sd_hitcount),  0) 
                     + 100*if(sd_pagelinks > 0, log10(sd_pagelinks), 0) 
                     + 250*if(sd_langlinks > 0, log10(sd_langlinks), 0) 
                  )
            + if(isnull(gi.gr_ranking), 0, gi.gr_ranking)
            + if(isnull(gq.gr_ranking), 0, gq.gr_ranking)
	+ if ( 0 = p_scope, 500, 0.5*p_scope)  ) - 500
      where r_project = ? and r_namespace = 0 /* SLOW_OK */;";
   }  else { 
       print "  Detected that project does not use importance ratings\n";

    $query = "update " . db_table_prefix() . "ratings 
       join " . db_table_prefix() . "projects 
                 on r_project = p_project 
       left join  " . db_table_prefix() . "selection_data on r_namespace = 0 
                  and r_article = sd_article 
       left join  " . db_table_prefix() . "global_rankings as gq on gq.gr_type = 'quality' 
                 and gq.gr_rating = r_quality 
       set r_score = floor(
             4/3 * (    50*if( sd_hitcount > 0, log10(sd_hitcount),  0) 
                     + 100*if(sd_pagelinks > 0, log10(sd_pagelinks), 0) 
                     + 250*if(sd_langlinks > 0, log10(sd_langlinks), 0) 
                   )
             + if(isnull(gq.gr_ranking), 0, gq.gr_ranking)
	+ if ( 0 = p_scope, 500, 0.5*p_scope)  ) - 500
      where r_project = ? and r_namespace = 0 /* SLOW_OK */;";
  }

#   print "QUERY: $query\n\n";

   $sth = $dbh->prepare($query);   
   my $time = time();
   $res = $sth->execute($project);
   $time = time() - $time;
   print "  Result: $res rows in $time seconds\n";

}
############################################################

=item B<database_handle>()

Return the Perl DBI database handle

=cut

sub database_handle { 
  return $dbh;
}

############################################################

sub db_table_prefix { 

  return $TablePrefix;

}


sub db_reconnect { 
  print "Reconnecting to database\n";  
  $dbh->commit();
  $dbh->disconnect();
  $dbh = db_connect($Opts);
}


# This is a hack to test whether the database is connected and functional

sub db_test_query { 
  my $dbhtmp = shift;

  my $testq = "select p_count from " . db_table_prefix() . 
              "projects where p_project ='Mathematics'";
  my $sth = $dbhtmp->prepare($testq);
  $sth->execute();
  my @r = $sth->fetchrow_array();
  if ( $r[0] > 0) { 
    return 1;
  } else { 
    return 0;
  }
}

# Load successfully
1;

__END__
