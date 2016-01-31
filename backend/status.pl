#!/usr/bin/perl

# status.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

use POSIX 'strftime';

open IN, "find /home/cbm/wp10downloads -name 'dl.*'|";

$procs = 0;
while ( $f = <IN> ) { 
  chomp $f;
  $f =~ /dl.(\d+)$/;
  $p = $1;

  if ( -e "/proc/$p" && -o "/proc/$p") { 
    print_line($f, $p);
    $procs++;
  } else { 
    unlink $f;
  }
}

print "\n$procs active processes\n";

exit;

sub print_line { 
  my $f = shift;
  my $p = shift;
  open FILE, "<", $f;
  binmode FILE, ":utf8";

  $mode = <FILE>;
  chomp($mode);

  $i = <FILE>;
  chomp $i;

  $count = <FILE>;
  chomp $count;
  
  $start_time = <FILE>;
  chomp($start_time);

  $last_time = <FILE>;
  chomp($last_time);

  $project = <FILE>;
  chomp($project);

  close FILE;

  $start_timestamp = strftime("%Y-%m-%d %H:%M", gmtime($start_time));
  $elapsed = time() - $start_time;

  $seconds = $elapsed % 60;
  $minutes = int($elapsed / 60) % 60;
  $hours = int($elapsed / 3600);

  print "Thread $p\n";
  print "  Started $start_timestamp\n";
  print "  Running " .$hours . "h " . $minutes ."m " . $seconds . "s\n";
  print "  Updating $i of $count\n";
  print "  Mode: $mode\n";

  $elapsed = time() - $last_time;
  print "  Working on $project for " . $elapsed . "s\n";
}
