	echo Latest update:
	git --no-pager log --pretty=oneline -n1 origin/master ^master
	git pull origin master
	if errorlevel 1 goto force
	echo Finished updating
	echo Starting up...
	goto run
:force
	git fetch --all
	git reset --hard origin/master
	echo Finished updating
	echo Starting up...
	goto run
:git
	TITLE Error!
	echo Git not found, Download here: https://git-scm.com/downloads
	echo Press any key to exit.
	pause >nul
	CD /D "%root%"
	goto :EOF
:python
	TITLE Error!
	echo Python not added to PATH or not installed. Download Python 3.5.2 or above and make sure you add to PATH: https://i.imgur.com/KXgMcOK.png
	echo Press any key to exit.
	pause >nul
	CD /D "%root%"
	goto :EOF
:run
	if exist tmp.txt del tmp.txt
	FOR /f %%p in ('where python') do SET PYTHONPATH=%%p
	echo Checking/Installing requirements (takes some time on first install)...
	chcp 65001 >nul
	set PYTHONIOENCODING=utf-8
	python -m pip install --user --upgrade pip >nul
	python -m pip install --user -r requirements.txt
	if errorlevel 1 (
	    echo Requirements installation failed. Perhaps some dependency is missing or access was denied? Possible solutions:
	    echo - Run as administrator
	    echo - Google the error
	    echo - Visit the Discord server for help
	    echo Press any key to exit.
	    set /p input=
	    exit
	)
	ping 127.0.0.1 -n 2 > nul
	cls
	type cogs\utils\credit.txt
	echo[
	echo[
	echo Requirements satisfied.
	echo Starting the bot (this may take a minute or two)...
	python loopself.py
	if %ERRORLEVEL% == 15 goto update