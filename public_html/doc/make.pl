#!/usr/bin/perl

use Pod::Simple::HTMLBatch;
my $batchconv = Pod::Simple::HTMLBatch->new;
#  $batchconv->some_option( some_value );
#  $batchconv->some_other_option( some_other_value );

@dirs = ("/home/project/e/n/w/enwp10/subversion-new/p_enwp10/wp10.2g/");
$output_dir = "/home/project/e/n/w/enwp10/public_html/doc/";

$batchconv->batch_convert( \@dirs, $output_dir );

