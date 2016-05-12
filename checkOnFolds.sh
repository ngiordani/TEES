for dir in GE09-Experiments_done/*/*/fold-0 ;
do 
    dir=${dir%/*} ; 
    if [ ! -e $dir/fold-9/docLevelEvaluation.csv ] ; 
    then
	echo $dir ; 
	for i in {0..9} ; 
	do
	    if [ ! -d $dir/fold-$i/classification-devel ] ;
	    then
		if [ ! -e $dir/fold-$i/log.txt ] ;
		then
		    echo "Currently building data set for fold $i. No log."
		    break;
		fi;
		MOD=`ls -la $dir/fold-$i/log.txt | grep -o "[0-9][0-9]:[0-9][0-9]"` ;
		if
		    grep -q Traceback $dir/fold-$i/log.txt ;
		then
		    echo "!!! Crashed on fold $i. Last write at $MOD. There are errors in this log." ;
		    break ;
		else
		    TIME=`head $dir/fold-$i/log.txt | grep -oP "(?<=Opening log log.txt at ).*2016"` ;
		    echo "Currently processing fold $i, started on $TIME, last write at $MOD" ;
		    break ;
		fi ;		
	    fi  ;
	done;
	echo "" ; 
    fi;
done
