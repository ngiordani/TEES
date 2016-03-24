REP_NAME=$1
DIRECTORY=$2

for file in $DIRECTORY/*
do
    java -cp ~/scr/working-dirs/DependencyTransformer/DependencyTransformer/classes converters.MakeUDAlternativesWithHandler $REP_NAME $file
    mv $file.$REP_NAME $file
done

rm $DIRECTORY/*.$REP_NAME.revert
