	ping 127.0.0.1 -n 2 > nul
	cls
	type cogs\utils\credit.txt
	echo[
	echo[
	echo Requirements satisfied.
	echo Starting the bot (this may take a minute or two)...
	python loopself.py
	if %ERRORLEVEL% == 15 goto update