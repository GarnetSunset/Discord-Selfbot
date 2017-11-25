        break
    params = [sys.executable, 'appuselfbot.py']
    params.extend(sys.argv[1:])
    subprocess.call(params)
