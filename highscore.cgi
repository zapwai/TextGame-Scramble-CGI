#!/usr/bin/perl
# CGI version of highscore.pl, March 2017
# May 2017, the HTML highscores update. We change scramble.html itself.

# Moderate mode fucks up my high scores!!

use CGI;

my $q = CGI->new;
my $filenum = $q->param('UID');
my $DataFile = "_$filenum.txt";
open (my $FH, "<", $DataFile);
my @DATA = <$FH>;
close $FH;
chomp ( @DATA );

my $score = $DATA[0];
my $mode = $DATA[4];
my $nick = $q->param('User');
$nick = substr($nick, 0, 3);

if (($nick =~ /,/) or ($nick =~ /;/)) {
    $nick = "   ";
}
# Correct the length. Formatting looks nicer with 3 characters.
if ( length $nick == 2) {
    $nick = $nick." ";
} elsif ( length $nick == 1 ) {
    $nick = $nick."  ";
} elsif ( length $nick == 0 ) {
    $nick = $nick."   ";
}

# @LINES and $filename are global. I rewrite all 3 lines of the text file.
# It works better if we just update scramble.html,
# but keep a copy of scores.txt for simplicity.
my $filename = "scores.txt";
my $htmltemplatename = "scramble_template.html";
my $htmlname = "scramble.html";
my $indexname = "index.html";
open (my $FH, '<', $filename)
    or die "Failed: [Does $filename exist?]<br> $!";
chomp(my @LINES = <$FH>);
close $FH;

sub PrintHTML{
    my $ReturnLine = shift;
    # For formatting purposes on the scramble.html page.
    # Replace each space with &nbsp.
    $ReturnLine =~ s/\s/&nbsp/g;
    open (my $html_target, ">", $htmlname);
    open (my $htmlblank, "<", $htmltemplatename);
    my @PAGE = <$htmlblank>;
    close $htmlblank;
    my $html_print_output;
    for my $k (0 .. $#PAGE) {
	if ($k == 44) {		# Line 45 is the one to edit.
	    $html_print_output = $html_print_output.$ReturnLine."\n";
	} else {
	    $html_print_output = $html_print_output.$PAGE[$k];
	}
    }
    print $html_target $html_print_output;
    close $html_target;
    open (my $index_target, ">", $indexname); # (copy to index.html)
    print $index_target $html_print_output;
    close $index_target;
}

sub UpdateTextScores {
    my ($mode, $NewLine) = @_;
    my $OUTPUT;
    if ($mode eq 'basic') {
	$OUTPUT = $NewLine."\n".$LINES[1]."\n".$LINES[2]."\n";
    } elsif ($mode eq 'moderate') {
	$OUTPUT = $LINES[0]."\n".$NewLine."\n".$LINES[2]."\n";
    } elsif ($mode eq 'hard') {
	$OUTPUT = $LINES[0]."\n".$LINES[1]."\n".$NewLine."\n";
    }  
    open (my $FILE, '>', $filename);
    print $FILE $OUTPUT;
    close $FILE;
}

sub UpdateScores {
    my ($mode, $NewLine) = @_;
    my $OUTPUT;
    if ($mode eq 'basic') {
	$OUTPUT = $NewLine."<br>".$LINES[1]."<br>".$LINES[2]."<br>";
    } elsif ($mode eq 'moderate') {
	$OUTPUT = $LINES[0]."<br>".$NewLine."<br>".$LINES[2]."<br>";
    } elsif ($mode eq 'hard') {
	$OUTPUT = $LINES[0]."<br>".$LINES[1]."<br>".$NewLine."<br>";
    }
    # Down here, so we don't update twice.
    UpdateTextScores($mode, $NewLine); 
    return $OUTPUT;
}

sub HighScore {
    my ($mode, $nick, $NewScore) = @_;
    my (@nick, @PrvScore, @name_score_chunk);

    # Get names/scores on the right line.
    if ($mode eq 'basic') {
	@name_score_chunk = split /;/, $LINES[0];
    } elsif ($mode eq 'moderate') {
	@name_score_chunk = split /;/, $LINES[1];
    } elsif ($mode eq 'hard') {
	@name_score_chunk = split /;/, $LINES[2];
    }
    for my $j (0..$#name_score_chunk) {
	($nick[$j], $PrvScore[$j]) = split(',', $name_score_chunk[$j]);
    }

    my $NewLine = $nick.",".$NewScore.";";
    my $ReturnLine;
    
    if ($NewScore > $PrvScore[0]) {
	$NewLine = $NewLine.$name_score_chunk[0].";".$name_score_chunk[1];
	$ReturnLine = UpdateScores($mode, $NewLine);
    } elsif ($NewScore > $PrvScore[1]) {
	$NewLine = $name_score_chunk[0].";".$NewLine.$name_score_chunk[1];
	$ReturnLine = UpdateScores($mode, $NewLine);
    } elsif ($NewScore > $PrvScore[2]) {
	$NewLine = $name_score_chunk[0].";".$name_score_chunk[1].";".$NewLine;
	$ReturnLine = UpdateScores($mode, $NewLine);
    } else {			# do nothing.
	return;
    }

    # open scramble.html for writing the high scores.
    PrintHTML($ReturnLine);
}

HighScore(($mode, $nick, $score));
unlink $DataFile;
print $q->redirect("./scramble.html");
