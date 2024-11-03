#!/bin/sh
#download the latest version chrome driver available as per the above line
wget -N http://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip
unzip chromedriver_linux64.zip -d .local/bin
chmod a+x .local/bin/chromedriver