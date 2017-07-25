while IFS=, read col1
do
	python worker.py $col1 &
    echo "Worker at port $col1 started"
done < workers.csv
