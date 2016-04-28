DIRECTORY=$1
CONVERTER=$2

for file in $DIRECTORY/*
do
    java -cp ~/scr/working-dirs/DependencyTransformer/DependencyTransformer/classes converters.$CONVERTER "$file"
#    java -cp ~/scr/working-dirs/DependencyTransformer/DependencyTransformer/classes converters.SplitSubjects "$file"
#    java -cp ~/scr/working-dirs/DependencyTransformer/DependencyTransformer/classes converters.SplitComplements "$file"
#    java -cp ~/scr/working-dirs/DependencyTransformer/DependencyTransformer/classes converters.SplitXcomp "$file"
#    java -cp ~/scr/working-dirs/DependencyTransformer/DependencyTransformer/classes converters.SplitSubjectsWithXcomp "$file"
    mv "$file".* "$file"
done
