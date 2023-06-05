# TFIDF-Hadoop

## Manual:

Phase 1:
-------

    cd PhaseOne
  
  **Local:**
  
    cat ../Data/* | ./MapperPhaseOne.py | sort | ./ReducerPhaseOne.py > OutputPhaseOne.txt

  **Hadoop:**
  
    hadoop jar ~/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.5.jar -input In -output OutPhaseOne -mapper MapperPhaseOne.py -reducer ReducerPhaseOne.py -file MapperPhaseOne.py -file ReducerPhaseOne.py

Phase 2:
-------
    cd ../PhaseTwo
  
  **Local:**
  
     cat ../PhaseOne/OutputPhaseOne.txt | ./MapperPhaseOne.py | sort | ./ReducerPhaseOne.py > OutputPhaseTwo.txt

  **Hadoop:**
  
    hadoop jar ~/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.5.jar -input OutPhaseOne -output OutPhaseTwo -mapper MapperPhaseTwo.py -reducer ReducerPhaseTwo.py -file MapperPhaseTwo.py -file ReducerPhaseTwo.py

Phase 3:
-------

    cd ../PhaseThree
  
  **Local:**
  
    cat ../PhaseTwo/OutputPhaseTwo.txt | ./MapperPhaseThree.py | sort | ./ReducerPhaseThree.py > OutputPhaseThree.txt

  **Hadoop:**
  
    hadoop jar ~/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.5.jar -input OutPhaseTwo -output OutPhaseThree -mapper MapperPhaseThree.py -reducer ReducerPhaseThree.py -file MapperPhaseThree.py -file ReducerPhaseThree.py

Phase 4:
-------

    cd ../PhaseFour
    
  **Local:**
  
    python CalculateSimilarity.py 

  **Hadoop:**
  
    hadoop dfs -copyToLocal OutPhaseThree/part-00000 OutputPhaseThree.txt
    python CalculateSimilarity.py 
