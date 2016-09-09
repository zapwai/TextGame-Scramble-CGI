#!/usr/bin/perl
#
# Thanks for playing SCRAMBLE!
# Copyright David Ferrone, Aug 2014
# Update (CGI) Sept 2016
##############################
# Keep words in the same directory.  
# You can find this in /usr/dict/words or /usr/share/dict/words

use CGI;
my $q = CGI->new;

print "Content-type: text/html\n\n";
print <<END;
<html>
<head>
<title>Scramble Moderate -- The CGI Version!</title>
<style>
a {text-decoration: none; font-size:x-small; font-weight:normal; color:green}
a:hover {text-decoration: underline; font-size:x-small; font-weight:bold; color:green;}
a:visited {color:green}
td { padding: 10px; background-color:#E5E7E9}
body {background-image: url("./cork-wallet.png");}
p { font-family: "Georgia"}
.words { font-family: "Courier New"}
</style>
<!-- Thank you subtlepatterns.com for the background -->
</head>
<body>
<br>
<p>
<table style="margin:1em auto;" width="75%" height="25%">
<tr>
<td>
<center>
END
# Moderate game word length is 6, and time is set to 30 seconds.
my $WordLength = 6;

# get clock time left
my $ClockTime = $q->param('TimeLeft');

# Relevant files.
my $filename = "./words";

## Using parameters passed via query string.
my $WinCount=$q->param('WC');
my $LossCount=$q->param('LC');
my $PreviousWord=$q->param('WORD');
my $PreviousGuess=$q->param('WordGuess');

if ($WinCount eq ""){ $WinCount = 0; $PreviousWord="";};
if ($LossCount eq ""){ $LossCount = 0; };
if ($ClockTime eq ""){ $ClockTime = 30; };

print "Loss Count: $LossCount, &nbsp&nbsp&nbsp&nbsp";
print "Win Count: $WinCount, &nbsp&nbsp&nbsp&nbsp";
print "<br>";

unless ($LossCount == 0 and $WinCount == 0){print "Previous Word: <span class='words'> $PreviousWord</span>, &nbsp&nbsp&nbsp&nbsp";
					    print "You said: <span class='words'> $PreviousGuess</span><br>";
					    print "Time Left: $ClockTime seconds";
					    print "<br><br>";
					  };

#~~~~~~~~~~~~~~~~~~~~~~~~

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
  my $word = select_word($WordLength);	# word of length WordLength!
  
  my @NewWord = mix_word($word); # NewWord is a permutation of word
  print "<br>The scrambled word is...<br>","<div class='words'>",@NewWord,"</div><br>";

  my $StartTime = time;      
  print <<MENUINPUT;
  <form action="scramble_input.cgi" method="post">
  Your Guess: <input type="text" name="WordGuess" autofocus>
<input type=hidden name=WC value=$WinCount>
<input type=hidden name=LC value=$LossCount>
<input type=hidden name=WORD value=$word>
<input type=hidden name=TimeLeft value=$ClockTime>
<input type=hidden name=PrevTime value=$StartTime>
<input type=hidden name=Mode value="moderate">
<input type="submit" value="Submit">
</form>
MENUINPUT

  print "<a href='./scramble.html'>Back</a>";
  print "&nbsp&nbsp&nbsp";
  print "<a href='./'>zapwai.net</a>";
  print "&nbsp&nbsp&nbsp";
  print qq/<a href="mailto:zapwai\@gmail.com">Contact<\/a>/;
  
  print "</center>";

  print "</td></tr></table>";

  print "</body></html>";  
}

sub moderate_game{
  # This game ends after 30 seconds have passed.
  # The time is checked with $StartTime.
  # The time is checked again in the input script, the difference is deducted from $ClockTime and passed back here.
  if ($ClockTime > 0){
    the_game();
  }
  elsif ($ClockTime <= 0){print "Time up! Your overall win count was $WinCount!<br>";
			  print qq(<a href="./scramble_moderate.cgi">Play Again</a>);
			  print qq(<br><a href="./">zapwai.net</a>);
			  print "</body></html>";
			}
}

moderate_game();
