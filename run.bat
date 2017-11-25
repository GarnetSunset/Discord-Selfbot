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