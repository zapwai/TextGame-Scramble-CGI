#!/usr/bin/perl -Tw
# David Ferrone, 2016
#
#
##############
# This processes the input (checks whether you were correct or not).
# It passes variables with GET...
# It makes more sense to write to a file, to keep track of these things.
# This is more of a 'proof of concept'.
####################

use CGI;
my $q = CGI->new;

my $filename = "./words";

my $Mode=$q->param('Mode');

my $WinCount=$q->param('WC');
my $LossCount=$q->param('LC');
my $word=$q->param('WORD');


my $InputWord=$q->param('WordGuess');
my $text=$InputWord;

## Moderate Settings
my $ClockTime = $q->param('TimeLeft');
my $PrevTime = $q->param('PrevTime');

my $CurrentTime = time;
my $ElapsedTime = $CurrentTime - $PrevTime;  # Number of seconds that you sat there before clicking submit

# Updating $ClockTime (time left)
$ClockTime = $ClockTime - $ElapsedTime;
  

## Hard Settings

sub is_word{
  # Input: $text, a string
  # Output: 1 if $text is a word in /usr/dict/words, 0 otherwise.
  my $text = $_[0];    
  open(my $file,  "<",  $filename)  or die "Can't open dictionary: $!";
  @words = <$file>;
  close($file);

  chomp @words;

  my $n = 0;

  while ($n <= $#words) {
    if ($words[$n] eq $text) {
      return 1;
    } else {
      $n++;
    }
  }
  return 0;
}

sub is_anagram{
  # Returns true if the two strings passed as variables are anagrams.  
  my ($s1, $s2) = @_;
  return (join '', sort { $a cmp $b } split(//, $s1)) eq
    (join '', sort { $a cmp $b } split(//, $s2));
}

$text = lc($text);	
$word = lc($word);
if ($text eq $word) {
  $WinCount++;			#increment wincount
  if ($Mode eq "hard") { $ClockTime += 6*(4+$WinCount)} # Add time in hard mode
} elsif (is_anagram($text, $word) && is_word($text)) {
  $WinCount++;    # increment wincount
  if ($Mode eq "hard") { $ClockTime += 6*(4+$WinCount)} # Add time in hard mode
} else {$LossCount++;}		#increment losscount

## Make html page which contains a form, and passes these parameters with post...
## autosubmits with javascript. 
print $q->header;
print "<html>";
print <<CSS;
<style>
body {background-image: url("./cork-wallet.png");}
</style>
CSS
print "<body>";
print qq( <form action="./scramble_$Mode.cgi" method="post" id="MyForm"> );
print <<HTMLPAGE;
<input type=hidden name=WC value=$WinCount>
<input type=hidden name=LC value=$LossCount>
<input type=hidden name=WORD value=$word>
<input type=hidden name=WordGuess value=$text>
<input type=hidden name=TimeLeft value=$ClockTime>
<input type="submit" value="Submit">
</body></html>
HTMLPAGE
print <<JAVAMAN;
<script>
document.getElementById('MyForm').submit();
</script>
JAVAMAN
