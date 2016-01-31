#!/usr/bin/perl

# RatingsTable.pm
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

 This class is used to create a table of article rating data,
 to abstract the table generation code away from the main code

=over 

=item The data for the table goes in a 2D hash, indexed by symbolic 
tags.

=item  A subset of this data is output, based on parameters.

=item  The symbolic tags are not used for output; there are other 
parameter for how to format them.

=back

The generate procedure is to set the data using the B<data> method, 
set the columns and rows to be displayed via B<columns> and B<rows>,
set the titles via B<columntitles> and B<rowtitles>, and then 
generate the wikicode via B<wikicode>.

=head1 METHODS

All methods must be passed to a RatingsTable instance $table

=over 

=cut

package RatingsTable;
use strict;
use Carp;

use Data::Dumper;

#######################################

=item B<new>

Standard constructor

=cut

sub new {
  my $self = {};
  bless($self);

  $self->{'columns'} = [];
  $self->{'rows'} = [];
  $self->{'columnlabels'} = {};
  $self->{'rowlabels'} = {};
  $self->clear();  # initialize data hash
  return $self;
}

#######################################

=item B<title>([NEWTITLE])

Get/set overarching title

=cut

sub title {
  my $self = shift;
  my $newtitle = shift;
  if ( defined $newtitle) { 
    $self->{'title'} = $newtitle;
  }
 return $self->{'title'};
}

#######################################

=item B<proj>([NEWPROJECT])

Get/set overarching project name

=cut

sub proj {
  my $self = shift;
  my $proj = shift;
  $self->{'proj'} = $proj;
  return $self->{'proj'};
}


####################################

=item B<clear>

Clear the data. Does not clear column or row names or formats

=cut

sub clear {
  my $self = shift;
  $self->{'data'}= {};
}

####################################

=item B<data>(ROW, COL, [NEWVALUE])

Get/set data for a particular cell

=cut

sub data { 
  my $self = shift;
  my $row = shift;
  my $col = shift;
  my $newvalue = shift;  

  if ( ! defined $self->{'data'}->{$row} ) {
     $self->{'data'}->{$row} = {};
  }

  if ( defined $newvalue ) { 
    $self->{'data'}->{$row}->{$col} = $newvalue;
  }

  return  $self->{'data'}->{$row}->{$col};
}


#############################

=item B<incrdata>

Increment the number in a table cell

=cut

sub incrdata { 
  my $self = shift;
  my $row = shift;
  my $col = shift;

  if ( ! defined $self->{'data'}->{$row} ) {
     $self->{'data'}->{$row} = {};
  }

  if ( ! defined $self->{'data'}->{$row}->{$col} ) {
    $self->{'data'}->{$row}->{$col} = 1;
  } else { 
    $self->{'data'}->{$row}->{$col} =  $self->{'data'}->{$row}->{$col} + 1;
  }    

  return  $self->{'data'}->{$row}->{$col};
}

###############################################################

=item B<columnlabels>([$ColumnLabels])

Get/set labels for columns. $ColumnLabels is a reference
to a hash of name => label pairs.

=cut

sub columnlabels {
  my $self = shift;
  my $newlabels = shift;

  if ( defined $newlabels) { 
    $self->{'columnlabels'} = $newlabels;
  }

  return  $self->{'columnlabels'};
}

##################################

=item B<rowlabels>([$RowLabels])

Get/set labels for rows. $ColumnLabels is a reference
to a hash of name => label pairs.

=cut

sub rowlabels {
  my $self = shift;
  my $newlabels = shift;

  if ( defined $newlabels) { 
    $self->{'rowlabels'} = $newlabels;
  }

  return  $self->{'rowlabels'};
}

#######################################

=item B<columns>([$ColumnList])

Get/set list of column names to use. $ColumnList is an array reference.

=cut

sub columns {
  my $self = shift;
  my $newcolumns = shift;

  if ( defined $newcolumns) { 
    $self->{'columns'} = $newcolumns
  }

  return  $self->{'columns'};
}

############################################33

=item B<rows>([$Rows])

Get/set list of row names to use. $Rows is an array reference

=cut

sub rows {
  my $self = shift;
  my $newrows = shift;

  if ( defined $newrows) { 
    $self->{'rows'} = $newrows;
  }

  return  $self->{'rows'};
}
 
######################################################

=item B<columntitle>([$title])

Get/set the title over all the rating columns. 

=cut

sub columntitle {
  my $self = shift;
  my $newtitle = shift;
  if ( defined $newtitle) { 
    $self->{'columntitle'} = $newtitle;
  }
 return $self->{'columntitle'};
}

=item B<unset_columntitle>() 

Remove the title over the rating columns

=cut

sub unset_columntitle { 
  my $self = shift;
  delete $self->{'columntitle'};
}


###########################################################
=item B<rowtitle>([$title])

Get/set the single title over all the rows

=cut

sub rowtitle {
  my $self = shift;
  my $newtitle = shift;
  if ( defined $newtitle) { 
    $self->{'rowtitle'} = $newtitle;
  }
 return $self->{'rowtitle'};
}

########################################################3

=item B<wikicode>()

 Generate wiki code from current data 

=cut

sub wikicode {

  my $self = shift;
  my $text;

  my $totalCols  = 0;
  my $row;
  my $col; 

  $totalCols = scalar @{$self->{'columns'}} + 1;

  $text .= << "HERE";
{| class="ratingstable wikitable plainlinks"  style="text-align: right; margin-left: auto; margin-right: auto;"
HERE

  if ( defined $self->{'title'} ) { 
    $text .= << "HERE";
|- 
! colspan="$totalCols" class="ratingstabletitle" | $self->{'title'}
HERE
  }

  my $classCols = $totalCols - 1;   
    # Number of columns covered by column title

  if ( defined $self->{'rowtitle'}) {
    if ( defined $self->{'columntitle'} ) {
       #Row and column titles

      $text .= << "HERE";
|-
! rowspan="2" style="vertical-align: bottom" | $self->{'rowtitle'}
! colspan="$classCols" | $self->{'columntitle'}
|-
HERE
    } else {
       #Row title but no column titles

      $text .= << "HERE";
|-
! style="vertical-align: bottom" | $self->{'rowtitle'}
HERE
    }
    foreach $col (@{$self->{'columns'}}) { 
if ( ! defined $self->{'columnlabels'}->{$col} ) { 
  carp("No label for column $col\n");
}
      $text .= << "HERE";
! $self->{'columnlabels'}->{$col}
HERE
    }
  } else {   # no row title 
    if (defined $self->{'columntitle'} ) {
        
      $text .= << "HERE";
|-
| &nbsp;
| colspan="$classCols" | $self->{'columntitle'}
|-
| &nbsp;
HERE
    } else {
      # no row title, no column title
      # Nothing to do in this case
    }
  }

   # output actual table data

  foreach $row ( @{$self->{'rows'}}) { 
if ( ! defined $self->{'rowlabels'}->{$row} ) { 
  carp("No label for row $row\n");
}
    $text .= << "HERE";
|-
| $self->{'rowlabels'}->{$row}
HERE

    foreach $col (@{$self->{'columns'}}) { 
#   print STDERR "Col $col Row $row\n";
      $text .= << "HERE";
|| $self->{'data'}->{$row}->{$col}
HERE
    }
  }

  my $proj = $self->{'proj'};

  $text .= "|-\n{{User:WP 1.0 bot/WikiWork|project=" . $proj . "|export=table}}\n|-";
  
  $text .= "\n|}\n";

  return $text;
}

###############################

sub transpose { 
  my $self = shift;

  my $tmp = $self->{'columns'};
  $self->{'columns'} = $self->{'rows'};
  $self->{'rows'} = $tmp;

  $tmp = $self->{'columntitle'};
  $self->{'columntitle'} = $self->{'rowtitle'};
  $self->{'rowtitle'} = $tmp;

  $tmp =  $self->{'columnlabels'};
  $self->{'columnlabels'} = $self->{'rowlabels'};
  $self->{'rowlabels'} = $tmp;


  my $olddata = $self->{'data'};
  $self->{'data'} = {};

  $self->{'clear'};
  my ($r, $c);
  foreach $r ( keys %$olddata ) { 
    foreach $c ( keys %{$olddata->{$r}} ) { 
      if ( ! exists $self->{'data'}->{$c} ) { 
        $self->{'data'}->{$c} = {};
      }
      $self->{'data'}->{$c}->{$r} = $olddata->{$r}->{$c};
    }
  }

}



###############################
## debugging

sub dump {
  my $self = shift;
  
  print "columns: " . Dumper($self->{'columns'}) . "\n\n";
  print "rows: " . Dumper($self->{'rows'}) . "\n\n";
  print "data: " . Dumper($self->{'data'}) . "\n\n";
}

############################## End

=pod 

=back

=cut

1; # return true on successful loading of the module

__END__
