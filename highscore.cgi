#!/usr/bin/perl
# CGI version of highscore.pl, March 2017
# First draft, we'll try displaying no HTML at all.
# Just redirect to a 'play again' after having processed the high score.

use CGI;
my $q = CGI->new;
my $score = $q->param('WC');
my $mode = $q->param('HSMode');
my $nick = $q->param('User');
$nick = substr($nick, 0, 3);
if (($nick =~ /,/) or ($nick =~ /;/)) {
    $nick = "   ";
}

# @LINES and $filename are global. I rewrite all 3 lines of the text file.

my $filename = "scores.txt";
open (my $FH, '<', $filename)
    or die "Failed: [Does $filename exist?]<br> $!";
chomp(my @LINES = <$FH>);	# SLURP
close $FH;

sub UpdateScores {
    my ($mode, $NewLine) = @_;
    my $OUTPUT;
    if ($mode eq 'easy') {
	$OUTPUT = $NewLine."\n".$LINES[1]."\n".$LINES[2]."\n";
    } elsif ($mode eq 'mod') {
	$OUTPUT = $LINES[0]."\n".$NewLine."\n".$LINES[2]."\n";
    } elsif ($mode eq 'hard') {
	$OUTPUT = $LINES[0]."\n".$LINES[1]."\n".$NewLine."\n";
    }
    # print "scores.txt will now say:<br>";
    # print $OUTPUT, "<br>";
    
    open (my $FILE, '>', $filename);
    print $FILE $OUTPUT;
    close $FILE;
}
sub HighScore {
    my ($mode, $nick, $NewScore) = @_;
    my (@nick, @PrvScore, @name_score_chunk);

    # Get names/scores on the right line.
    if ($mode eq 'easy') {
	@name_score_chunk = split /;/, $LINES[0];
    } elsif ($mode eq 'mod') {
	@name_score_chunk = split /;/, $LINES[1];
    } elsif ($mode eq 'hard') {
	@name_score_chunk = split /;/, $LINES[2];
    }

    # print " These are the current records for $mode mode:\t";
    for my $j (0..$#name_score_chunk) {
	($nick[$j], $PrvScore[$j]) = split(',', $name_score_chunk[$j]);
	# print $nick[$j], ", ", $PrvScore[$j], "; ";
    }
#    print "<br>";

    my $NewLine = $nick.",".$NewScore.";";
    
    if ($NewScore > $PrvScore[0]) {
#	print "\t\t You have beaten an old high score!<br>";
	$NewLine = $NewLine.$name_score_chunk[0].";".$name_score_chunk[1];
	UpdateScores($mode, $NewLine);
    } elsif ($NewScore > $PrvScore[1]) {
#	print "\t\t You have beaten an old high score!<br>";
	$NewLine = $name_score_chunk[0].";".$NewLine.$name_score_chunk[1];
	UpdateScores($mode, $NewLine);
    } elsif ($NewScore > $PrvScore[2]) {
#	print "\t\t You have beaten an old high score!<br>";
	$NewLine = $name_score_chunk[0].";".$name_score_chunk[1].";".$NewLine;
	UpdateScores($mode, $NewLine);
    } else {
#	print "<br>Sorry... that is not a high score.<br>";
    }
}

HighScore(($mode, $nick, $score));


# Now redirect
if ($mode eq 'easy') {
    print $q->redirect('./scramble_basic.cgi');
} elsif ($mode eq 'mod') {
    print $q->redirect('./scramble_moderate.cgi');
} else {
    print $q->redirect('./scramble_hard.cgi');
}
