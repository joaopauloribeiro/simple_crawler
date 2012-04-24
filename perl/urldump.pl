#!/usr/bin/perl
use Data::Dumper;

$file = open(INFILE, "index.html");
$data = "";
while (<INFILE>) {
  $data .= $_;
}
close(INFILE);

%links = ();
while ($data =~ /<a.*?href=['"](.*?)['"].*?>(.*?)<\/a>/ig) {
  $link = $1;
  $name = $2;
  $name =~ s/(<.*?>)//g;
  $links{$link} = $name;
}
print(keys(%links) . " links\n");
print Dumper(\%links);
