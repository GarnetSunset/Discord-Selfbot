            bot.run(token, bot=False)
        except discord.errors.LoginFailure:
            if not heroku:
                if _silent:
                    print('Cannot use setup Wizard becaue of silent mode')
                    exit(0)
                print("It seems the token you entered is incorrect or has changed. If you changed your password or enabled/disabled 2fa, your token will change. Grab your new token. Here's how you do it:\n")
                print("Go into your Discord window and press Ctrl+Shift+I (Ctrl+Opt+I can also work on macOS)")
                print("Then, go into the Applications tab (you may have to click the arrow at the top right to get there), expand the 'Local Storage' dropdown, select discordapp, and then grab the token value at the bottom. Here's how it looks: https://imgur.com/h3g9uf6")
                print("Paste the contents of that entry below.")
                print("-------------------------------------------------------------")
                token = input("| ").strip('"')
                with open("settings/config.json", "r+", encoding="utf8") as fp:
                    config = json.load(fp)
                    config["token"] = token
                    fp.seek(0)
                    fp.truncate()
                    json.dump(config, fp, indent=4)
                continue
        break
