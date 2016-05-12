PREFIX=$1
LIMIT=$2
FILTER=$3

for dir in $PREFIX-Experiments*/$3*/*/ ;
do
    if [ -e $dir/fold-$LIMIT/docLevelEvaluation.csv ] ;
    then
	fscore=`python MyScripts/bootstrap.py --aggregate $dir/fold-[0-$LIMIT]/docLevelEvaluation.csv fscore --compareTo $PREFIX-Experiments*/baselines/basicUD/fold-[0-$LIMIT]/docLevelEvaluation.csv` ; 
	p=`python MyScripts/bootstrap.py --system $dir/fold-[0-$LIMIT]/docLevelEvaluation.csv --baseline $PREFIX*/baselines/basicUD/fold-[0-$LIMIT]/docLevelEvaluation.csv -i 1000`
	VALUES=""
        for i in $(seq 0 $LIMIT) ;
        do
            diff=`python MyScripts/bootstrap.py --aggregate $dir/fold-$i/docLevelEvaluation.csv fscore --compareTo $PREFIX-Experiments*/baselines/basicUD/fold-[$i]/docLevelEvaluation.csv`
            VALUES=$diff,$VALUES
        done
        VALUES=${VALUES%?}
	stdev=`echo $VALUES | python -c "import numpy, sys ; array = sys.stdin.read() ; array = map(float, array.strip().split(',')) ; print '{:10.3f}'.format(numpy.std(array)), '{:10.3f}'.format(numpy.median(array))"`
	echo "$fscore   $p     $stdev    $dir" ; 
    fi ; 
done # | sort -n