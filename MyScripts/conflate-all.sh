TASK=$1
DIR=$1-Experiments

for trans in MyScripts/Transformations/Transformation-* 
do 
    TARGET=`cat $trans/target.txt`
    echo $TARGET

    mkdir -p $DIR/conflated/$TARGET
    mkdir -p $DIR/conflated/duplicated-$TARGET

    for part in devel test train 
    do
	FILE=$TASK-$part.xml
	python MyScripts/utils.py substituteDependencyTypes --output $DIR/conflated/$TARGET/$FILE --target $TARGET $trans/*.map $DIR/baselines/splitNmod/$FILE
	python MyScripts/utils.py substituteDependencyTypes --output $DIR/conflated/duplicated-$TARGET/$FILE --target $TARGET --keepOriginal $trans/*.map $DIR/baselines/splitNmod/$FILE
    done
    MyScripts/trainModel.sh $TASK $DIR/conflated/$TARGET
    MyScripts/trainModel.sh $TASK $DIR/conflated/duplicated-$TARGET

done
