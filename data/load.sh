#!/bin/bash

# Skrypt do scalania plików z katalogu i ładowania do Hadoopa

DATA_DIR="plots"
OUT_FILE="PLOTS_DATA.txt"
EXTENSION=".txt"
HADOOP_DIR="plots"

function ask () {

	while true; do
    	read -p "$1" yn
    	case $yn in
        	[Yy]* ) 
				ANSWER=1
				break
				;;
        	[Nn]* ) 
				ANSWER=0
				break
				;;
        	* ) echo "Use y or n.";;
    	esac
	done

    if [ $ANSWER -eq 0 ]; then exit; fi
}

function remove_old() {
    # Delete output file if exists
    if [[ -f "$OUT_FILE" ]]; then
        rm "$OUT_FILE"
    fi
}

function merge() {
    for file in "$DATA_DIR"/*"$EXTENSION"; do
        echo "Processed file [$file]"
        if [[ -f "$file" ]]; then
            filename=$(basename "$file" "$EXTENSION")
            content=$(cat $file | dos2unix | tr -d '\n')
            content=$(clear_text "$content")
            echo "$filename $content" >> "$OUT_FILE"
        fi
    done
}

function public() {
    hdfs dfs -rm -r $HADOOP_DIR
    hdfs dfs -mkdir $HADOOP_DIR
    hdfs dfs -put "$OUT_FILE" $HADOOP_DIR
}

function clear_text() {
    local input=$1

    # Remove punctuation marks
    input=$(echo "$input" | tr -d '[:punct:]')

    # Upper case -> Lower case
    input=$(echo "$input" | tr '[:upper:]' '[:lower:]')

    # Remove numbers
    input=$(echo "$input" | sed 's/[0-9]//g')

    # Remove popular stop words
    local stopwords=("a" "an" "and" "are" "as" "at" "be" "by" "for" "from" "has" "he" "in" "is" "it" "its" "of" "on" "that" "the" "to" "was" "were" "will" "with")
    for word in "${stopwords[@]}"; do
        input=$(echo "$input" | sed "s/\\b${word}\\b//g")
    done

    # One space between words
    input=$(echo "$input" | tr -s ' ')

    # Trim
    input=$(echo "$input" | xargs)

    echo "$input"
}

# START
ask "Are you sure you want to merge all the files? [y/n] "
remove_old
merge
ask "Put output on hadoop HDFS? [y/n] "
public
echo "Done - Output in directory [$HADOOP_DIR] on hadoop HDFS"