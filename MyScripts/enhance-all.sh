TASK=$1
DIR=$1-Experiments
BASELINE=$2

for ENHANCEMENT in IntroduceXADVCL #SplitSubjects SplitComplements SplitXcomp SplitSubjectsWithXcomp AnnotateNegation IntroduceXADVCL
do
    mkdir -p $DIR/enhancements/$ENHANCEMENT

    for part in devel test train 
    do
	FILE=$TASK-$part.xml
	MyScripts/convertParses.sh $BASELINE/$FILE $DIR/enhancements/$ENHANCEMENT/$FILE $ENHANCEMENT 
    done

    MyScripts/trainModel.sh $TASK $DIR/enhancements/$ENHANCEMENT
done
