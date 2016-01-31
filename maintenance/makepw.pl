#!/usr/bin/perl

use Digest::MD5;


my $user = $ARGV[0];
my $pass = $ARGV[1];

  my $md5sum = Digest::MD5->new();
  $md5sum->add($user);
  $md5sum->add($pass);
  
  my $d = $md5sum->hexdigest();


print "insert into passwd values ('$user', '$d');\n";
