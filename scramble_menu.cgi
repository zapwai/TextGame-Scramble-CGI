#!/usr/bin/perl
use CGI;

my $q = CGI->new;
my $ChosenOption = $q->param('option');

my $RedirectTarget = "http://zapwai.net";
if ($ChosenOption eq "Basic") {$RedirectTarget="./scramble_basic.cgi"}
elsif ($ChosenOption eq "Moderate") {$RedirectTarget="./scramble_moderate.cgi"}
elsif ($ChosenOption eq "Hard") {$RedirectTarget="./scramble_hard.cgi"}

print $q->redirect($RedirectTarget);
