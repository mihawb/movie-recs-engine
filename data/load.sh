#!/bin/bash

# Skrypt do scalania plików z katalogu i ładowania do Hadoopa

DATA_DIR="plots"
OUT_FILE="plots_output.txt"
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
            echo "$filename: $content" >> "$OUT_FILE"
        fi
    done
}

function public() {
    hdfs dfs -rm -r $HADOOP_DIR
    hdfs dfs -mkdir $HADOOP_DIR
    hdfs dfs -put "$OUT_FILE" $HADOOP_DIR
}

# START
ask "Are you sure you want to merge all the files? [y/n] "
remove_old
merge
ask "Put output on hadoop HDFS? [y/n] "
public
echo "Done - Output in directory [$HADOOP_DIR] on hadoop HDFS"