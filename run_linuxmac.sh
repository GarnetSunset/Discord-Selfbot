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
