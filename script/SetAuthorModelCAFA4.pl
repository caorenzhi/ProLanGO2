#
# By Prof. Cao at Pacific Lutheran University
# Email: caora@plu.edu

use FileHandle;

if(@ARGV<2)
{ 
    print "this script is going to set the author and model information. Try: \nperl $0 dir_predictions CaoLab1 1 dir_output [optional, a number to keep at most this number of predictions]\n";
#    print "\nperl $0 ../result/predictions_random_1000_Lan2fun_model3_v2 CaoLab1 3 ../test/Caolab1_model3\n";
#    print "\nperl $0 ../result/predictions_random_1000_Lan2fun_model3_v2 CaoLab1 3 ../test/Caolab1_model3_100 100\n";
   print "perl $0 ../result/CAFA4_prediction_temp1/Predictions CaoLab1 3 ../test/CaoLab1_model3_100 100\n";
   die;
}

$dir_input = $ARGV[0];
$author = $ARGV[1];
$model = $ARGV[2];
$dir_out = $ARGV[3];
-s $dir_out || system("mkdir $dir_out");

if(@ARGV>4)
{
   $limit = $ARGV[4];
}

opendir(DIR,$dir_input);
@files = readdir(DIR);
foreach $file (@files)
{
   if ($file eq "." || $file eq "..")
   {next;}
   $path_in = $dir_input."/".$file;
   $newName = processName($file);
   $path_out = $dir_out."/".$newName;
   process($path_in,$path_out);
}

$zip = $dir_out.".zip";
system("zip -r $zip $dir_out");

sub processName($)
{
   ($orig) = @_;
   #@tem = split(/\_/,$orig);
   @tem = split(/\./,$orig);
   if(@tem<3)
   {
       print($orig);
       die "Error, check file $orig, should have author name, model id, and taxid!\n";}
   #$result = $author."_".$model."_".$tem[2];
   $result = $author."_".$model."_".$tem[1]."_go.txt";
   return $result;
}


sub process($$)
{
  ($input,$out) = @_;
  %hash = ();
  $IN = new FileHandle "$input";

  $OUT= new FileHandle ">$out";
## we will print header information first, because this is for CAFA 4, my script will not generate the header information.
print $OUT "AUTHOR\t".$author."\n";
print $OUT "MODEL\t".$model."\n";
print $OUT "KEYWORDS\t"." de novo prediction, machine learning, natural language processing."."\n";

  while(defined($line=<$IN>))
  {
     chomp($line);
     @tem = split(/\s+/,$line);
     if($tem[0] eq "AUTHOR")
     {
die "This is not expected, please check your prediction file and code here\n";
        print $OUT "AUTHOR\t".$author."\n";
     }
     elsif($tem[0] eq "MODEL")
     {
        print $OUT "MODEL\t".$model."\n";
     }
     elsif($tem[0] eq "KEYWORDS" || $tem[0] eq "END")
     {
        print $OUT $line."\n";
     }
     else
     {

        if(@ARGV>4)
        {
          print "Model skip $ARGV[4]!\n";
          if(not exists $hash{$tem[0]}) {$hash{$tem[0]} = 1;}
          else {$hash{$tem[0]}++;}
          if($hash{$tem[0]} > $limit) {print "skip $tem[0]\n";next;}    # skip if you already make enough predictions for this model
        }
        
        @tem2 = split(/\s+/,$line);
        print $OUT $tem2[0]."\t".$tem2[1]."\t".sprintf("%.2f",$tem2[2])."\n";        
        #print $OUT $line."\n";
        
     }
  }
  print $OUT "END\n";
  $OUT->close();
  $IN->close();
}
