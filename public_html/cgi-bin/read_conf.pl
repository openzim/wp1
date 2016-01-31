#!/usr/bin/perl

# read_conf.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

Routines to parse configuration variables from a settings file

=cut

use strict;
use Data::Dumper;

$ENV{'SERVER_ADMIN'} = 'theopolismewiki@gmail.com';

my $Settings = read_conf();

#####################################################################

=item B<read_conf>()

Read the configuration file from F<~/.wp10.conf>.
Return a hash references with all the settings.
Set up the include path from the I<lib> setting. 

=cut

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

  local $Data::Dumper::Terse = 1;
  local $Data::Dumper::Sortkeys = 1;
  #print "Configuration settings: \n";
  #print Dumper($settings);
  
  #print "Include path (\@INC):\n\t";
  #print (join "\n\t", @INC) . "\n";

  return $settings;  
}

###########################################################################

=item B<get_conf>(KEY)

Return the configuration value with key I<key>.

=cut

sub get_conf { 
  my $var = shift;
  return $Settings->{$var};
}

#####################################################################

# Load successfully
1;
