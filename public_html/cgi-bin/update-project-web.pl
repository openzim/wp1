#!/usr/bin/perl

use Encode;

$project = $ARGV[0];

# broken
$project = decode("utf8",decode("utf8", $project));

$lq = '&laquo;';
$rq = '&raquo;';
print "Project: $lq$project$rq\n";


open OUT, ">>", "/data/project/enwp10/Debug.txt";
print OUT "--\n";
print OUT `/bin/date`;
print OUT "Update '$project'\n";
close OUT;


$PDIR = "/data/project/enwp10";
chdir "$PDIR/backend";

system "./download.pl", $project;
print "\n";
print "--- Finished downloading assessment data, now uploading table to wiki\n";
system "./copy_tables.pl", "--project", $project;

system "./check_stats_page.pl", $project;
