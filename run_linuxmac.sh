				if [ $ret == "15" ]; then
					min_updater
					run_bot
				else
					echo "Shutting down"
				fi

			else
				echo "Requirements installation failed"
				exit 254
			fi
		else
			echo "Using pip as a python3 module"
			echo "Upgrading pip"
			if python -m pip install --user --upgrade pip; then
				echo "Upgrading requirements"
				if python -m pip install --user -r requirements.txt; then
					echo "Starting bot..."
					python loopself.py
					ret=$?
					if [ $ret == "15" ]; then
						min_updater
						run_bot
					else
						echo "Shutting down"
					fi
				else
					echo "Requirements installation failed"
					exit 254
				fi
			else
				echo "Pip could not be installed. Try using your package manager"
				exit 253
			fi
		fi

	else
		echo "You do not appear to have Python 3 installed"
		echo "Python 3 is almost certainly available from your package manager or just google how to get it"
		echo "However if you are, for instance, using Linux from Scratch, you likely do not need instruction"
	fi

}

updater
run_bot
