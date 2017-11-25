        if kill == 'update':
            exit(15)
        break
    params = [sys.executable, 'appuselfbot.py']
    params.extend(sys.argv[1:])
    subprocess.call(params)
