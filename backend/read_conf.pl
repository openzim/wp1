#!/usr/bin/perl

# read_conf.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

use strict;
use Data::Dumper;

my $Settings = read_conf();

sub read_conf { 
  my $filename;
  my $settings;
  my $homedir = (getpwuid($<))[7];
  
  if ( defined $ENV{'WP10_CREDENTIALS'} ) {
    $filename = $ENV{'WP10_CREDENTIALS'};
  } else { 
    $filename = $homedir . "/.wp10.conf";
  }

  die "Can't open configuration file '$filename'\n"
    unless -r $filename;

  if ( $ARGV[0] eq '--debug' ) { 
    print "Reading configuration file '$filename'\n";
  }

  open CONF, "<", $filename 
    or die "Can't open configuration file '$filename': $!\n";

  my $text = "";
  my $line;
  
  while ( $line = <CONF> ) {
    $text .= $line;
  }
  close CONF;

  $settings = eval '{ ' . $text . ' }';

  if ( $@ ) { 
    die "\nError parsing configuration file '$filename':\n  $@\n";
  }


  foreach $line ( @{$settings->{'lib'}} ) {
    push @INC, $line;
  }


  if ( $ARGV[0] eq '--debug' ) { 

    local $Data::Dumper::Terse = 1;
    local $Data::Dumper::Sortkeys = 1;
    print "Configuration settings: \n";
    print Dumper($settings);

    print "Include path (INC):\n\t";
    print (join "\n\t", @INC);
    print  "\n--\n";
  }

  return $settings;

}

sub get_conf { 
  my $var = shift;
  return $Settings->{$var};
}



# Load successfully
1;
