#!/usr/bin/perl

# toolserver_api.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS
 
 Routines to update the local database from information 
 on the Wikimedia Toolserver

=head1 FUNCTIONS

=over
 
=cut

use strict;
use DBI;
use Encode;
use Data::Dumper;
use POSIX 'strftime';

our $Opts;
require 'read_conf.pl';

my  $Prefix;
my  $PrefixRev;

my $dbh = toolserver_connect($Opts);

my $RemoveUnderscores = 0;

#####################################################################

=item B<toolserver_connect>( )
 
 Establishes a connection with the toolserver's copy of the wiki's 
 database
 
 Returns a DBH object
 
=cut

sub toolserver_connect {
  my $opts = shift;

  die "No 'database_wiki_ts' given in database conf file\n"
    unless ( defined get_conf('database_wiki_ts'));

  if ( $opts->{'use_toolserver'} eq '0' ) { 
#     print "Not using toolserver\n";
     return;
    }
   
   my $connect = "DBI:mysql"
         . ":database=" . get_conf('database_wiki_ts');
   
   # For the enwiki_p db, this should be sql-s1
   if ( defined get_conf('host_wiki_ts') ) {
         $connect .= ":host=" . get_conf('host_wiki_ts') ;
   }
   
   
        my $username = get_conf('username') || "";
        my $password = get_conf('password') || "";

  if ( defined get_conf('credentials-toolserver') ) {
    $connect .= ":mysql_read_default_file=" 
    . get_conf('credentials-toolserver');
  }
  
  my $db = DBI->connect($connect, $username, $password,
  {'RaiseError' => 1, 
  'AutoCommit' => 0} )
  or die "Couldn't connect to database: " . DBI->errstr;
  
  get_prefixes(get_conf('database_wiki_ts'), $db);

        return $db;
}

#####################################################################

=item B<get_prefixes>(DB, DBH )
 
Loads a the namespace names of the "DB" wiki from the 
toolserver's global database into internal variables
 
 Parameters:
 
 DB: database name
 DBH: database handle
 
=cut

sub get_prefixes { 
  my $db = shift;
  my $dbh = shift;
  my $query = "SELECT ns_id, ns_name FROM p50380g50494_data.namespacename 
                 WHERE ns_type = 'primary' and dbname = ?";
  
  my $sth = $dbh->prepare($query);
  my $c = $sth->execute($db);
  
  my @row;
  
  while (@row = $sth->fetchrow_array()) {
    if ( $row[1] ne "" ) { 
      $row[1] .= ":";
    }
    $Prefix->{$row[0]} = $row[1];
    $PrefixRev->{$row[1]} = $row[0];
  }

## Left over from toolserer namespacename table
#  
#  die "No 'database_ts' given in database conf file\n"
#  unless ( defined get_conf('database_ts') );
#  
#  my $connect = "DBI:mysql" . ":database=" . get_conf('database_ts');
#  
#  if ( defined get_conf('host_ts') ) {
#    $connect .= ":host="     . get_conf('host_ts') ;
#  }
#
#        my $username = get_conf('username') || "";
#        my $password = get_conf('password') || "";
#  
#  if ( defined get_conf('credentials-toolserver') ) {
#    $connect .= ":mysql_read_default_file=" 
#    . get_conf('credentials-toolserver');
#  }
#  
#  my $dbt = DBI->connect($connect, $username, $password,
#  {'RaiseError' => 1, 
#  'AutoCommit' => 0} )
#  or die "Couldn't connect to database: " . DBI->errstr;  
#  my $sth = $dbt->prepare($query);
#  $dbt->disconnect();
}

######################################################################
=item B<toolserver_pages_in_category>(CATEGORY, [NS])
 
  Returns an array reference listing pages in CATEGORY
 
  CATEGORY _must_ be UTF-8 encoded
  
  The NS parmater, optional, is a numeric namespace for 
  filtering the results.
  
  The pages in the resulting array _do_ have the namespace
  prefix attached (for example C<Talk:Foo> and C<Wikipedia:Bar>)
  
  The titles returned are UTF-8 encoded
 
=cut
sub toolserver_pages_in_category { 
  my $cat = shift;
  my $ns = shift;
  
  my $query = "
  SELECT page_namespace, page_title  /* SLOW_OK */
  FROM page 
  JOIN categorylinks ON page_id = cl_from
  WHERE cl_to = ?";
  
  my @qparam = ($cat);
  
  if ( defined $ns ) {
    $query .= " AND page_namespace = ?";
    push @qparam, $ns;
  };

  my $sth = $dbh->prepare($query);
  my $t = time();
  my $r = $sth->execute(@qparam);
  print "\tListed $r pages in " . (time() - $t) . " seconds\n";
  
  my @row;
  my @results;
  my $title;
  while (@row = $sth->fetchrow_array) { 
    $title = $Prefix->{$row[0]} . $row[1];
    #    $title = decode("utf8", $title);
    if ( $RemoveUnderscores ) { 
      $title =~ s/_/ /g;
    }
    push @results, $title;
  }                             
  
  return \@results;
}

######################################################################
=item B<toolserver_pages_in_category_detailed>(CATEGORY, [NS]) 
 
 Returns a reference to an array of hashes, 
 one for each page in CATEGORY.
 
 The output format is
 
 {  'ns'        => NAMESPACE, 
 'title'     => TITLE,
 'pageid'    => PAGEID,
 'sortkey'   => SORTKEY,
 'timestamp' => TIMESTAMP }
 
 CATEGORY _must_ be UTF-8 encoded. 
 
 The NS parmater, optional, is a numeric namespace for 
 filtering the results.
 
 The page titles in the resulting array _do_not_ have the namespace
 prefix attached (for example, the page C<Talk:Foo> will show
 
 { 'ns' => '1',
 'title' => 'Foo',
 ...  }
 
 The data returned is all UTF-8 encoded.
  
=cut

sub toolserver_pages_in_category_detailed { 
  my $cat = shift;
  my $ns = shift;
  
  my $query = "
  SELECT page_namespace, page_title, page_id, cl_sortkey, cl_timestamp 
  FROM page  /* SLOW_OK */
  JOIN categorylinks ON page_id = cl_from
  WHERE cl_to = ?";
  
  my @qparam = ($cat);
  
  if ( defined $ns ) {
    $query .= " AND page_namespace = ?";
    push @qparam, $ns;
  };
  
  my $sth = $dbh->prepare($query);
  
  my $t = time();
  my $r = $sth->execute(@qparam);
  print "\tListed $r pages in " . (time() - $t) . " seconds\n";
  
  my @row;
  my @results;
  my $data;
  my $title;
  my $ts;
  while (@row = $sth->fetchrow_array) { 
    $data = {};
    $data->{'ns'} = $row[0];
    # obselete behavior
    #      $title =  $Prefix->{$row[0]} . $row[1];
    #      $title = decode("utf8", $title);
    
    $title = $row[1];
    if ( $RemoveUnderscores ) { 
      $title =~ s/_/ /g;
    }
    $data->{'title'} = $title;
    
    $data->{'pageid'} = $row[2];
    $data->{'sortkey'} = $row[3];
    
    $ts = $row[4];
    $ts =~ s/ /T/;
    $ts = $ts . "Z";
    #      print "T '$row[4]' '$ts'\n";
    
    $data->{'timestamp'} = $ts;
    push @results, $data;
  }    
  return \@results;
}

######################################################################
=item B<toolserver_resolve_redirect>(NS, TITLE)

Resolves a redirect from NS:TITLE. 

Returns undef if page is not a redirect, returns
(TARGET_NS, TARGET_TITLE) if it is.

=cut

sub toolserver_resolve_redirect { 
  my $ns = shift;
  my $title = shift;

  if ( $RemoveUnderscores ) { 
    $title =~ s/ /_/g;
  }

  my $query = "select rd_namespace, rd_title, page_touched from page 
               join redirect on page_id = rd_from 
                and page_title = ? and page_namespace = ?";

  my $sth = $dbh->prepare($query);
  my $r = $sth->execute($title, $ns);

  if ( $r == 1) { 
    my @row = $sth->fetchrow_array();
    if ( $RemoveUnderscores ) { 
      $row[1] =~ s/_/ /g;
    }
    return $row[0], $row[1], fix_timestamp($row[2]);
  }
  
  return undef;
}

######################################################################
=item B<toolserver_get_move_log>(NS, TITLE)

Gets move log entries for NS:TITLE 

Returns an array ref of log entries, sorted from newest to oldest

=cut

sub toolserver_get_move_log { 
  my $ns = shift;
  my $title = shift;

  if ( $RemoveUnderscores ) { 
    $title =~ s/ /_/g;
  }

  my $query = "select log_id, log_type, log_action, log_timestamp, 
                  user_name, log_namespace, log_title, log_comment, log_params 
               from logging 
               join user on log_user = user_id where log_namespace = ?
               and log_title = ?  and log_type = 'move' 
               order by log_timestamp DESC";

  my $sth = $dbh->prepare($query);
print "Executing query: '$query' '$ns' '$title' \n";
  my $r = $sth->execute($ns, $title);
print "back from query\n";
  my @row;

  my $results = [];
  my $data;
  my @row;

  while ( @row = $sth->fetchrow_array() ) { 

    if ( $RemoveUnderscores ) { 
      $row[4] =~ s/_/ /g;
      $row[6] =~ s/_/ /g;
      $row[7] =~ s/_/ /g;
    }

    $data = {};
    $data->{'logid'} = $row[0];
    $data->{'type'} = $row[1];
    $data->{'action'} = $row[2];
    $data->{'timestamp'} =  fix_timestamp($row[3]);
    $data->{'user'} = $row[4];
    $data->{'ns'} = $row[5];
    $data->{'title'} = $row[6];
    $data->{'comment'} = $row[7];

    my $art = $row[8];
    my $ns = 0;
    my $n;

    foreach $n ( keys %$PrefixRev ) { 
      next if ( $n eq "");

      if ( $art =~ /^\Q$n\E/ ) {
        $ns = $PrefixRev->{$n};
        $art =~ s/^\Q$n\E//;
        last;
      }
    }
    $data->{'dest-ns'} = $ns;
    $data->{'dest-title'} = $art;
    push @$results, $data;
  }

  return $results;
}


sub fix_timestamp { 
  my $t = shift;

  return substr($t, 0, 4) . "-" . substr($t, 4, 2) . "-"
           . substr($t, 6, 2) . "T" . substr($t, 8, 2) 
           . ":" . substr($t, 10, 2) . ":" . substr($t, 12, 2)  . "Z";
}

1;
