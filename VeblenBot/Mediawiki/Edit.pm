package Mediawiki::Edit;
# $Revision: 1.1 $
# Carl Beckhorn, 2008
# Copyright: GPL 2.0

my $deprecated_err = << "HERE";
The Mediawiki::Edit library is obsolete and deprecated. 
It is no longer maintained and is believed to be broken. 

You can replace Mediawiki::Edit with Mediawiki::API with little 
effort. Just replace \$editor->edit(...) with \$api->edit_page(...).

The edit_page() function in Mediawiki::API takes an additional argument,
an array reference of options. These are documented in the API docs.
The most important options are:

  'section'=>'new'   :  start a new section
  'bot'=>1           :  mark the edit as a bot edit

If your bot needs to detect edit conflicts, you need to read the API
editing docs for details on how to do that.

To disable this fatal error, in order to keep using Mediawiki::Edit,
edit the Mediawiki/Edit.pm file, and comment out the line that says 
"die \$deprecated_err".

HERE

die "$deprecated_err\n";


use strict;
use Data::Dumper;
use LWP::UserAgent;
use HTTP::Cookies;
use HTML::TokeParser;
use Encode;
use URI::Escape;

#   # Usage:
#
#   # Initialize
#   require Mediawiki::Edit;
#   my $client = Mediawiki::Edit->new();
#   $client->base_url('http://en.wikipedia.org/w');
#
#   # Log in
#   $client->login($user, $pass);
#    # OR #
#   $client->login_from_file($credentials_file_name);
#
#   # Edit
#   $client->edit($page, $text, $summary, $minor, $watch);
#   $client->append($talkpage, $text, $sectiontitle, 0, 0);

###########################################################

sub new { 
  my $self = {};

  my $class = shift;

  my $name = shift || 'Editor name';

  $self->{'agent'} = new LWP::UserAgent;
  $self->{'agent'}->cookie_jar(HTTP::Cookies->new());

  $self->{'baseurl'} = 'http://192.168.1.71/~mw/wiki';
  $self->{'indexurl'} = 'http://192.168.1.71/~mw/wiki/index.php';
  $self->{'apiurl'} = 'http://192.168.1.71/~mw/wiki/api.php';
  $self->{'loggedin'} = 'false';
  $self->{'maxRetryCount'} = 3;
  $self->{'debugLevel'} = 1;
  $self->{'maxlag'} = 5;
  $self->{'requestCount'} = 0;
  $self->{'htmlMode'} = 0;
  $self->{'decodeprint'} = 1;
  $self->{'dbLockedMessage'} = 'Database locked';
  $self->{'editFailedDelay'} = 5;

  $self->{'name'} = $name;

  bless($self);
  return $self;
}

#############################################################

sub base_url () { 
  my $self = shift;
  my $newurl = shift;

  if ( defined $newurl)  {
    $self->{'baseurl'} = $newurl;
    $self->{'indexurl'} = $newurl . "/index.php";
    $self->{'apiurl'} = $newurl . "/api.php";
    $self->print(1, "A Set base URL to: $newurl");
  }
  return $self->{'baseurl'};
}

####################################3

sub debug_level { 
  my $self = shift;
  my $level = shift;

  if ( defined $level) { 
    $self->{'debugLevel'} = $level;
    $self->print(1,"A Set debug level to: $level");
  }

  return $self->{'debugLevel'};
}

########################################################

sub html_mode  {
  my $self = shift;
  my $mode = shift;
  if ( defined $mode)  {
    $self->{'htmlMode'} = $mode;
    if ( $self->{'htmlMode'} > 0 ) { 
      $self->print(1, "A Enable HTML mode");
    } else {
      $self->print(1, "A Disable HTML mode");
    }
  }

  return $self->{'htmlMode'};
}


#####################################################3

sub maxlag { 
  my $self = shift;
  my $maxlag = shift;

  if ( defined $maxlag) { 
    $self->{'maxlag'} = $maxlag;
    $self->print(1,"A Maxlag set to " . $self->{'maxlag'});
  }

  return $self->{'maxlag'};
}


#############################################################3

sub name {
  my $self = shift;
  my $newname = shift;

  if ( defined $newname ) { 
    $self->{'name'} = $newname;
    $self->print(1,"A name set to " . $self->{'name'});
  }
  return $self->{'name'};
}

#############################################################3

sub login { 
  my $self = shift;
  my $userName = shift;
  my $userPassword = shift;

  $self->print(1,"A Logging in");

  my $res;

  $res = $self->makeHTMLrequest('post',
          [ 'title' =>  'Special:UserLogin',
            'action' => 'submitlogin',
            'type' => 'login',
            'wpLoginattempt' => 'Log in',
            'wpName'     => $userName,
            'wpPassword' => $userPassword,
            'wpRemember' => 1] );

  $res = $self->makeHTMLrequest('post',
        ['title'=>'Special:UserLogin','wpCookieCheck'=>'login']);

  my $content = $res->content();

  $self->print(5, "Content 2: '$content'");

  if ( $res->code() == 200 ) { 
    $self->print(1,  "E Login error.");
    exit;
  } elsif ( $res->code() ==  302 ) { 
    $self->print(1,"R Login successful");
    $self->{'loggedin'} = 'true';
  } else { 
    $self->print(1,  "E Login error (strange HTTP response code).");
    exit;
  }

#  if ( $content =~ m/var wgUserName = "$userName"/ ) {
#    $self->print(1,"R Login successful");
#    $self->{'loggedin'} = 'true';
#  } else {
#    if ( $content =~ m/There is no user by the name/ ) {
#       $self->{errstr} = qq/Login  failed: User does not exist/;
#    } elsif ( $content =~ m/Incorrect password entered/ ) {
#       $self->{errstr} = qq/Login failed: Bad password/;
#    } elsif ( $content =~ m/Password entered was blank/ ) {
#       $self->{errstr} = qq/Login failed: Blank password/;
#    }
#    $self->print(1,  "E Login error.");
#    exit;
#  }

}

##################################

sub login_from_file {
  my $self = shift;
  my $file = shift;
  open IN, "<$file" or die "Can't open file $file: $!\n";

  my ($a, $b, $user, $pass, $o);
  $o = $/;   # Paranoia
  $/ = "\n";
  while ( <IN> ) { 
    chomp;
    ($a, $b) = split /\s+/, $_, 2;
    if ( $a eq 'user') { $user = $b;}
    if ( $a eq 'pass') { $pass = $b;}
  }

  close IN;
  $/ = $o;

  if ( ! defined $user ) { 
    die "No username to log in\n";
  }

  if ( ! defined $pass ) { 
    die "No password to log in\n";
  }

  $self->login($user, $pass);
}

#############################################################3

sub cookie_jar {

  my $self = shift;
  return $self->{'agent'}->cookie_jar();

}

#############################################################3

sub add_maxlag_param {
  my $self = shift;
  my $arr = shift;

  if ( defined $self->{'maxlag'} && $self->{'maxlag'} >= 0 ) { 
    push @$arr, 'maxlag';
    push @$arr, $self->{'maxlag'};
  }
}


sub add_maxlag_url { 
  my $self = shift;
  my $url = shift;

  if ( defined $self->{'maxlag'} && $self->{'maxlag'} >= 0 ) { 
    $url .= '&maxlag=' . $self->{'maxlag'};
  }

  return $url;
}

######################################

sub makeHTMLrequest {
  my $self = shift;
  my $type = shift;
  my $args = shift;

  my $url = $self->{'indexurl'};

  $self->print(2, "A Making HTML request (" . $self->{'requestCount'} . ")");

  if ( $type eq 'post' ) {
    $self->add_maxlag_param($args);
    $self->print(5, "I URL: " . $url);

    my $k = 0;
    while ( $k < scalar @{$args}) { 
      $self->print(5, "I \t" . ${$args}[$k] . " => " . ${$args}[$k+1]);
      $k += 2;
    }
  } else { 
    $url = ${$args}[0];
    $url = $self->add_maxlag_url($url);
    $self->print(5, "I URL: " . $url);
  }

  my $retryCount = 0;
  my $delay = 4;
 
  my $res;

  while (1) { 
    $self->{'requestCount'}++;

    if ( $retryCount == 0) { 

    } else { 
      $self->print(1,"A Repeating request ($retryCount)");
    }

    if ( $type eq 'post') { 
      $res = $self->{'agent'}->post($url, $args);
    } else {
      $res = $self->{'agent'}->get($url);
    }


    last if $res->is_success();
    last if $res->is_redirect();

    $self->print(1, "I HTTP response code: " . $res->code() ) ;
    $self->print(5, "I HTTP response content: " . $res->content() ) ;

    if (defined $res->header('x-squid-error')) { 
      $self->print(1,"I \tSquid error: " 
                               . $res->header('x-squid-error'));
    }

    $retryCount++;

#   $self->print(1, Dumper($res->headers));

    if ( defined $res->header('retry-after')) { 
      $delay = $res->header('x-database-lag');
      $self->print(2,"I Maximum server lag exceeded");
      $self->print(3,"I Current lag $delay, limit " 
                                             . $self->{'maxlag'});

#      print Dumper($res);
    }

    $self->print(1, "I sleeping for " . $delay . " seconds");

    sleep $delay;

    if ( $delay < 30) { 
      $delay = $delay * 2;
    } else { 
      $delay = 60;
    }
     
    if ( $retryCount > $self->{'maxRetryCount'}) { 
      my $errorString = 
           "Exceeded maximum number of tries for a single request.\n";
      $errorString .= 
       "Final HTTP error code was " . $res->code() . " " . $res->message . "\n";
      $errorString .= "Aborting.\n";
      die($errorString);
    }
  }

#  $self->print(6, Dumper($res));

  return $res;
}


#############################################################

sub dump { 
  my $self = shift;
  return Dumper($self);
}


##############################################


sub get_edit_token { 
  my $self = shift;
  my $page = shift;
  my $section = shift;

  $self->print(1, "I Get token for $page");

  my $url = $self->{'indexurl'} . "?title=" 
             . uri_escape($page) . "&action=edit";

  if ( defined $section ) { 
    $url .= '&section=' . $section;
  }

  my $res = $self->makeHTMLrequest('get', [ $url ]);

  my $content = $res->content();

  my $p = HTML::TokeParser->new(\$content);
  my $edittime;
  my $starttime;
  my $edittoken;
  my $edittext;
  my $tag;
  while ($tag = $p->get_tag('input')) {
    next unless $tag->[1]->{type} eq 'hidden';
    if ( $tag->[1]->{name} eq 'wpEdittime') { 
       $edittime = $tag->[1]->{value};
    } elsif ( $tag->[1]->{name} eq 'wpStarttime') { 
       $starttime =  $tag->[1]->{value}; 
    } elsif ( $tag->[1]->{name} eq 'wpEditToken') { 
       $edittoken =  $tag->[1]->{value}; 
    }
  }

  # Inefficient; should use HTML::Parser directly to avoid the second pass
  $p = HTML::TokeParser->new(\$content);
  while ($tag = $p->get_tag('textarea')) {
    if ( $tag->[1]->{name} eq 'wpTextbox1') { 
       $edittext =  $p->get_text();
    }
  }

  return ($edittoken, $edittime, $starttime, $edittext);
}

#######################################################

sub edit { 
  my $self = shift;
  my $page = shift;
  my $text     = shift;
  my $summary  = shift;
  my $is_minor = shift || '0';
  my $is_watched = shift || '0';

  my ($edittoken, $edittime, $starttime, $edittext);

  if ( $self->{'loggedin'} eq 'false' ) { 
    die "Attempted to edit while not logged in, aborting.\n";
  }

  $self->print(1, "A Commit $page (edit summary: '$summary')");

  my $try = 0;
  my $maxtries = $self->{'maxRetryCount'};
  my $getToken = 1;

  while (1) { 
    $try++;

    if ( $getToken == 1) { 
      ($edittoken, $edittime, $starttime, $edittext) =  
                            $self->get_edit_token($page);

      if ( defined $edittoken) { 
        $getToken = 0; 
      } else {
        next;  
      }

      if ( $edittext eq $text) { 
        $self->print(2,"I server text matches text to upload. Not making an edit");
        return;
      }	
    }


    my $queryParameters =   [ "action" => "submit",
                              "title" => $page,
                              "wpTextbox1"    => $text,
                              "wpSummary"     => $summary, 
                              "wpSave"        => 'Save Page',
                              "wpEdittime"    => $edittime,
                              "wpStarttime" => $starttime,
                              "wpEditToken"   => $edittoken ];

  if ( defined ($is_watched) && $is_watched == 1) { 
      $queryParameters = [@$queryParameters, ["wpWatchthis" => 1]];
   }

   if ( defined($is_minor) && $is_minor == 1) { 
      $queryParameters = [@$queryParameters, ["wpMinoredit" => 1]];
   }

    my $res = $self->makeHTMLrequest('post',$queryParameters);


    if ( $res->code() == 302 ) { 
      $self->print(2, "I Edit successful");
      last;
    } elsif ( $res->code() == 200) { 
      $self->print(1, "E Edit unsuccessful ($try/$maxtries)");
     
      if ( $res->header('title') =~ /^\Q$self->{'dbLockedMessage'}\E/ ) {
        $self->print(2, "I  Databased locked, retrying\n");
        $try--;
        $getToken = 1;
      } else {    
        print Dumper($res);
      }

      sleep $self->{'editFailedDelay'};

      if ( $try >= $maxtries) { 
        $self->print(1, "E Too many tries, giving up");
        last;
      }
    }
  }
}


################################################################
sub edit_section  { 
  my $self = shift;
  my $page = shift;
  my $section = shift;
  my $text     = shift;
  my $summary  = shift;
  my $is_minor = shift || '0';
  my $is_watched = shift || '0';

  my ($edittoken, $edittime, $starttime, $edittext);

  if ( $self->{'loggedin'} eq 'false' ) { 
    die "Attempted to edit while not logged in, aborting.\n";
  }


  if ( ! ( $section =~ /^\d+$/ ) ) { 
    die "Section '$section' invalid, must be nonnegative integer.\n";
  }

  $self->print(1, "A Commit section $section of $page (edit summary: '$summary')");

  my $try = 0;
  my $maxtries = $self->{'maxRetryCount'};
  my $getToken = 1;

  while (1) { 
    $try++;

    if ( $getToken == 1) { 
      ($edittoken, $edittime, $starttime, $edittext) =  
                            $self->get_edit_token($page, $section);

      if ( defined $edittoken) { 
        $getToken = 0; 
      } else {
        next;  
      }

      if ( $edittext eq $text) { 
        $self->print(2,"I server text matches text to upload. Not making an edit");
        return;
      }	
    }

    my $queryParameters =   [ "action" => "submit",
                              "title" => $page,
                              "wpTextbox1"    => $text,
                              "wpSummary"     => $summary, 
                              "wpSection"     => $section,
                              "wpSave"        => 'Save Page',
                              "wpEdittime"    => $edittime,
                              "wpStarttime" => $starttime,
                              "wpEditToken"   => $edittoken ];

  if ( defined ($is_watched) && $is_watched == 1) { 
      $queryParameters = [@$queryParameters, ["wpWatchthis" => 1]];
   }

   if ( defined($is_minor) && $is_minor == 1) { 
      $queryParameters = [@$queryParameters, ["wpMinoredit" => 1]];
   }

    my $res = $self->makeHTMLrequest('post',$queryParameters);


    if ( $res->code() == 302 ) { 
      $self->print(2, "I Edit successful");
      last;
    } elsif ( $res->code() == 200) { 
      $self->print(1, "E Edit unsuccessful ($try/$maxtries)");
     
      if ( $res->header('title') =~ /^\Q$self->{'dbLockedMessage'}\E/ ) {
        $self->print(2, "I  Databased locked, retrying\n");
        $try--;
        $getToken = 1;
      } else {    
        print Dumper($res);
      }

      sleep $self->{'editFailedDelay'};

      if ( $try >= $maxtries) { 
        $self->print(1, "E Too many tries, giving up");
        last;
      }
    }
  }
}


################################################################

sub append { 
  my $self = shift;
  my $page = shift;
  my $text     = shift;
  my $summary  = shift;
  my $is_minor = shift || 0;
  my $is_watched = shift || 0;

  my ($edittoken, $edittime, $starttime);

  $self->print(1, "E Commit $page (msg: $summary)");

  my $try = 0;
  my $maxtries = $self->{'maxRetryCount'};

  my $getToken = 1;

  while (1) { 
    $try++;

    if ( $getToken == 1) { 
      ($edittoken, $edittime, $starttime) =  
                            $self->get_edit_token($page);

      if ( defined $edittoken) { 
        $getToken = 0; 
      } else {
        next;  
      }
    }

    my $queryParameters = [ "action" => "submit",
                            "title" => $page,
                            "wpSection" => 'new',
                            "wpTextbox1"    => $text,
                            "wpSummary"     => $summary, 
                            "wpSave"        => 'Save Page',
                            "wpEdittime"    => $edittime,
                            "wpStarttime" => $starttime,
                            "wpEditToken"   => $edittoken ];



   if ( defined ($is_watched) && $is_watched == 1) { 
      $queryParameters = [@$queryParameters, ["wpWatchthis" => 1]];
   }

   if ( defined($is_minor) && $is_minor == 1) { 
      $queryParameters = [@$queryParameters, ["wpMinoredit" => 1]];
   }


    my $res = $self->makeHTMLrequest('post', $queryParameters);

    if ( $res->code() == 302 ) { 
      $self->print(2, "I Edit successful");
      last;
    } elsif ( $res->code() == 200) { 
      $self->print(1, "E Edit unsuccessful ($try/$maxtries)");

      if ( $res->header('title') =~ /^\Q$self->{'dbLockedMessage'}\E/ ) {
        $self->print(2, "I  Databased locked, retrying\n");
        $try--;  
        $getToken = 1;  
      } else {    
        print Dumper($res);
      }
      sleep $self->{'editFailedDelay'};

      if ( $try == $maxtries) { 
        $self->print(1, "E Too many tries, giving up");
        last;
      }
    }
  }
}

################################################################

sub print { 
  my $self = shift;
  my $limit = shift;
  my $message = shift;

  if ( defined $self->{'name'} ) { 
    $message = $self->{'name'} . ": " . $message;
  }

  if ( $self->{'decodeprint'} == 1) { 
    $message = decode("utf8", $message);
  }

  if ( $limit <= $self->{'debugLevel'} ) {
    print $message;
    if ( $self->{'htmlMode'} > 0) { 
      print " <br/>\n";
    } else { 
      print "\n";
    }
  }
}


########################################################
## Return success upon loading class
1;

