#!/bin/bash

cd ${0%/*}

startfail=0

if [ -z "$(python -V 2>/dev/null | grep 'Python 3')" ]; then
	echo "Python version >= 3.5 is required !"
	exit
fi

if [ ! -f ./venv/bin/python ]; then

	if [ -z "$(virtualenv --version 2>/dev/null)" ]; then
		echo "Installing virtualenv with pip"
		pip install virtualenv
	fi

	echo "Setting up a linux virtual environnement"
	virtualenv ./venv

	echo "Installing dependencies..."
	./venv/bin/pip install websocket-server
fi

if [ ! -d ./settings/ ]; then
	echo "Creating a settings directory"
	mkdir ./settings
fi

if [ ! -f ./settings/game_settings.py ]; then
	echo "File $PWD/settings/game_settings.py not found, downloading a template from github..."
	wget https://raw.githubusercontent.com/Julien00859/Bomberman/master/settings/game_settings.py ./settings/
	echo "Please check the file before restarting this script"

	startfail=1
fi

if [ ! -f ./settings/server_settings.py ]; then
	echo "File $PWD/settings/server_settings.py not found, downloading a template from github..."
	wget https://raw.githubusercontent.com/Julien00859/Bomberman/master/settings/server_settings.py ./settings/
	echo "Please check the file before restarting this script"
	startfail=1
fi

if [ $startfail -eq 1 ]; then
	echo "Server startup aborded, see reason(s) above"
	exit
fi

echo "Starting server. CTRL+C to quit."
./venv/bin/python start.py

