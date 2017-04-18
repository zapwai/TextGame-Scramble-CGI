#!/usr/bin/perl
#
# Thanks for playing SCRAMBLE!
# Copyright David Ferrone, Aug 2014
# Update (CGI) Aug 2016
# Update (High scores) Apr 2017
##############################
# Keep words file in the same directory.  
# You can find this in /usr/dict/words or /usr/share/dict/words

# Need to receive WinCount (&WC), LossCount (&LC)
# (Could also pass Word and WordGuess to print confirmation...)
##############################

use CGI;
my $q = CGI->new;

print "Content-type: text/html\n\n";
print <<END;
<html>
    <head>
    <title>Scramble Basic -- The CGI Version!</title>
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
# Basic game word length is 5.
my $WordLength = 5;

  # Relevant files.
  my $filename = "./words";

  ## Using parameters passed via query string.
  my $WinCount=$q->param('WC');
  my $LossCount=$q->param('LC');
  my $PreviousWord=$q->param('WORD');
  my $PreviousGuess=$q->param('WordGuess');


  if ($WinCount eq "") {
      $WinCount = 0; $PreviousWord="";
  }
  ;
  if ($LossCount eq "") {
      $LossCount = 0;
  }
  ;

  print "Loss Count: $LossCount, &nbsp&nbsp&nbsp&nbsp";
  print "Win Count: $WinCount, &nbsp&nbsp&nbsp&nbsp";
  print "<br>";

  # Print previous word, unless you just started playing.
  unless ($LossCount == 0 and $WinCount == 0){print "Previous Word: <span class='words'> $PreviousWord</span>, &nbsp&nbsp&nbsp&nbsp";
					      print "You said: <span class='words'> $PreviousGuess </span><br>";
  }
  ;


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
      my $word = select_word($WordLength); # word of length WordLength!
      
      my @NewWord = mix_word($word); # NewWord is a permutation of word
      print "<br>The scrambled word is...<br>","<div class='words'>",@NewWord,"</div><br>";


      print <<SUBFORM;
      <form action="scramble_input.cgi" method="post">
	  Your Guess: <input type="text" name="WordGuess" autofocus>
	  <input type=hidden name=WC value=$WinCount>
	  <input type=hidden name=LC value=$LossCount>
	  <input type=hidden name=WORD value=$word>
	  <input type=hidden name=Mode value="basic">
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
      # Loops are bad on a web page?  Seems poorly thought out to use a while loop...
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
	      <input type=hidden name=WC value=$WinCount>
	      <input type=hidden name=HSMode value="easy">  
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


