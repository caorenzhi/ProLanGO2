use FileHandle;

######
# Author: Prof. Renzhi Cao
# on 1/1/2020
#####

if(@ARGV<3)
{
   die "Processing sequence into protein language based on fragment database! Three parameters are needed, the k-mers database, the fasta file or folder contains fasta files, output folder.\nperl $0 ../database/FragDATABASE.txt ../data/TargetFiles/ ../result/CAFA_folder_for_prediction\nperl $0 ../database/New_Balanced_FragDATABASE_34567_top2000.txt ../data/TargetFiles/ ../result/CAFA4_folder_for_prediction\nperl $0 ../database/New_Balanced_FragDATABASE_34567_top2000.txt ../../SelectCAFA3Targets/result/Select2000Targets/ ../data/CAFA3_sample";
}


$fragDATA = $ARGV[0];
$funDATA = $ARGV[1];
$dir_output = $ARGV[2];

-s $dir_output || system("mkdir $dir_output");

if(-f $funDATA)
{# this is a fasta file!
   $tmp_targets = $dir_output."/tmpInput";
   system("mkdir $tmp_targets");
   system("cp ".$funDATA." ".$tmp_targets);
   $funDATA = $tmp_targets;
}

$IN = new FileHandle "$fragDATA";
%hash3 = ();     # for fragment 3
%hash4 = ();
%hash5 = ();
%hash6 = ();
%hash7 = ();

%hashALL = ();
while(defined($line=<$IN>))
{
  chomp($line);
  if($line eq "") {next;}
  $hashALL{$line} = 1;
  if(length($line) == 3)
  {
     $hash3{$line} = 1;
  }
  elsif(length($line) == 4)
  {  $hash4{$line} = 1;}
  elsif (length($line) == 5)
  {  $hash5{$line} = 1;}
  elsif (length($line) == 6)
  {  $hash6{$line} = 1;}
  elsif (length($line) == 7)
  {  $hash7{$line} = 1;}
  else {die "check $line\n";}
}
$IN->close();

opendir(DIR,$funDATA);
@files = readdir(DIR);
foreach $file (@files)
{
  if($file eq "." || $file eq "..")
  {
    next;
  }
  $inputfile = $funDATA."/".$file;
  $outputfile1 = $dir_output."/".$file.".ProlanguageGO";
  $outputfile2 = $dir_output."/".$file.".filteredProlanguageGO";
  processfasta($inputfile,$outputfile1);
  filterfasta($outputfile1,$outputfile2);
  unlink($outputfile1); 
}

sub filterfasta($$)
{
  my($inputfile,$outputfile) = @_;
  $IN = new FileHandle "$inputfile";
  $OUT = new FileHandle ">$outputfile";
  while(defined($line=<$IN>))
  {
     chomp($line);
     @tem = split(/\|/,$line);
     $ID = $tem[1];
     @tem2 = split(/\s+/,$tem[0]);
     $result = "NULL";
     for($i=0; $i<scalar(@tem2); $i++)
     {
        if(exists $hashALL{$tem2[$i]})
        {
           if($result eq "NULL")
           {
              $result = $tem2[$i];
           }
           else
           {
              $result = $result." ".$tem2[$i];
           }

        }
     }
     if($result ne "NULL")
     {
        print $OUT $result."|".$ID."\n";
     }
   }


  $OUT->close();
  $IN->close();
}

sub processfasta($$)
{
  my($inputfile,$outputfile1) = @_;
  $IN = new FileHandle "$inputfile";
  $OUT1 = new FileHandle ">$outputfile1";
  $current_sequence="NULL";
  $ID = "NULL";
  while(defined($line=<$IN>))
  {
     chomp($line);
     if(substr($line,0,1) eq ">")
     {# this is the id, need to save and print out
        @tem = split(/\s+/,$line);
        if($ID ne "NULL")
        {
           print $OUT1 process($current_sequence)."|".$ID."\n";
        }
        $ID = $tem[0];
        $current_sequence="NULL";
     }
     else
     {
       if($current_sequence eq "NULL")
       {
         $current_sequence = $line;
       }
       else
       {
         $current_sequence.=$line;
       }
     }
  }
  if($ID ne "NULL")
  {
    print $OUT1 process($current_sequence)."|".$ID."\n";   # print out the last sequence or ID
  }

  $OUT1->close();
  $IN->close();
}




sub process($)
{
  my($sequence) = @_;
  my(%hash_frag) = ();     # for fragment status
  ## first check fragment with length 7
  for($i = 0; $i<=length($sequence)-7; $i++)
  {
     if(exists $hash7{substr($sequence,$i,7)})
     {
        for($j=$i;$j<$i+7;$j++)
        {
            $hash_frag{$j} = 7;
        }
        $i+=6;
     }
  }
  ## now check fragment with length 6
  for($i = 0; $i<=length($sequence)-6; $i++)
  {
     for($j=$i;$j<$i+6;$j++)
     {
         if(exists $hash_frag{$j})
         {
            last;
         }
     }
     if($j<$i+6) {$i=$j+1;next;}   # we already process this fragment before
     if(exists $hash6{substr($sequence,$i,6)})
     {
        for($j = $i;$j<$i+6;$j++)
        {
            $hash_frag{$j} = 6;
        }
     }
  }
  ## now check fragment with length 5
  for($i = 0; $i<=length($sequence)-5; $i++)
  {
     for($j=$i;$j<$i+5;$j++)
     {
         if(exists $hash_frag{$j})
         {
            last;
         }
     }
     if($j<$i+5) {$i=$j+1;next;}   # we already process this fragment before
     if(exists $hash5{substr($sequence,$i,5)})
     {
        for($j = $i;$j<$i+5;$j++)
        {
            $hash_frag{$j} = 5;
        }
     }
  }
  ## now check fragment with length 4
  for($i = 0; $i<=length($sequence)-4; $i++)
  {
     for($j=$i;$j<$i+4;$j++)
     {
         if(exists $hash_frag{$j})
         {
            last;
         }
     }
     if($j<$i+4) {$i=$j+1;next;}   # we already process this fragment before
     if(exists $hash4{substr($sequence,$i,4)})
     {
        for($j = $i;$j<$i+4;$j++)
        {
            $hash_frag{$j} = 4;
        }
     }
  }
  ## now check fragment with length 3
  for($i = 0; $i<=length($sequence)-3; $i++)
  {
     for($j=$i;$j<$i+3;$j++)
     {
         if(exists $hash_frag{$j})
         {last;}
     }
     if($j<$i+3) {$i=$j+1;next;}   # we already process this fragment before
     if(exists $hash3{substr($sequence,$i,3)})
     {
         for($j = $i;$j<$i+3;$j++)
         {
             $hash_frag{$j} = 3;
         }
     }
  }
  $f_tag = -1;
  $result = "null";
  for($i=0;$i<length($sequence); $i++)
  {
    if(not exists $hash_frag{$i}) {$hash_frag{$i}=0;}
    if($result eq "null")
    {
       $f_tag = $hash_frag{$i};
       if($f_tag == 3) {$result=substr($sequence,$i,3);$i+=2;}
       if($f_tag == 4) {$result=substr($sequence,$i,4);$i+=3;}
       if($f_tag == 5) {$result=substr($sequence,$i,5);$i+=4;}
       if($f_tag == 6) {$result=substr($sequence,$i,6);$i+=5;}
       if($f_tag == 0) {$result = substr($sequence,$i,1);}
    }
    else
    {
       if($f_tag == 0 && $hash_frag{$i} == 0)
       {
          $result.=substr($sequence,$i,1);
       }
       else
       {
          $result.=" ";
          $current_tag = $hash_frag{$i};
          if($current_tag == 3) {$result.=substr($sequence,$i,3);$i+=2;}
          if($current_tag == 4) {$result.=substr($sequence,$i,4);$i+=3;}
          if($current_tag == 5) {$result.=substr($sequence,$i,5);$i+=4;}
          if($current_tag == 6) {$result.=substr($sequence,$i,6);$i+=5;}
          if($current_tag == 0) {$result.=substr($sequence,$i,1);}
          $f_tag = $current_tag;
       }
    }
  }

  return $result;
}
