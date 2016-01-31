#!/usr/bin/perl

# api_routines.pl
# Part of WP 1.0 bot
# See the files README, LICENSE, and AUTHORS for additional information

=head1 SYNOPSIS

Routines for fetching content from the wiki. This library
is a wrapper that abstracts Mediawiki::API and toolserver_api.pl
into a common interface and output format. 

=over

=cut

use strict;
use Encode;

use Data::Dumper;

require Mediawiki::API;
require "toolserver_api.pl";

require 'read_conf.pl';


my $api;
my $namespaces;

my $use_toolserver = get_conf('use_toolserver');

if ( ! $use_toolserver ) { 
  die "I don't like it\n";
  # I don't know whether the non-toolserver code (i.e. the API-only code)
  # will work at all. I am intentionally disabling it. If you want to try
  # to use it, expect to do some debugging. 
  # CBM 2011-4-4
}


#####################################################################

=item B<init_api>()

Initialize an internal Mediawiki::API object.

=cut

sub init_api() { 
  return if ( defined $api );

  $api = new Mediawiki::API;  # global object 
  $api->maxlag(-1);
  $api->max_retries(20);

  $api->base_url(get_conf('api-url'));
  $api->debug_level(3);

  my $cred = get_conf('api-credentials');

  if ( $cred ) { 
    $api->login_from_file($cred);
  }
  $api->{'decodeprint'} = 0;

  if ( defined $ENV{'API_DEBUG'} ) { 
    $api->debug_level($ENV{'API_DEBUG'});
  }

  # Initialize hash of namespace prefixes
  my $r = $api->site_info();
  $r = $r->{'namespaces'}->{'ns'};

  $namespaces ={};
  my $n;
  foreach $n ( keys %$r ) { 
    if ( $r->{$n}->{'content'} ne "" ) { 
      $namespaces->{$n}= $r->{$n}->{'content'} . ":";
    } else { 
      $namespaces->{$n}= $r->{$n}->{'content'} . "";
    }
  }
}

#####################################################################

=item B<pages_in_category>(CATEGORY, [NS])

Returns an array reference listing pages in CATEGORY

CATEGORY _must_ be UTF-8 encoded

The NS parmater, optional, is a numeric namespace for 
filtering the results.

The pages in the rsulting array _do_ have the namespace
prefix attached (for example C<Talk:Foo> and C<Wikipedia:Bar>)

The titles returned are UTF-8 encoded

=cut

sub pages_in_category {
  my $cat = shift;
  my $ns = shift;

  print "Get: $cat\n";

  if ( ( ! defined $ENV{'NO_TOOLSERVER_CATS'}) && $use_toolserver ) { 
#    print "\tusing toolserver\n";
    $cat =~ s/^Category://;
    $cat =~ s/ /_/g;
    my $r =  toolserver_pages_in_category($cat, $ns);
    return $r;
  }

    $cat =~ s/^Category://;

  print "Bypassing toolserver, getting category list from API\n";
  init_api();

  my $t = time();
  my $r = $api->pages_in_category($cat, $ns);  
  my @encoded;
  foreach $_ ( @$r ) { 
    $_ = encode("utf8", $_);
    $_ =~ s/^Category://;
    $_ =~ s/ /_/g;
    push @encoded, $_;
  }
  my $count = scalar @encoded;

  print "\tListed $count pages in " . (time() - $t) . " seconds\n";

  return \@encoded;
}

#####################################################################

=item B<pages_in_category_detailed>(CATEGORY, [NS], [LARGE])

Returns a reference to an array of hashes, 
one for each page in CATEGORY.

The output format is

  {  'ns'        => NAMESPACE, 
     'title'     => TITLE,
     'pageid'    => PAGEID,
     'sortkey'   => SORTKEY,
     'timestamp' => TIMESTAMP }

CATEGORY _must_ be UTF-8 encoded. 

The NS parameter, optional, is a numeric namespace for 
filtering the results. If NS is set to '*' or omitted then
all namespaces are searched. 

The LARGE parameter, optional, is a flag (0 or 1) that gives
a prediction about whether the category may be "large", that is,
may contain many articles.  The toolserver query killer tends
to kill the category listing query for large categories. Setting
the LARGE flag to 1 causes the system to always use the API instead of
the toolserver to list the category contents. This is much slower but is
not subject to the query killer.  Setting the parameter to 0 
(which is the default) causes the system to use either the toolserver 
or the API at its choice depending on configuration parameters. 

The page titles in the resulting array _do_not_ have the namespace
prefix attached (for example, the page C<Talk:Foo> will show

  { 'ns' => '1',
    'title' => 'Foo',
     ...  }

The data returned is all UTF-8 encoded.

=cut

sub pages_in_category_detailed {
  my $cat = shift;
  my $ns = shift;
  my $large = shift || 0;

  if ( $ns eq '*') { $ns = undef; }

  print "Get: $cat $ns (large: $large)\n";

  if ( (! defined $ENV{'NO_TOOLSERVER_CATS'}) 
       && ( ! $large ) && $use_toolserver ) { 
#    print "\tusing toolserver\n";
    $cat =~ s/^Category://;
    $cat =~ s/ /_/g;
    my $r = toolserver_pages_in_category_detailed($cat, $ns);
    return $r;
  }

  print "Bypassing toolserver, getting category list from API\n";

  init_api();

  my $t  = time();
  my $results = $api->pages_in_category_detailed($cat, $ns);

  my $r;

  foreach $r ( @$results ) { 
    $r->{'title'} =~ s/^\Q$namespaces->{$r->{'ns'}}\E//;
    $r->{'title'} = encode("utf8", $r->{'title'});
    $r->{'sortkey'} = encode("utf8", $r->{'sortkey'});
    $r->{'title'} =~ s/ /_/g;
  }

  my $count = scalar @$results;
  print "\tListed $count pages in " . (time() - $t) . " seconds\n";

  return $results;
}

#####################################################################

=item B<content>(PAGE) 

Fetch the source code of PAGE. The returned text is UTF-8 encoded.

=cut

sub api_content {
  my $art = shift;

  init_api();

  my $t = $api->content($art);

  if ( $t eq "") { return ""; }

  return encode("utf8", $t);

}

#####################################################################

=item B<content_section>(PAGE, SECTION) 

Fetch the source code of section number SECTION in PAGE. The lede is
section 0.

The returned text is UTF-8 encoded.

=cut

sub content_section {
  my $art = shift;
  my $sect = shift;

  init_api();

  my $t = $api->content_section($art, $sect);

  if ( $t eq "") { return ""; }

  return encode("utf8", $t->{'content'});

}


#####################################################################

=item B<api_namespaces>() 

Fetch a hash reference mapping namespace number to namespace prefix.

=cut

sub api_namespaces {
    init_api(); 
 
    return $namespaces;
}

#####################################################################
=item B<api_resolve_redirect>(NS, TITLE) 

Find the redirect target for NS:TITLE.

Return undef if NS:TITLE is not a redirect, otherwise return
(DEST_NS, DEST_TITLE, REV_TIMESTAMP)

=cut

sub api_resolve_redirect {
  my $ns = shift;
  my $title = shift;

  if ($use_toolserver == 1) { 
#    print "\tusing toolserver\n";
    return toolserver_resolve_redirect($ns, $title);
  }

  init_api();

  $title = $namespaces->{$ns} . $title;  

  print "T '$title'\n";

  my $data = $api->makeXMLrequest(['action'=>'query',
                                    'titles'=>$title,
                                    'redirects'=>'1',
                                    'prop'=>'revisions',
                                    'rvlimit' =>'1',
                                    'format'=>'xml']);

  print Dumper($data);

  my $c = $data->{'query'}->{'redirects'}->{'r'}->{'to'};

  if ( defined $c) { 
    my $ns = $data->{'query'}->{'pages'}->{'page'}->{'ns'};
    my $title = $data->{'query'}->{'pages'}->{'page'}->{'title'};
    my $timestamp = $data->{'query'}->{'pages'}->{'page'}->{'revisions'}->{'rev'}->{'timestamp'};
    $title =~ s/^\Q$namespaces->{$ns}\E//;
    return $ns, $title, $timestamp;
  } else { 
    return undef;
  }        
}

#####################################################################
=item B<api_get_move_log>(NS, TITLE) 

Download a list of move log entries for NS:TITLE

Returns a reference to an array of hashes

=cut

sub api_get_move_log {
  my $ns = shift;
  my $title = shift;

# Disabled
  if (0 && ($use_toolserver == 1)) { 
    print "\tusing toolserver\n";
    return toolserver_get_move_log($ns, $title);
  }

  init_api();

  $title = $namespaces->{$ns} . $title;  

  my $data = $api->log_events($title, ['letype'=>'move']);

  my $output = [];
  my ($d, $prefix);

  foreach $d ( @$data ) { 
    $d->{'user'} = encode('utf8', $d->{'user'});
    $d->{'title'} = encode('utf8', $d->{'title'});
    $d->{'comment'} = encode('utf8', $d->{'comment'});
    $d->{'dest-ns'} =$d->{'move'}->{'new_ns'};
    $d->{'dest-title'} = encode('utf8',$d->{'move'}->{'new_title'});

    # The following is to resolve ENWPONE-14
    $prefix = $namespaces->{$d->{'dest-ns'}};
    $d->{'dest-title'} =~ s/^\Q$prefix//;

    push @$output, $d;
  }

  return $output;
}

#####################################################################
=item B<api_edit>(WIKIPAGE, CONTENT, SUMMARY)

Edit WIKIPAGE with given content and edit summary

=cut

sub api_edit { 
  my $page = shift;
  my $content = shift;
  my $summary = shift;

  init_api();

  $api->edit_page($page, $content, $summary, ['bot' => 1]);
}
#####################################################################


sub get_api_object { 
  init_api();
  return $api;
}


#####################################################################

#Load successfuly
1;
