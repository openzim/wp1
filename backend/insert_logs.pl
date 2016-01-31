#!/usr/bin/perl

# insert_logs.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

require 'read_conf.pl';
my $Opts = read_conf();
my $NotAClass = $Opts->{'not-a-class'};

use DBI;
my $dbh = db_connect($Opts);
my $sth_move = $dbh->prepare('insert into moves values (?,?,?,?,?) on duplicate key update m_old_article = m_old_article');
my $sth_logging = $dbh->prepare('insert into logging values (?,?,?,?,?,?,?,?) on duplicate key update l_timestamp = l_timestamp ');


use POSIX 'strftime';
$global_timestamp = strftime("%Y%m%d%H%M%S", gmtime(time()));

my $c = 0;
my $d = 0;

open IN, "<", $ARGV[0];
print "$ARGV[0]: ";
select STDOUT; 
$| = 1;
while ( $line = <IN> ) { 
  $c++;
  if ( defined $seen{$line} ) { 
    $d++;
    next;
  }
  if ( 0 == $c % 1000) { print "."; }

  $seen{$line} = 1;
  chomp $line;

  $line =~ s/(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)/$1-$2-$3T$4:$5:$6Z/;

  @parts = split /\| /, $line;

  if ( $parts[2] eq 'renamed' ) { 

# 20080904000000| Mathematics| renamed| Vector (spatial)| B-Class
# | Top-Class| Vector (geometric)

    $sth_move->execute($parts[0], 0, $parts[3], 0, $parts[6]);   
    $sth_logging->execute($parts[1], 0, $parts[3], "moved", 
                          $global_timestamp, "", "", $parts[0]);

  } elsif ( $parts[2] eq 'added' ) { 

#2008-09-04T00:00:00Z| Mathematics| added| Separation axiom| B-Class| Mid-Class

    $sth_logging->execute($parts[1], 0, $parts[3], 
                          'quality', $global_timestamp,
                          $NotAClass, $parts[4], $parts[0]);

    $sth_logging->execute($parts[1], 0, $parts[3], 
                          'importance', $global_timestamp,
                           $NotAClass, $parts[5], $parts[0]);

  } elsif ( $parts[2] eq 'removed' ) { 

#2008-08-27T00:00:00Z| Mathematics| removed| Homotopy| B-Class| Top-Class

    $sth_logging->execute($parts[1], 0, $parts[3], 
                          'quality', $global_timestamp,
                          $parts[4], $NotAClass, $parts[0]);

    $sth_logging->execute($parts[1], 0, $parts[3], 
                          'importance', $global_timestamp,
                          $parts[5], $NotAClass, $parts[0]);

  } elsif ( $parts[2] eq 'reassessed' ) { 

#2008-08-21T00:00:00Z| Mathematics| reassessed| List of International 
# Mathematical Olympiads| Unassessed-Class| Mid-Class| FA-Class| Mid-Class
  
    if ( $parts[4] ne $parts[6] ) { 
      $sth_logging->execute($parts[1], 0, $parts[3], 
                            'quality', $global_timestamp,
                            $parts[4], $parts[6], $parts[0]);
    }

    if ( $parts[5] ne $parts[7] ) { 
      $sth_logging->execute($parts[1], 0, $parts[3], 
                          'importance', $global_timestamp,
                            $parts[5], $parts[7], $parts[0]);
    }

  } else { 
    die "Bad action: " . $parts[2] . "\n$line\n";
  }

}

$dbh->commit();

print "\tLines: $c / dups $d\n";

exit;


#  my $sth_insert_logging = $dbh->prepare_cached("INSERT INTO logging " 
# . "values (?,?,?,?,?,?,?,?)");


#  print "U: '$project' '$art' '$ns' '$table'\n";
#
#  $sth_insert_logging->execute($project, $ns, $art, $table, 
#                               $global_timestamp,
#                               $oldvalue, $value, $timestamp);





sub db_connect {
  my $opts = shift;

  die "No database given in database conf file\n"
    unless ( defined $opts->{'database'} );

  my $connect = "DBI:mysql"
           . ":database=" . $opts->{'database'};

  if ( defined $opts->{'host'} ) {
    $connect .= ":host="     . $opts->{'host'} ;
  }

  if ( defined $opts->{'credentials-readwrite'} ) {
    $opts->{'password'} = $opts->{'password'} || "";
    $opts->{'username'} = $opts->{'username'} || "";

    $connect .= ":mysql_read_default_file=" 
              . $opts->{'credentials-readwrite'};
  }

  my $db = DBI->connect($connect, 
                        $opts->{'username'}, 
                        $opts->{'password'},
                       {'RaiseError' => 1, 
                        'AutoCommit' => 0} )
     or die "Couldn't connect to database: " . DBI->errstr;
   
  return $db;
}

