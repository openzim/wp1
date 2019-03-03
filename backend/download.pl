#!/usr/bin/perl

# download.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

use strict;
use Data::Dumper;
use POSIX;
use Getopt::Long;

select STDOUT;
$| = 1;


#############################################################
# Define global variables and then load subroutines

require 'read_conf.pl';
our $Opts = read_conf(); # Also initializes library paths

require 'database_routines.pl';
require 'wp10_routines.pl';
require 'api_routines.pl';

my $start_time = time();

#############################################################

my ($mode, $projects) = parse_argv();

if ( $mode eq 'none') { usage(); exit; }

my $count = scalar @$projects;
print "Will update $count projects \n";

my $i = 0;
my $project;

foreach $project ( @$projects ) {
  $i++;
  if ( $count > 1) { 
    printf "\n%%-- %4d / %d : %s\n", $i, $count, $project;
  }
  update_status($project, $mode, $i, $count);
  download_project($project);
#  print "Sleeping...\n";
#  sleep 600;
}

print "Done.\n";

exit;

#####################################################################

sub update_status {
  return;
# XXX broken, disabled
# This was supposed to be used to let a web tool track the 
# status of the download process, but tht system never
# worked correctly

  my $project = shift;
  my $mode = shift;
  my $i = shift;
  my $count = shift;
  open OUT, ">", "/home/cbm/wp10downloads/dl.$$";
  print OUT "$mode\n";
  print OUT "$i\n";
  print OUT "$count\n";
  print OUT $start_time . "\n";
  print OUT time() . "\n";
  print OUT $project . "\n";
  close OUT;
}

#####################################################################

sub parse_argv { 
  my $opts = {};

  if ( ! GetOptions($opts, 'all', 'existing', 'new', 'under=i', 
                    'over=i','all','releases','reviews',
                    'excludefile=s', 'exclude=s@' )) {
    usage();
    exit;
  }

  my $project;

  my $includes = {};
  while ( $project = shift @ARGV ) {
    $project =~ s/ /_/g;
    $includes->{$project} = 1;
    $opts->{'includes'} = 1;
  }

  my $excludes = {};
  while ( $project = shift @{$opts->{'exclude'}} ) {
    $excludes->{$project} = 1;
  }

  my $filename = $opts->{'excludefile'};
  if(open(my $fh, '<:encoding(UTF-8)', $filename)){
    while (my $exproj = <$fh>) {
      chomp $exproj;
      $excludes->{$exproj} = 1;
    }
    close($fh);
  } elsif ( exists $opts->{'excludefile'} ) {
    die "Could not open --excludefile: '$filename'\n";
  }

  my $mode = "none";

  if ( exists $opts->{'existing'} ) {
    if ( exists $opts->{'new'} || exists $opts->{'all'} ) {
      usage();
    }
    $mode = 'existing';
  } elsif ( exists $opts->{'all'} ) {
    if ( exists $opts->{'new'} || exists $opts->{'existing'}) {
      usage();
    }
    $mode = 'all';
  } elsif ( exists $opts->{'new'} ) {
    if ( exists $opts->{'existing'} || exists $opts->{'all'}) {
      usage();
    }
    $mode = 'new';
  }

  if ( $mode eq 'none' && exists $opts->{'includes'} ) {
    $mode = 'all';
  }

  if ( exists $opts->{'releases'} ) {
    print "Download release data\n";
    download_release_data();  
    exit;
  }

  if ( exists $opts->{'reviews'} ) {
    print "Download review data\n";
    download_review_data();    
    exit;
  }

  if ( ! ( $mode eq 'new' || $mode eq 'all' || $mode eq 'existing') ) { 
    return ("none", []);
  }    

  my $project_details = db_get_project_details();
  
  my $project_list = download_project_list();

  my $projects = {};

  my $ts;

print "Mode: '$mode'\n";
  if ( $mode eq 'all' ) {
    foreach $project ( @$project_list ) {

#print "P: '$project'\n";

      if ( exists $opts->{'includes'} ) {
        next unless ( exists $includes->{$project} );
      }
      next if ( exists $excludes->{$project});
      $ts = $project_details->{$project}->{'timestamp'} || 0;
      $projects->{$project} = $ts;
    }
  } elsif ( $mode eq 'existing') {
    foreach $project ( keys %$project_details ) {
      if ( exists $opts->{'includes'} ) {
        next unless ( exists $includes->{$project} );
      }
      next if ( exists $excludes->{$project});
      if ( exists $opts->{'over'} ) {
        next if ($project_details->{$project}->{'count'} < $opts->{'over'});
      }
      if ( exists $opts->{'under'} ) {
        next if ($project_details->{$project}->{'count'} > $opts->{'under'} );
      }

      $ts = $project_details->{$project}->{'timestamp'} || 0;
      $projects->{$project} = $ts;
    }
  } elsif ( $mode eq 'new') {
    foreach $project ( @$project_list ) {
      if ( exists $opts->{'includes'} ) {
        next unless ( exists $includes->{$project} );
      }

      next if ( exists $excludes->{$project});
      next if ( exists $project_details->{$project});

      $ts = $project_details->{$project}->{'timestamp'} || 0;
      $projects->{$project} = $ts;
    }
  } else {
    return ("none", []);
  }

  my @list =  sort { ($projects->{$a} <=> $projects->{$b}) || $a cmp $b }
              keys %$projects;

  if ( $mode eq 'existing' ) { 
    if ( exists $opts->{'over'} ) { 
      $mode .= ' over ' . $opts->{'over'};
    }
    if ( exists $opts->{'under'} ) { 
      $mode .= ' under ' . $opts->{'under'};
    }
  }

  if ( $opts->{'includes'} ) { 
    $mode .= " from ";
    $mode .= join " ",  keys %$includes;
  }

  if ( scalar keys %$excludes ) { 
    $mode .= " excluding ";
    $mode .= join " ",  keys %$excludes;

  }

  return ($mode, \@list);
}

#####################################################################

sub usage { 
print << "HERE";
Usage:  
$0 [--releases] [--review] [--all | --new | --existing] \
   [--over N] [--under N] [--exclude PROJECT] PROJECT 

  --releases         : Update data on release versions
  --reviews          : Update data on article review (e.g. FA)

  --all              : Update ratings data for all projects
  --existing         : Update data only for projects already in local database
  --new              : Update data only for projects not in local database

  --excludefile FILE : Don't update projects listed one per line in FILE
  --exclude PROJ     : Don't update PROJ. Option can be repeated 

The following two options only work with --existing
 --under N       : Only update projects with <= N articles
 --over N        : Only update projects with >= N articles
HERE
}

__END__
