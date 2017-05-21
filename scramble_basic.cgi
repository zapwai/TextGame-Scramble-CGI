#!/usr/bin/perl
# Thanks for playing SCRAMBLE!
# Copyright David Ferrone, Aug 2014
# Update (CGI) Aug 2016
# Update (High scores) Apr 2017
# Update (Cookie, Private parameters, Refresh cheat) May 2017
############################################################
# Keep words file in the same directory.  
# You can find this in /usr/dict/words or /usr/share/dict/words
############################################################
# To stop the 'refresh cheat':
# (If you hit refresh you used to get a new word, no punishment.)
# We store @NewWord in $DATA[7] (the scrambled word),
# We store a 0 or 1 flag in $DATA[8]
# (0 means we need a word yet, 1 means we have not submitted an answer.)
############################################################
use CGI;

my $q = CGI->new;
my $filenum;
sub eat_cookie{
    my $cookie = $q->cookie('BasicCookie');
    if ( !"$cookie" ) {
	do {
	    $filenum = int rand(10000);
	}  while (-e "_$filenum.txt") ;
	# This will guarantee no conflict with multiple users.

	$cookie = $q->cookie(-name=>'BasicCookie',
			     -value=>"$filenum",
			     -expires=>'+2h',
			 );
    } else {
	$filenum = $cookie;	   
    }
    return $cookie;
}

sub set_datafile{
    ##  WC, LC, WORD, GUESS, MODE, ClockTime left, time at load, Scrambled word, refresh_flag (with new lines)
    my $DataFile = "_$filenum.txt";
    open (my $FH, ">", $DataFile);
    print $FH "0\n0\n\n\nbasic\n30\n".time."\n\n0\n";
    close $FH;
    chmod 0640, $DataFile;
}

my $cookie = eat_cookie();	# Cookie sets or gets UID ($filenum)
print $q->header(-cookie=>$cookie);
my $DataFile = "_$filenum.txt";
unless (-e $DataFile){
    set_datafile();		# Create file if necessary.
}

print <<END;
<html>
    <head>
    <title>Scramble Basic -- The CGI Version!</title>
    <style>
    a {text-decoration: none; font-size:x-small; font-weight:normal; color:green}
 a:hover {text-decoration: underline; font-size:x-small; font-weight:bold; color:green;}
 a:visited {color:green}
td { padding: 10px; background-color:#E5E7E9}
  p { font-family: "Georgia"}
  .words { font-family: "Courier New"}
  </style>
      </head>
      <body>
      <br>
      <p>
      <table style="margin:1em auto;" width="75%" height="25%">
      <tr>
      <td>
      <center>
END
# Basic game word length is 5.
my $WordLength = 5;

# Relevant files.
my $filename = "./words";

open (my $FH, "<", $DataFile);
my @DATA = <$FH>;		# Contains parameters.
close $FH;

my $WinCount=$DATA[0];
my $LossCount=$DATA[1];
my $PreviousWord=$DATA[2];
my $PreviousGuess=$DATA[3];
my $ScrambledWord=$DATA[7];
my $RefreshFlag=$DATA[8];
print "Loss Count: $LossCount, &nbsp&nbsp&nbsp&nbsp";
print "Win Count: $WinCount, &nbsp&nbsp&nbsp&nbsp";
print "<br>";

# Print previous word, unless you just started playing.
unless (($LossCount == 0 and $WinCount == 0) or ($RefreshFlag==1)) {
    print "Previous Word: <span class='words'> $PreviousWord</span>, &nbsp&nbsp&nbsp&nbsp";
    print "You said: <span class='words'> $PreviousGuess </span><br>";
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

sub select_word{
    #input: length of word, an integer.
    #output a random word from /usr/dict/words of that length.
    my $DesiredLength = shift;
    my $SelectedWord;
    my $CandidateCount = 0;

    open my $dict_fh, '<', $filename
	or die "Can't read words file: $!\n";
  WORD:
    while ( my $word = <$dict_fh> ) {
	chomp $word;
	next WORD if length $word != $DesiredLength;
	$SelectedWord = $word if rand ++$CandidateCount < 1;
    }
    return $SelectedWord;
}

sub mix_word{
    #input: a string
    #output: a permutation of that string (an array)
    my $word = shift;
    my @NewWord;
    my @Letters = split(//, $word);

    while ($#Letters >= 0) {
	my $N = int ( rand($#Letters) );
	($Letters[$N], $Letters[$#Letters]) =
	    ($Letters[$#Letters], $Letters[$N]); push
	    @NewWord, pop @Letters;
    }
    return @NewWord;
}

# ~~~~~~~~~~~ ~~~~~~~~~~~ ~~~~~~~~~~~ ~~~~~~~~~~~ ~~~~~~~~~~~

sub the_game{
    # The actual word, $word, is selected and written to our datafile.
    my @NewWord; #The scrambled word.
    my $word;
    unless ($RefreshFlag == 1) {
	$word = select_word($WordLength);
	@NewWord = mix_word($word); # NewWord is a permutation of word.

	open (my $FH, ">", $DataFile);
	for my $k (0 .. $#DATA) {
	    if ($k == 2) {
		print $FH $word."\n";
	    } elsif ($k == 7) {
		print $FH @NewWord,"\n"; 
	    } elsif ($k == 8) {
		print $FH "1\n";
	    } else {
		print $FH $DATA[$k];
	    }
	}
	close $FH;
    }
    
    if ($RefreshFlag==1){
	@NewWord = $DATA[7];
    }

    print "<br>The scrambled word is...<br>","<div class='words'>",@NewWord,"</div><br>";

    print <<SUBFORM;
      <form action="scramble_input.cgi" method="post">
	  Your Guess: <input type="text" name="WordGuess" maxlength=$WordLength autofocus>
	  <input type=hidden name=UID value=$filenum>
	  <input type="submit" value="Submit">
	  </form>
SUBFORM
	  
    print "<a href='./scramble.html'>Back</a>";
    print "&nbsp&nbsp&nbsp";
    print "<a href='../'>zapwai.net</a>";
    print "&nbsp&nbsp&nbsp";
    print qq/<a href="mailto:zapwai\@gmail.com">Contact<\/a>/;
    print "</center>";
    print "</td></tr></table>";
    print "</body></html>";  
}
  
sub basic_game{
    # 3 losses will end the game in the basic version.
    if ($LossCount < 3) {
	the_game();
    } elsif ($LossCount > 2) {
	print "Your overall win count was $WinCount!<br>";
	# Add this to the losing case (last elsif) in each scramble_<mode>.cgi
	print <<ITSAFORM;
	  <br>
	  <form action="highscore.cgi" method="post">
	      Please enter your initials: <br>
	      <input type="text" name=User autofocus>
	      <input type=hidden name=UID value=$filenum>  
	      <input type="submit" value="Submit">
	      </form><p>
ITSAFORM
	print qq(<a href="./scramble_basic.cgi">Play Again</a>);
	print qq(<br><a href="./scramble.html">Back</a>);
	print qq(<br><a href="../">zapwai.net</a>);
	print "</body></html>";
    }
}

basic_game();


