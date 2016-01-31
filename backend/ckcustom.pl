#!/usr/bin/perl

# ckcustom.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

Maintenance script to check the syntax of the custom table file

=cut

require 'custom_tables.pl';
require 'read_custom.pl';

my $custom = read_custom(1);

