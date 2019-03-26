## script for post processing PAT data in batch
## ${Base_dir} contains all the PAT source data that needs to be processed, change this dir to your own
Base_dir=/home/test1

################################################################################
## DO NOT NEED TO EDIT BELOW PARTS!!!
################################################################################
PAT_POST_HOME=$( cd $( dirname ${BASH_SOURCE[0]} ) && pwd )

Original_name="PAT-Result"
for item in `ls ${Base_dir}`
do
	echo "Processing ${item}..."
	New_name=${item}
	New_dir=${Base_dir}/${item}/instruments/
	sed -i "s/${Original_name}/${New_name}/g" ${PAT_POST_HOME}/pat-post-process.py
	sed -i "s|<source>.*</source>|<source>${New_dir}</source>|g" ${PAT_POST_HOME}/config.xml
	${PAT_POST_HOME}/pat-post-process.py
	echo "${item} done!"
	Original_name=${New_name}
done
## change back to original value
sed -i "s/${Original_name}/PAT-Result/g" ${PAT_POST_HOME}/pat-post-process.py
sed -i "s|<source>.*</source>|<source>/foo/bar/instruments/</source>|g" ${PAT_POST_HOME}/config.xml



