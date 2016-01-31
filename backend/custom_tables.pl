use strict;

# custom_tables.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

########################################################################
# Table for the Ships project, only displays a few selected 
# quality assessment levels

sub custom_ships_table_1 {
  my $proj = 'Ships';
  my $title = 'WikiProject Ships articles by quality and importance';
  my $tdata = fetch_project_table_data($proj, undef, undef, $title);

  my $GoodClasses = { 'FA-Class' => 1,
                      'A-Class' => 1,
                      'GA-Class' => 1,
                      'B-Class' => 1,
                      'C-Class' => 1,
                      'Start-Class' => 1,
                      'Stub-Class' => 1,
                      'List-Class' => 1,
                      'Book-Class' => 1,
                      };

  my $data = $tdata->{'data'};
  my $key;
  foreach $key ( keys %$data ) { 
    if ( ! defined $GoodClasses->{$key} ) { 
      delete $data->{$key};
    }
  }

  my $format = \&format_cell_pqi;

  my $code = make_project_table_wikicode($tdata, $title, 
                              $format, 
                              { 'noassessed' => 'true'} );

  return $code;
}

########################################################################
# Table for the Essays project: hides the 'quality' row, because all
# their articles are NA quality

sub custom_essays_table_1 { 
  my $proj = 'Wikipedia_essays';
  my $title = 'Wikipedia essays by impact';
  my $tdata = fetch_project_table_data($proj, undef, undef, $title);

#XXX
#print Dumper($tdata);
#die;

  my $ratings = $tdata->{'data'}->{'NA-Class'};
  my $sort = $tdata->{'SortImp'};


  my $code = << "HERE";
{| class="ratingstable wikitable plainlinks"  style="text-align: right;"
|- 
! colspan="7" class="ratingstabletitle" | $title
|-
HERE

  my $imp;
  foreach $imp ( sort { $sort->{$b} <=> $sort->{$a} } keys %$ratings ) { 
    $code .= "! " . $tdata->{'ImportanceLabels'}->{$imp} . "\n";
  }

  $code .= "! | '''Total'''\n";
  $code .= "|-\n";

  my $total = 0;
  foreach $imp ( sort { $sort->{$b} <=> $sort->{$a} } keys %$ratings ) { 
    $code .= "|| " . format_cell_pqi($proj, 'NA-Class', 
                                     $imp, $ratings->{$imp} )
             . "\n";
    $total += $ratings->{$imp};
  }
  $code .= "|| " . format_cell_pqi($proj, undef, undef, $total) . "\n";
  $code .= "|}";

  return $code;

}

########################################################################
# Table for the US roads project, amalgamates data from the per-state
# projects and computes some statistics for each one. 

sub custom_roads_table_1 {

  #The following data is in the order that the table rows should appear
  my $RoadProjectData = [
    'IH' => 'Interstate Highway System',
    'USH' => 'U.S. Highway system',
    'Auto trail' => 'U.S. auto trail',
    'Alabama' => 'Alabama road transport',
    'Alaska' => 'Alaska road transport',
    'American Samoa' => 'American Samoa road transport',
    'Arizona' => 'Arizona road transport',
    'Arkansas' => 'Arkansas road transport',
    'California' => 'California road transport',
    'Colorado' => 'Colorado road transport',
    'Connecticut' => 'Connecticut road transport',
    'Delaware' => 'Delaware road transport',
    'D.C.' => 'District of Columbia road transport',
    'Florida'=> 'Florida road transport',
    'Georgia' => 'Georgia (U.S. state) road transport',
    'Guam' => 'Guam road transport',
    'Hawaii' => 'Hawaii road transport',
    'Idaho' => 'Idaho road transport',
    'Illinois' => 'Illinois road transport',
    'Indiana' => 'Indiana road transport',
    'Iowa' => 'Iowa road transport',
    'Kansas' => 'Kansas road transport',
    'Kentucky' => 'Kentucky road transport',
    'Louisiana' => 'Louisiana road transport',
    'Maine' => 'Maine road transport',
    'Maryland' => 'Maryland road transport',
    'Massachusetts' => 'Massachusetts road transport',
    'Michigan' => 'Michigan road transport',
    'Minnesota' => 'Minnesota road transport',
    'Mississippi' => 'Mississippi road transport',
    'Missouri' => 'Missouri road transport',
    'Montana' => 'Montana road transport',
    'Nebraska' => 'Nebraska road transport',
    'Nevada' => 'Nevada road transport',
    'New Hampshire' => 'New Hampshire road transport',
    'New Jersey' => 'New Jersey road transport',
    'New Mexico' => 'New Mexico road transport',
    'New York' => 'New York road transport',
    'North Carolina' => 'North Carolina road transport',
    'North Dakota' => 'North Dakota road transport',
    'Ohio' => 'Ohio road transport',
    'Oklahoma' => 'Oklahoma road transport',
    'Oregon' => 'Oregon road transport',
    'Pennsylvania' => 'Pennsylvania road transport',
    'Puerto Rico' => 'Puerto Rico road transport',
    'Rhode Island' => 'Rhode Island road transport',
    'South Carolina' => 'South Carolina road transport',
    'South Dakota' => 'South Dakota road transport',
    'Tennessee' => 'Tennessee road transport',
    'Texas' => 'Texas road transport',
    'U.S. Virgin Islands' => 'U.S. Virgin Islands road transport',
    'Utah' => 'Utah road transport',
    'Vermont' => 'Vermont road transport',
    'Virginia' => 'Virginia road transport',
    'Washington' => 'Washington road transport',
    'West Virginia' => 'West Virginia road transport',
    'Wisconsin' => 'Wisconsin road transport',
    'Wyoming' => 'Wyoming road transport',
    'USRD' => 'U.S. road transport'
  ];

  # List of projects that have a grey background for their table row
  my $RoadProjectsGrey = {
    'IH' => 1, 'USH' => 1, 'Auto trail' => 1, 
    'D.C.' => 1, 'Guam' => 1, 'Puerto Rico' => 1, 
    'U.S. Virgin Islands' => 1, 'USRD' => 1, 'American Samoa'=>1
  };
 

  # Parse data into more useful structures  
  my $i;
  my $RoadProjects = [];
  my $RoadProjectCats = {};
  for ( $i = 0; $i < scalar @$RoadProjectData; $i+= 2) { 
    push @$RoadProjects, $RoadProjectData->[$i];
    $RoadProjectCats->{$RoadProjectData->[$i]} 
                         = $RoadProjectData->[$i+1];
  }

  my $Classes = {
    'FA-Class'    => {'sort'=>1, 'weight'=>0, 'name'=>'FA'},
    'A-Class'     => {'sort'=>2, 'weight'=>1, 'name'=>'A'},
    'GA-Class'    => {'sort'=>3, 'weight'=>2, 'name'=>'GA'},
    'B-Class'     => {'sort'=>4, 'weight'=>3, 'name'=>'B'},
    'C-Class'     => {'sort'=>5, 'weight'=>4, 'name'=>'C'},
    'Start-Class' => {'sort'=>6, 'weight'=>5, 'name'=>'Start'},
    'Stub-Class'  => {'sort'=>7, 'weight'=>6, 'name'=>'Stub'},
  };

  my $dbh = database_handle();

  # This query is indexed and very fast, so I'm not bothering to 
  # to combine all the road projects into a single query
  my $sth = $dbh->prepare("select r_quality, count(r_article) as num 
                             from " . db_table_prefix() . "ratings 
                              where r_project  = ? 
                              and r_namespace = 0 
                              group by r_quality");

  my ( $proj, $cat, $data, $class, $weight, $omega, $total, $num);

  my $text = << "HERE";
{|class="wikitable sortable"
|-
!State
!{{FA-Class|category=Category:FA-Class U.S. road transport articles}}
!{{A-Class|category=Category:A-Class U.S. road transport articles}}
!{{GA-Class|category=Category:GA-Class U.S. road transport articles}}
!{{B-Class|category=Category:B-Class U.S. road transport articles}}
!{{C-Class|category=Category:C-Class U.S. road transport articles}}
!{{Start-Class|category=Category:Start-Class U.S. road transport articles}}
!{{Stub-Class|category=Category:Stub-Class U.S. road transport articles}}
!Total
!&#969;
!&#937;
HERE

  foreach $proj ( @$RoadProjects ) { 
    $omega = 0;
    $total = 0;  

    $text .= "|-\n";

    if ( defined $RoadProjectsGrey->{$proj} ) { 
      $text .= "!bgcolor=silver|";
    } else { 
      $text .= "!";
    }

    $text .= "[[Wikipedia:Version 1.0 Editorial Team/" 
                 . $RoadProjectCats->{$proj}
              . " articles by quality statistics|" . $proj . "]]\n";

    $cat = $RoadProjectCats->{$proj};
    $cat =~ s/ /_/g;


    $sth->execute($cat);
    $data = $sth->fetchall_hashref('r_quality');

    foreach $class ( sort { $Classes->{$a}->{'sort'} 
                            <=> $Classes->{$b}->{'sort'} } 
                     keys %$Classes ) { 
      $weight = $Classes->{$class}->{'weight'};
      if ( ! defined $data->{$class} ) { 
        $num = 0;
      } else { 
        $num = $data->{$class}->{'num'};
      }

      if ( defined $RoadProjectsGrey->{$proj} ) { 
        $text .= "|bgcolor=silver";
      }  
      $text .= "|$num\n";

      $total += $num;
      $omega += $num * $weight;
    }

    if ( defined $RoadProjectsGrey->{$proj} ) { 
      $text .= "|bgcolor=silver";
    }  
    $text .= "|$total\n";

    if ( defined $RoadProjectsGrey->{$proj} ) { 
      $text .= "|bgcolor=silver";
    }  
    $text .= "|$omega\n";

    if ( defined $RoadProjectsGrey->{$proj} ) { 
      $text .= "|bgcolor=silver";
    }  

    if ( $total > 0 ) { 
      $text .= "|" . (sprintf("%2.3f", $omega/ $total)) . "\n";
    } else { 
       $text .= "|&ndash;\n";   
    }

    $i++;
  }

  $text .= "|}";

  my $d = `/bin/date`;
  chomp $d;
  $text .= "<!-- $d --> ";


  return $text;
}

########################################################################
# Table for the Canada roads project, amalgamates data from the 
# subprojects and computes some statistics for each one. 

sub custom_canada_roads_table_1 {

  #The following data is in the order that the table rows should appear
  my $RoadProjectData = [
    'Alberta' => 'Alberta road transport',
    'British Columbia' => 'British Columbia road transport',
    'Manitoba' => 'Manitoba road transport',
    'New Brunswick' => 'New Brunswick road transport',
    'Newfoundland and Labrador' => 'Newfoundland and Labrador road transport',
    'Northwest Territories' => 'Northwest Territories road transport',
    'Nova Scotia' => 'Nova Scotia road transport',
    'Ontario' => 'Ontario road transport',
    'Nunavut' => 'Nunavut road transport',
    'Prince Edward Island' => 'Prince Edward Island road transport',
    'Quebec' => 'Quebec road transport',
    'Saskatchewan' => 'Saskatchewan road transport',
    'TCH' => 'Trans-Canada Highway',
    'Yukon' => 'Yukon road transport',
    'CRWP' => 'Canada road transport',
  ];

  # List of projects that have a grey background for their table row
  my $RoadProjectsGrey = {
    'Nunavut' => 1,
    'Northwest Territories' => 1,
    'Yukon' => 1,
  }; 

  # Parse data into more useful structures  
  my $i;
  my $RoadProjects = [];
  my $RoadProjectCats = {};
  for ( $i = 0; $i < scalar @$RoadProjectData; $i+= 2) { 
    push @$RoadProjects, $RoadProjectData->[$i];
    $RoadProjectCats->{$RoadProjectData->[$i]} 
                         = $RoadProjectData->[$i+1];
  }

  my $Classes = {
    'FA-Class'    => {'sort'=>1, 'weight'=>0, 'name'=>'FA'},
    'A-Class'     => {'sort'=>2, 'weight'=>1, 'name'=>'A'},
    'GA-Class'    => {'sort'=>3, 'weight'=>2, 'name'=>'GA'},
    'B-Class'     => {'sort'=>4, 'weight'=>3, 'name'=>'B'},
    'C-Class'     => {'sort'=>5, 'weight'=>4, 'name'=>'C'},
    'Start-Class' => {'sort'=>6, 'weight'=>5, 'name'=>'Start'},
    'Stub-Class'  => {'sort'=>7, 'weight'=>6, 'name'=>'Stub'},
  };

  my $dbh = database_handle();

  # This query is indexed and very fast, so I'm not bothering to 
  # to combine all the road projects into a single query
  my $sth = $dbh->prepare("select r_quality, count(r_article) as num 
                             from " . db_table_prefix() . "ratings 
                              where r_project  = ? 
                              and r_namespace = 0 
                              group by r_quality");

  my ( $proj, $cat, $data, $class, $weight, $omega, $total, $num);

  my $text = << "HERE";
{|class="wikitable sortable"
|-
!Province
!{{FA-Class|category=Category:FA-Class Canada road transport articles}}
!{{A-Class|category=Category:A-Class Canada road transport articles}}
!{{GA-Class|category=Category:GA-Class Canada road transport articles}}
!{{B-Class|category=Category:B-Class Canada road transport articles}}
!{{C-Class|category=Category:C-Class Canada road transport articles}}
!{{Start-Class|category=Category:Start-Class Canada road transport articles}}
!{{Stub-Class|category=Category:Stub-Class Canada road transport articles}}
!Total
!&#969;
!&#937;
HERE

  foreach $proj ( @$RoadProjects ) { 
    $omega = 0;
    $total = 0;

    $text .= "|-\n";

    if ( defined $RoadProjectsGrey->{$proj} ) { 
      $text .= "!bgcolor=silver|";
    } else { 
      $text .= "!";
    }

    $text .= "[[Wikipedia:Version 1.0 Editorial Team/" 
                 . $RoadProjectCats->{$proj}
              . " articles by quality statistics|" . $proj . "]]\n";

    $cat = $RoadProjectCats->{$proj};
    $cat =~ s/ /_/g;

    $sth->execute($cat);
    $data = $sth->fetchall_hashref('r_quality');

    foreach $class ( sort { $Classes->{$a}->{'sort'} 
                            <=> $Classes->{$b}->{'sort'} } 
                     keys %$Classes ) { 
      $weight = $Classes->{$class}->{'weight'};
      if ( ! defined $data->{$class} ) { 
        $num = 0;
      } else { 
        $num = $data->{$class}->{'num'};
      }

      if ( defined $RoadProjectsGrey->{$proj} ) { 
        $text .= "|bgcolor=silver";
      }  
      $text .= "|$num\n";

      $total += $num;
      $omega += $num * $weight;
    }

    if ( defined $RoadProjectsGrey->{$proj} ) { 
      $text .= "|bgcolor=silver";
    }  
    $text .= "|$total\n";


    if ( defined $RoadProjectsGrey->{$proj} ) { 
      $text .= "|bgcolor=silver";
    }  
    $text .= "|$omega\n";

    if ( defined $RoadProjectsGrey->{$proj} ) { 
      $text .= "|bgcolor=silver";
    }  

    if ( $total > 0 ) { 
      $text .= "|" . (sprintf("%2.3f", $omega/ $total)) . "\n";
    } else { 
       $text .= "|&ndash;\n";   
    }

    $i++;
  }

  $text .= "|}";

  my $d = `/bin/date`;
  chomp $d;
  $text .= "<!-- $d --> ";

  return $text;
}


########################################################################
# Tables for the Mathematics project, amalgamates data from various
# fields of mathematics and makes a large table from them all

sub math_fields_categories { 
  #The following data is in the order that the table rows should appear
  my $MathFields ={
    'Algebra' => 'Mathematics articles related to algebra',
    'Analysis' => 'Mathematics articles related to analysis',
    'Applied mathematics' => 'Mathematics articles related to applied mathematics',
    'Basics' => 'Mathematics articles related to basic mathematics',
    'Discrete mathematics' => 'Mathematics articles related to discrete mathematics',
    'Foundations, logic, and set theory' => 'Mathematics articles related to foundations, logic, and set theory',
    'Frequently viewed' => 'Frequently viewed mathematics articles',
    'General' => 'Mathematics articles related to general mathematics',
    'Geometry' => 'Mathematics articles related to geometry',
    'History' => 'Mathematics articles related to history',
    'Mathematical physics' => 'Mathematics articles related to mathematical physics',
    'Mathematicians' => 'Mathematics articles related to mathematicians',
    'Number theory' => 'Mathematics articles related to number theory',
    'Probability and statistics' => 'Mathematics articles related to probability and statistics',
    'Topology' => 'Mathematics articles related to topology',
#    'Theorems and conjectures' => '',
    'Vital articles' => 'Vital mathematics articles' };

  return $MathFields;
}


sub custom_mathematics_table_field_quality {
  
  my $MathFields = math_fields_categories();

  my $dbh = database_handle();

  my $Classes = {
    'FA-Class'    => {'sort'=>1, 'name'=>'FA'},
    'FL-Class'    => {'sort'=>2, 'name'=>'FL'},
    'A-Class'     => {'sort'=>3, 'name'=>'A'},
    'GA-Class'    => {'sort'=>4, 'name'=>'GA'},
    'B-Class'     => {'sort'=>5, 'name'=>'B'},
    'C-Class'     => {'sort'=>6, 'name'=>'C'},
    'Start-Class' => {'sort'=>7, 'name'=>'Start'},
    'Stub-Class'  => {'sort'=>8, 'name'=>'Stub'},
    'List-Class'  => {'sort'=>9, 'name'=>'List'},
  };

  my $sth = $dbh->prepare("
       select r_quality, count(r_article) as num 
         from " . db_table_prefix() . "ratings 
         join enwiki_p.page 
           on  page_title = r_article and page_namespace = 1
         join enwiki_p.categorylinks on cl_from = page_id
             where r_project  = 'Mathematics'
                and r_namespace = 0 
               and cl_to = ? 
         group by r_quality");


#  my $sth_theorems = $dbh->prepare("
#       select r_quality, count(r_article) as num
#         from ratings
#         join enwiki_p.page
#           on  cast(replace(page_title, '_', ' ') as char character set utf8)
#                   = r_article  and page_namespace = 0
#         join enwiki_p.categorylinks on cl_from = page_id
#             where r_project  = 'Mathematics'
#                and r_namespace = 0
#               and cl_to in ('Mathematical_theorems','Mathematical_conjectures')
#         group by r_quality");


  my ( $field, $cat, $data, $class, $total, $num, $text);

  my $lines = {};

  my $link = "http://toolserver.org/~enwp10/bin/list2.fcgi?run=yes" 
               . "&filterCategory=on&namespace=0" ;

  foreach $field ( sort {$a cmp $b} keys %$MathFields ) { 
    $total = 0;
    $text = "";

    $cat = $MathFields->{$field};
    $cat =~ s/ /_/g;

    $text .= "|-\n";
    $text .= "!";

    my $flink = $link . "&categoryt=" . uri_escape($cat) 
                . "&projecta=Mathematics";

    $text .= "[$flink $field]\n";


#    if ( $field eq 'Theorems and conjectures' ) { 
#      $sth_theorems->execute();
#      $data = $sth_theorems->fetchall_hashref('r_quality');
#    } else { 
      $sth->execute($cat);
      $data = $sth->fetchall_hashref('r_quality');
#    }

    foreach $class ( sort { $Classes->{$a}->{'sort'} 
                            <=> $Classes->{$b}->{'sort'} } 
                     keys %$Classes ) { 

      if ( ! defined $data->{$class} ) { 
        $num = 0;
      } else { 
        $num = $data->{$class}->{'num'};
      }

      $flink = $link . "&categoryt=" . uri_escape($cat) 
                 . "&projecta=Mathematics"
                 . "&quality=$class";

      $text .= "|[$flink $num]\n";

      $total += $num;
    }
   $text .= "|'''$total'''\n";
   $lines->{$field} = $text;
  }

  $text = << "HERE";
{|
|-
! Mathematics articles by field and quality
|-
|
{|class="wikitable sortable plainlinks" style="margin-top: 0em;"
|-
!Field
!{{FA-Class|category=Category:FA-Class mathematics articles}}
!{{FL-Class|category=Category:FL-Class mathematics articles}}
!{{A-Class|category=Category:A-Class mathematics articles}}
!{{GA-Class|category=Category:GA-Class mathematics articles}}
!{{B-Class|category=Category:B-Class mathematics articles}}
!{{C-Class|category=Category:C-Class mathematics articles}}
!{{Start-Class|category=Category:Start-Class mathematics articles}}
!{{Stub-Class|category=Category:Stub-Class mathematics articles}}
!{{List-Class|category=Category:Stub-Class mathematics articles}}
!'''Total'''
HERE

  foreach $_ ( sort {$a cmp $b} keys %$lines ) { 
    $text .= $lines->{$_};
  }

  $text .= "|}\n|}";

  return $text;
}



sub custom_mathematics_table_field_priority {
  
  my $MathFields = math_fields_categories();

  my $dbh = database_handle();

  my $Classes = {
    'Top-Class'    => {'sort'=>1, 'name'=>'Top'},
    'High-Class'    => {'sort'=>2, 'name'=>'High'},
    'Mid-Class'     => {'sort'=>3, 'name'=>'Mid'},
    'Low-Class'    => {'sort'=>4, 'name'=>'Low'},
  };

  my $sth = $dbh->prepare("
       select r_importance, count(r_article) as num 
         from " . db_table_prefix() . "ratings 
         join enwiki_p.page 
           on  page_title = r_article  and page_namespace = 1
         join enwiki_p.categorylinks on cl_from = page_id
             where r_project  = 'Mathematics'
                and r_namespace = 0 
               and cl_to = ? 
         group by r_importance");


  my ( $field, $cat, $data, $class, $total, $num, $text);

  my $lines = {};

  my $link = "http://toolserver.org/~enwp10/bin/list2.fcgi?run=yes" 
               . "&filterCategory=on&namespace=0" ;

  foreach $field ( sort {$a cmp $b} keys %$MathFields ) { 
    $total = 0;
    $text = "";

    $cat = $MathFields->{$field};
    $cat =~ s/ /_/g;

    $text .= "|-\n";
    $text .= "!";

    my $flink = $link . "&categoryt=" . uri_escape($cat) 
                . "&projecta=Mathematics";

    $text .= "[$flink $field]\n";

    print "Field: $field Cat: '$cat'\n";

      $sth->execute($cat);
      $data = $sth->fetchall_hashref('r_importance');

    foreach $class ( sort { $Classes->{$a}->{'sort'} 
                            <=> $Classes->{$b}->{'sort'} } 
                     keys %$Classes ) { 

      if ( ! defined $data->{$class} ) { 
        $num = 0;
      } else { 
        $num = $data->{$class}->{'num'};
      }

      $flink = $link . "&categoryt=" . uri_escape($cat) 
                 . "&projecta=Mathematics"
                 . "&importance=$class";

      $text .= "|[$flink $num]\n";

      $total += $num;
    }
   $text .= "|'''$total'''\n";
   $lines->{$field} = $text;
  }

  $text = << "HERE";
{|
|-
! Mathematics articles by field and priority
|-
|
{|class="wikitable sortable plainlinks" style="margin-top: 0em;"
|-
!Field
!{{Top-Class|category=Category:Top-Priority mathematics articles}}
!{{High-Class|category=Category:High-Priority mathematics articles}}
!{{Mid-Class|category=Category:Mid-Priority mathematics articles}}
!{{Low-Class|category=Category:Low-Priority mathematics articles}}
!'''Total'''
HERE

  foreach $_ ( sort {$a cmp $b} keys %$lines ) { 
    $text .= $lines->{$_};
  }

  $text .= "|}\n|}";

  return $text;
}



1;

