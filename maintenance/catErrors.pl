#!/usr/bin/perl
use Encode;
use Data::Dumper;


use utf8;
use encoding 'utf8';

require 'read_conf.pl';
our $Opts = read_conf(); # Also initializes library paths

require 'database_routines.pl';
require 'wp10_routines.pl';
require 'api_routines.pl';

my $cats = pages_in_category('Wikipedia 1.0 assessments');

$pcount = 0;
$t = scalar @$cats;

open OUT, ">", "Errors";
select OUT;
 $| = 1;
select STDOUT;

foreach $c ( @$cats ) { 
  $c =~ s/_/ /g; 
  $pcount++;
#  print "\n#--- $pcount / $t : $c\n";

  next unless ($c =~ /^(.*) articles by quality/);

  $project = $1;

  print "P: '$project'\n";
  next unless ($project eq 'United States');

  $quality = {};
  $importance = {};
  $articles = {};

  $c =~ s/^Category://;
  $qualitycats =pages_in_category($c);

  foreach $qc ( @$qualitycats ) { 
    $qc =~ s/_/ /g;
    next unless ( $qc =~ /([^ ]*) /);
    $qual = $1;
    print "   $qual => $qc\n";
    if ( ($qual eq 'Unassessed' ) || ($qual =~ /-Class/) ) { 
      print "OK $qual $qc\n"; 
    } else { 
      print "BAD $qual $qc\n"; 
      next;
    }

    if ( $qual eq "Unassessed" ) { $qual = 'Unassessed-Class'; }
 
    if ( defined $quality->{$qual} ) { 
      print "ERROR (duplicate category): $project quality $qual\n";
      print "      " . $quality->{$qual} . "\n";
      print "      $qc\n";
      print OUT "CATDUP\t$project\tquality\t$qual";
      print OUT "\t" . $quality->{$qual} ;
      print OUT "\t$qc\n";
    } else { 
      $quality->{$qual} = $qc;
    }

    $qc =~ s/^Category://;
    $arts = pages_in_category($qc, 1);
    foreach $art (@$arts ) { 
      $art =~ s/_/ /g;
      if ( defined $articles->{$art} ) { 
        print "ERROR (duplicate rating): $project $art\n";
        print "      " . $articles->{$art} . "\n";
        print "      $qual\n";
        print OUT "* QUALDUP\t$project\t[[Talk:$art]]";
        print OUT "\t" . $articles->{$art} ;
        print OUT "\t$qual\n";
      } else {
        $articles->{$art} = $qual;
      }
    }
  }

  $articles = {};

  $i = $c;
  $i =~ s/quality$/importance/;
  $icats = pages_in_category($i);
  if ( 0 == scalar @$icats ) { 
    $i =~ s/importance$/priority/;
    $icats = pages_in_category($i);
  }

  print "\nIMP: $i " . (scalar @$icats) . "\n";

  foreach $ic ( @$icats ) { 
    $ic =~ s/_/ /g;
    next unless ( $ic =~ /([^ ]*)(?:-Class)? /);
    $imp = $1;
    print "   $imp => $ic\n";

    if ( defined $importance->{$imp} ) { 
      print "ERROR (duplicate category): $project importance $imp\n";
      print "      " . $importance->{$imp} . "\n";
      print "      $ic\n";
      print OUT "CATDUP\t$project\t$imp";
      print OUT "\t" . $importance->{$imp} . "\t";
      print OUT "\t$ic\n";
    } else { 
      $importance->{$imp} = $ic;
    }

    $ic =~ s/^Category://;
    $arts = pages_in_category($ic, 1);
    foreach $art (@$arts ) { 
      $art =~ s/_/ /g;
      if ( defined $articles->{$art} ) { 
        print "ERROR (duplicate rating): $project $art\n";
        print "      " . $articles->{$art} . "\n";
        print "      $imp\n";
        print OUT "* IMPDUP\t$project\t[[Talk:$art]]";
        print OUT "\t" . $articles->{$art} ;
        print OUT "\t$imp\n";
      } else {
        $articles->{$art} = $imp;
      }
    }



  } 

}

