#!/usr/bin/perl
#
# Thanks for playing SCRAMBLE!
# Copyright David Ferrone, Aug 2014
# Update (CGI) Sept 2016
##############################
# Keep words in the same directory.  
# You can find this in /usr/dict/words or /usr/share/dict/words

use CGI;
use CGI::Carp qw(fatalsToBrowser);
my $q = CGI->new;

my $filenum;
sub eat_cookie{
    my $cookie = $q->cookie('MyCookie');
    if ( !"$cookie" ) {
	$filenum = int rand(1000);
	$cookie = $q->cookie(-name=>'MyCookie',
			     -value=>"$filenum",
			     -expires=>'+2h',
			 );
    } else {
	$filenum = $cookie;	   
    }
    return $cookie;
}

sub set_datafile{
    #WC, LC, WORD, GUESS, MODE, ClockTime, PrevTime(with new lines)
    my $DataFile = "_$filenum.txt";
    open (my $FH, ">", $DataFile);
    print $FH "0\n0\n\n\nhard\n30\n".time."\n";
    close $FH;
    chmod 0640, $DataFile;
}

my $cookie = eat_cookie();	# Cookie sets or gets UID ($filenum)
print $q->header(-cookie=>$cookie);
my $DataFile = "_$filenum.txt";
unless (-e $DataFile){
    set_datafile();		# Create file if necessary.
}

open (my $FH, "<", $DataFile);
my @DATA = <$FH>;
close $FH;

my $WinCount=$DATA[0];
my $LossCount=$DATA[1];
my $PreviousWord=$DATA[2];
my $PreviousGuess=$DATA[3];
my $Mode=$DATA[4];

# get clock time left, this should be second to last line.
my $ClockTime = $DATA[5];

print <<END;
<html>
<head>
<title>Scramble Hard -- The CGI Version!</title>
<style>
a {text-decoration: none; font-size:x-small; font-weight:normal; color:green}
a:hover {text-decoration: underline; font-size:x-small; font-weight:bold; color:green;}
a:visited {color:green}
td { padding: 10px; background-color:#E5E7E9}
p { font-family: "Georgia"}
.words { font-family: "Courier New"}
</style>
<script>
var count=$ClockTime;
var counter=setInterval(timer, 1000);
function timer(){count = count - 1; document.getElementById("timer").innerHTML=count}
</script>
</head>
<body>
<br>
<p>
<table style="margin:1em auto;" width="75%" height="25%">
<tr>
<td>
<center>
END

# Hard game word length begins at 4, and time is set to 30 seconds.
# As you win, the length gets longer and you get additional time.
my $WordLength = 4;

# Relevant files.
my $filename = "./words";

$WordLength += $WinCount;

print "Loss Count: $LossCount, &nbsp&nbsp&nbsp&nbsp";
print "Win Count: $WinCount, &nbsp&nbsp&nbsp&nbsp";
print "<br>";

unless ($LossCount == 0 and $WinCount == 0){print "Previous Word: <span class='words'> $PreviousWord</span>, &nbsp&nbsp&nbsp&nbsp";
					    print "You said: <span class='words'> $PreviousGuess</span><br>";
					}
;
unless ($ClockTime <= 0 or $ClockTime == 30 or $LossCount > 0){
    print "Time Left: <span id='timer'>$ClockTime</span> seconds"; # Javascript countdown...
    print "<br><br>";
}
;

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

sub select_word{
    #input: length of word, an integer.
    #output a random word from /usr/dict/words of that length.

    my $DesiredLength = @_[0];
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
    my $word = @_[0];
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
    # The actual word, $word, is selected and written to SCRAMBLELOG.
    my $word = select_word($WordLength); # word of length WordLength!
    open (my $FH, ">", $DataFile);
    for my $k (0 .. $#DATA) {
	if ($k == 2) {
	    print $FH $word."\n";
	} else {
	    print $FH $DATA[$k];
	}
    }
    close $FH;
  
    my @NewWord = mix_word($word); # NewWord is a permutation of word
    print "<br>The scrambled word is...<br>","<div class='words'>",@NewWord,"</div><br>";

    print <<MENUINPUT;
  <form action="scramble_input.cgi" method="post">
  Your Guess: <input type="text" name="WordGuess" autofocus>
<input type=hidden name=UID value=$filenum>
<input type="submit" value="Submit">
</form>
MENUINPUT

    print "<a href='./scramble.html'>Back</a>";
    print "&nbsp&nbsp&nbsp";
    print "<a href='../'>zapwai.net</a>";
    print "&nbsp&nbsp&nbsp";
    print qq/<a href="mailto:zapwai\@gmail.com">Contact<\/a>/;
    print "</center>";
    print "</td></tr></table>";
    print "</body></html>";  
}

sub hard_game{
    # This game ends after 30 seconds have passed.
    # The time is checked with $StartTime.
    # The time is checked again in the input script, the difference is deducted from $ClockTime and passed back here.
    if (($ClockTime <= 0) or ($LossCount == 1)) {
	print "Game over! Your overall win count was $WinCount!<br>";
# Add this to the losing case (last elsif) in each scramble_<mode>.cgi
	print <<FORM;
	  <br>	
<form action="highscore.cgi" method="post">
Please enter your initials: <br>
<input type="text" name=User autofocus>
<input type=hidden name=UID value=$filenum>  
<input type="submit" value="Submit">
</form>
FORM
	print qq(<a href="./scramble_hard.cgi">Play Again</a>);
	print qq(<br><a href="./scramble.html">Back</a>);			 
	print qq(<br><a href="../">zapwai.net</a>);
	print "</body></html>";
    } elsif ($ClockTime > 0) {
	the_game();
    }
}

hard_game();

