#!/usr/bin/perl

# cache.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

Routines for using a databse table as an HTML cache

=cut

use Data::Dumper;
use Encode;
use strict;

our $dbh;

#####################################################################

=item B<cache_set>(KEY, CONTENT, $EXPIRY)

Add CONTENT to cache with key KEY, expiring in EXPIRY seconds

=cut

sub cache_set {
  my $key = shift;
  my $content = shift;
  my $expiry = shift;

  cache_purge();

  my $timestamp += time() + $expiry;

  my $sth = $dbh->prepare("UPDATE cache 
                        SET c_expiry = ?, c_content = ? 
                        WHERE c_key = ?");

  print "<!-- Update cache -->\n";
  print "<!-- KEY: '$key' -->\n";
  print "<!-- EXPIRY: '$expiry' -->\n";

  my $r = $sth->execute($timestamp, $content, $key);

  print "<!-- Cache update. Result: '$r' -->\n";

  if ( $r eq '' || $r eq '0E0') { 
    print "<!-- Cache insert -->";
    print "<!-- KEY: '$key' -->\n";
    print "<!-- EXPIRY: '$expiry' -->\n";

    $sth = $dbh->prepare("INSERT INTO cache VALUES (?,?,?)");
    $r = $sth->execute($key, $timestamp, $content);

    print "<!-- Cache insert. Result: '$r' -->\n";
  }
  print "<!-- Cache done -->\n";
}


###########################################################

=item B<cache_purge>()

Purge outdated entries from cache.

=cut

sub cache_purge { 

# Temporary hack because tables seem to get locked
# CBM - 2011-5-15 
# Reinstated, 2011-9-6
return;

  my $timestamp = time();

  my $sth = $dbh->prepare("DELETE FROM cache WHERE c_expiry < ?");
  my $r = $sth->execute($timestamp);

#  print "<!-- PURGE CACHE. Clear $r entries older than $timestamp -->\n";
}

############################################################

=item B<cache_exists>(KEY)

Tells whether a cache entry for KEY exists. 
Returns the exipiry if it does; returns undef if it doesn't.

=cut

sub cache_exists  { 
  my $key = shift;

  cache_purge();

#  print "<!-- CACHE EXISTS: key:'$key' -->\n";

  my $sth = $dbh->prepare("SELECT c_expiry FROM cache WHERE c_key = ?");
  my $r = $sth->execute($key);

  if ( $r = 0 ) { return undef; } 

  my @row = $sth->fetchrow_array();
  return $row[0];
}

###########################################################

=item B<cache_get>(KEY)

Get cache entry for KEY. Returns undef if there is no entry

=cut

sub cache_get  { 
  my $key = shift;

  cache_purge();

  my $sth = $dbh->prepare("SELECT c_content FROM cache WHERE c_key = ?");
  my $r = $sth->execute($key);

#  print "<!-- CACHE GET: key:'$key' -->\n";

  if ( $r = 0 ) { return undef; } 

  my @row = $sth->fetchrow_array();
  return $row[0];
}

###########################################################

# Load successfully
1;
