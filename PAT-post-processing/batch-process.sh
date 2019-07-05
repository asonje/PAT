## script for post processing PAT data in batch
## ${Base_dir} contains all the PAT source data that needs to be processed, change this dir to your own
Base_dir=/home/test1

################################################################################
## DO NOT NEED TO EDIT BELOW PARTS!!!
################################################################################
PAT_POST_HOME=$( cd $( dirname ${BASH_SOURCE[0]} ) && pwd )

cd ${Base_dir}
for item in `ls -d */` ## only dirs under ${Base_dir}
do
	echo "Processing ${item} ..."
	New_dir=${Base_dir}/${item}/instruments
	if [ -d ${New_dir} ]; then
		sed -i "s|<source>.*</source>|<source>${New_dir}</source>|g" ${PAT_POST_HOME}/config.xml
		${PAT_POST_HOME}/pat-post-process.py ${PAT_POST_HOME}/config.xml
		echo "${item} done!"
	else
		echo "WARNING: ${item} is not a PAT file, will ignore!"
	fi
done
## change back to original value
sed -i "s|<source>.*</source>|<source>/foo/bar/instruments/</source>|g" ${PAT_POST_HOME}/config.xml
cd -



