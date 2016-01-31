#!/usr/bin/perl

# copy_tables.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

Copy assessment tables to the wiki

=cut

use utf8;
use encoding 'utf8';

binmode STDOUT, ":utf8";
select STDOUT;
$| = 1;

use strict;
use Encode;

#############################################################
# Define global variables and then load subroutines

require 'read_conf.pl';
our $Opts = read_conf(); # Also initializes library paths

require 'database_routines.pl';
require 'wp10_routines.pl';
require 'api_routines.pl';
require 'tables_lib.pl';
require 'custom_tables.pl';
require 'read_custom.pl';


############################################################

if ( $ARGV[0] =~ /^--project/ ) {  # accept --project and --projects
  $ARGV[1] =~ s/ /_/g;
  copy_project_tables($ARGV[1]);
} elsif ( $ARGV[0] eq '--global' ) { 
  copy_global_table();
} elsif ( $ARGV[0] eq '--custom' ) { 
  copy_custom_tables($ARGV[1]);
} else { 
  print << "HERE";
Usage:

* Copy project tables:

  $0 --project [PROJECT]

* Copy global table:

  $0 --global 

* Copy custom tables:

  $0 --custom [TABLE NAME]

HERE
}

exit;

############################################################

sub copy_project_tables { 
  my $filter = shift;

  my $project_details = db_get_project_details(); # BUG - this is calling the one from database_www - fix!
  my $project;

  my $count = scalar keys %$project_details;
  print "Count: $count\n";

  my $timestamp_u = strftime("%Y%m%d%H%M%S", gmtime(time()));

  my $i = 0;
  foreach $project ( sort {$project_details->{$a}->{'p_upload_timestamp'}
                           cmp $project_details->{$b}->{'p_upload_timestamp'} } keys %$project_details ) {
    if ( defined $filter ) { 
      next unless ( ($filter eq $project) 
                 || ($project =~ /^\Q$filter\E$/) );
    }

    $i++;
    print "\n$i / $count $project\n";

    print "Trying to reconnect\n";
    db_reconnect();  # This is a hack to work around the database server
                     # randomly killing queries from this script

    my $page = "User:WP 1.0 bot/Tables/Project/$project";
    my $summary = "Copying assessment table to wiki";
    my ( $html, $wiki, $timestamp, $acount) = cached_project_table($project);
    $wiki = munge($wiki, 'project');

    if ( $acount == 0 ) { 
       print "Count is zero, skipping\n";
       next;
    } else { 
       print "Count: $acount\n";
    }

#    $wiki .= "<noinclude>{{DEFAULTSORT|$project}}</noinclude>";

    if ( ! defined $ENV{'DRY_RUN'}) {
      api_edit( $page, $wiki, $summary);
      print "Timestamp: $timestamp_u\n";
      db_set_upload_timestamp($project, $timestamp_u);

    }
  }

  db_commit();

}


############################################################

sub copy_custom_tables { 

  my $filter = shift;
  print "Filtering custom tables with '$filter'\n";

  my $custom = read_custom();

  my $table;
  my $code;
  my $dest;
  my $summary;

  foreach $table ( keys %$custom ) { 
    if ( defined $filter ) { 
      next unless ( $table =~ /\Q$filter\E/);  
    }

    print "Creating custom table '$table'\n";

    if ( ! defined $custom->{$table}->{'dest'} ) { 
      die "No destination for table '$table'\n";
    } else { 
      $dest = $custom->{$table}->{'dest'};
    }

    if ( $custom->{$table}->{'type'} eq 'projectcategory' ) { 
      print "... projectcategory type\n";
      $code = project_category_table($custom->{$table});
    } elsif ( $custom->{$table}->{'type'} eq 'project' ) { 
      print "... project type\n";
      $code = project_custom_table($custom->{$table});
    } elsif ( $custom->{$table}->{'type'} eq 'customsub' ) { 
      print "... customsub type\n";
      $code = &{$custom->{$table}->{'customsub'}}();
    }  else { 
      die ("Bad table type for '$table'\n");
    }

    $code = munge($code, 'project');
    $summary = "Copying custom table '$table' to wiki\n";


    if ( ! defined $ENV{'DRY_RUN'}) {
      api_edit($dest, $code, $summary);
    } else { 
      print "DRY RUN - not editing wiki\n";
    }
  }
}

############################################################

sub project_category_table { 
  my $data = shift;

  my $project = $data->{'project'};
  my $cat = $data->{'cat'};
  my $catns = $data->{'catns'};
  my $title = $data->{'title'};
  my $dest = $data->{'dest'};
  my $config = $data->{'config'};

  my $summary = "Copying assessment table to wiki";

  my ($html, $wiki) = make_project_table($project, $cat, $catns, $title, $config);

  return $wiki;
}

############################################################

sub project_custom_table { 
  my $data = shift;

  my $project = $data->{'project'};
  my $cat = undef;
  my $catns = undef;
  my $title = $data->{'title'};
  my $dest = $data->{'dest'};
  my $config = $data->{'config'};

  my $summary = "Copying assessment table to wiki";

  my ($html, $wiki) = make_project_table($project, $cat, $catns, $title, $config);

  return $wiki;
}


############################################################

sub copy_global_table { 
  print "Copying global table\n";

  my $page = "User:WP 1.0 bot/Tables/OverallArticles";
  my $summary = "Copying assessment table to wiki";
  my ( $html, $wiki) = cached_global_ratings_table();
  $wiki = munge($wiki, 'global');

  api_edit($page, $wiki, $summary);
  exit;
}

############################################################
# In case we need to do some reformatting for the wiki

sub munge { 
  my $text = shift;
  my $mode = shift;

  if ( $mode eq 'project' ) { 
      # Don't center the tables so they can be trancluded more flexibly
    $text =~ s/margin-left: auto;//;
    $text =~ s/margin-right: auto;//;
  }

  return $text;
}

############################################################
