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
my $logname = "./SCRAMBLELOG";

my $WinCount;
my $LossCount;
my $word;

# Get parameters
open (my $fh, "<", $logname) or die "No logfile...";
while (my $Line = <$fh>){
  chomp $Line;
  my @LN = split(/:/, $Line);
  if ($LN[0] eq "LC") {$LossCount=$LN[1]};
  if ($LN[0] eq "WC") {$WinCount=$LN[1]};
  if ($LN[0] eq "Word") {$word=$LN[1]};  
}
close $fh;

my $InputWord=$q->param('WordGuess');
my $text=$InputWord;


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
} elsif (is_anagram($text, $word) && is_word($text)) {
  $WinCount++;    # increment wincount
} else {$LossCount++;}		#increment losscount



# Update log file with change counts.
## Write to file
open (my $fh, ">", $logname);
print $fh "LC:$LossCount\n";   
print $fh "WC:$WinCount\n";
print $fh "Word:$word\n";
close $fh;

# Redirect back to scramble_basic with the changed counts.
print $q->redirect('./scramble_basic.cgi');
