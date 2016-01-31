#!/usr/bin/perl

# read_custom.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

use strict;
use Data::Dumper;

my $custom_die = 0;

sub read_custom { 
  my $verbose = shift || 0;

  my $homedir = (getpwuid($<))[7];  
  my $filename = 'Custom.tables.dat';

  die "Can't open file '$filename'\n"
    unless -r $filename;

  logmsg(1, $verbose, "-- Reading configuration file '$filename'\n");

  open CONF, "<", $filename 
    or die "Can't open configuration file '$filename': $!\n";

  my $text = "";
  my $line;
  
  while ( $line = <CONF> ) {
    $text .= $line;
  }
  close CONF;

  my $settings = eval '{ ' . $text . ' }';

  if ( $@ ) { 
    die "\nError parsing configuration file '$filename':\n  $@\n";
  }

  if ( $verbose > 1) { 

    local $Data::Dumper::Terse = 1;
    local $Data::Dumper::Sortkeys = 1;
    logmsg(2, $verbose, "Configuration settings: \n");
    logmsg(2, $verbose, Dumper($settings) );
    logmsg(2, $verbose, "\n");
  }

  check_custom($settings, $verbose);

  return $settings;
}

sub check_custom { 
  my $settings = shift;
  my $verbose = shift || 0;
  my $tablen;
  my $table;

  logmsg(1, $verbose, "-- Verifying custom table instructions \n");

  foreach $tablen ( keys %$settings ) { 
    logmsg(1, $verbose, "Table: $tablen\n");
    $table = $settings->{$tablen};

    if ( ! defined $table->{'type'} ) { 
      fatal($tablen, "no type specified");
    }

    logmsg(1, $verbose, "  type: " . ($table->{'type'}) . "\n");

    if ( 'projectcategory' eq $table->{'type'} ) { 
      my $param;
      foreach $param ( ('cat', 'catns', 'project', 'title', 'dest') ) { 
        if ( ! defined $table->{$param} ) { 
          fatal($tablen, "parameter '$param' not specified");
        } else { 
          logmsg(1, $verbose, "  $param: " . ($table->{$param}) . "\n");
        }
      } 
      
      if ( ! defined $table->{'config'} ) { 
        $table->{'config'} = {};
      } else { 
        logmsg(1, $verbose, "  configuration:\n");
        my $param;
        foreach $param ( sort {$a cmp $b} keys %{$table->{'config'}} ) { 
          logmsg(1, $verbose, "    $param: " . $table->{'config'}->{$param} . "\n");
        }   
      }

      logmsg(1, $verbose, "\n");
    } elsif ( 'project' eq $table->{'type'} ) { 
      my $param;
      foreach $param ( ('project', 'title', 'dest') ) { 
        if ( ! defined $table->{$param} ) { 
          fatal($tablen, "parameter '$param' not specified");
        } else { 
          logmsg(1, $verbose, "  $param: " . ($table->{$param}) . "\n");
        }
      } 
      
      if ( ! defined $table->{'config'} ) { 
        $table->{'config'} = {};
      } else { 
        logmsg(1, $verbose, "  configuration:\n");
        my $param;
        foreach $param ( sort {$a cmp $b} keys %{$table->{'config'}} ) { 
          logmsg(1, $verbose, "    $param: " . $table->{'config'}->{$param} . "\n");
        }   
      }

      logmsg(1, $verbose, "\n");

    } elsif ( $table->{'type'} eq 'customsub' ) { 
      if ( ! defined $table->{'customsub'} ) { 
        fatal($tablen, "custom subroutine not specified");
      } else {
        logmsg(1, $verbose, "  custom subroutine: specified\n");
      }

      if ( ! defined $table->{'dest'} ) { 
        fatal($tablen, "destination not specified");
      } else {
        logmsg(1, $verbose, "  dest: " . ($table->{'dest'}) . "\n");
      }     
    
    } else { 
      fatal($tablen, "unrecognized type: " . ($table->{'type'}) . "\n");
    }
  }

  if ( $custom_die > 0 ) { 
    die "Encountered $custom_die fatal errors, aborting\n";
  }

  logmsg(1, $verbose, "\n-- Finished verifying custom table instructions \n");
}


sub fatal { 
  my $table = shift;
  my $error = shift;
  print "Fatal error with configuration of '$table': $error\n";
  $custom_die++;
}

sub logmsg { 
  my $level = shift;
  my $threshold = shift;
  my $message = shift;
  if ( $threshold >= $level ) { 
    print $message;
  }
}

# Load successfully
1;
