#!/usr/bin/perl

# init_cache.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

Routine to initialize a Cache::File object

=cut

require Cache::File;

our $Opts;

sub init_cache { 
  die "Cache directory must be specified as 'cachedir'\n"
    unless ( defined $Opts->{'cachedir'} );

  die "Cache location " . $Opts->{'cachedir'} . " isn't valid\n"
    unless ( -d $Opts->{'cachedir'} && -w $Opts->{'cachedir'} );

  my $cacheFile = Cache::File->new( cache_root => $Opts->{'cachedir'});

  return $cacheFile;
}

# Load successfully
1;

