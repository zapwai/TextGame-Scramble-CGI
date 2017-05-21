#!/usr/bin/perl
# David Ferrone, 2016
####################
# This processes the input (checks whether you were correct or not).
####################
use CGI;

sub strip{			# Thanks PerlMaven!
    my $str = shift;
    $str =~ s/^\s+|\s+$//g;
    return $str;
}

my $q = CGI->new;

my $words_filename = "./words";
my $filenum = $q->param('UID');
my $DataFile = "_$filenum.txt";
my $InputWord=$q->param('WordGuess');
my $text=strip($InputWord);

open (my $FH, "<", $DataFile);
my @DATA = <$FH>;		# Contains parameters.
close $FH;
chomp(@DATA);
my $WinCount=$DATA[0];
my $LossCount=$DATA[1];
my $word=$DATA[2]; 
#The inputted $text is $DATA[3], we will write it in a moment.
my $Mode=$DATA[4];

## Moderate and Hard ClockTime Settings
my $ClockTime;
my $PrevTime;

$ClockTime = $DATA[5];
$PrevTime = $DATA[6]; # Epoch time, when you loaded previous page.
# Compute number of seconds that you sat there before clicking submit.
my $ElapsedTime = time - $PrevTime;
# Update $ClockTime (the time left)
$ClockTime = $ClockTime - $ElapsedTime;

my $ScrambledWord=$DATA[7]; #Only used if they hit refresh.
# These two lines are irrelevant. 
my $RefreshFlag=$DATA[8]; # It is 1, we turn it into a 0.

sub is_word{
    # Input: $text, a string
    # Output: 1 if $text is a word in /usr/dict/words, 0 otherwise.
    my $text = $_[0];    
    open(my $file,  "<",  $words_filename)  or die "Can't open dictionary: $!";
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
    $WinCount++;		#increment wincount
    if ($Mode eq "hard") {
	$ClockTime += 6*(4+$WinCount);
    }				# Add time in hard mode
} elsif (is_anagram($text, $word) && is_word($text)) {
    $WinCount++;		# increment wincount
    if ($Mode eq "hard") {
	$ClockTime += 6*(4+$WinCount);
    }				# Add time in hard mode
} else {
    $LossCount++;
}				#increment losscount

# Update the data file.
open (my $FH, ">", $DataFile);
print $FH $WinCount."\n";
print $FH $LossCount."\n";
print $FH $word."\n";
print $FH $text."\n";
print $FH $Mode."\n";

print $FH $ClockTime."\n";
print $FH time."\n"; # This helps you by a few ms I suppose.

print $FH $ScrambledWord."\n";
print $FH "0\n"; # Resetting the RefreshFlag.
close $FH;

# autosubmits with javascript.
# (May want to just use a redirect. Would look better.)
print $q->header;
print $q->start_html;
print qq( <form action="./scramble_$Mode.cgi" method="post" id="MyForm"> );
print qq( <input type="submit" value="Submit"> );
print <<JS;
<script>
document.getElementById('MyForm').submit();
</script>
JS
print $q->end_html;
