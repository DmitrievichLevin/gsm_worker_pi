#!/bin/sh
#get latest version
version=`curl http://chromedriver.storage.googleapis.com/LATEST_RELEASE)`;
echo 'Currently LATEST_RELEASE:' $version;
#download the latest version chrome driver available as per the above line
wget -N http://chromedriver.storage.googleapis.com/${version}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip -d /usr/local/bin
chmod a+x /usr/local/bin/chromedriver
#install latest google chrome
yum install https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
google_version=`google-chrome --version`;
echo 'Google Chrome Version:' $google_version;
echo 'End of the script'