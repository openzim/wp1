use Data::Dumper;
use LWP::UserAgent;


sub tusc_verify_password {
  my $user = shift;
  my $pass = shift;
  my $ua = LWP::UserAgent->new();

  my $r = $ua->post("http://toolserver.org/~magnus/tusc.php", 
                    [ "check"=>1,
                     "botmode"=>1,
                     "user"=>$user,
                     "password"=>$pass,
                     "language"=>"en",
                     "project"=>"wikipedia"]);


  $r = $r->decoded_content();

  if ( $r eq "1" ) { 
    return 1;
  } else { 
    return 0;
  }
}

1;
