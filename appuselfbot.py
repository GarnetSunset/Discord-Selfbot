        except Exception as e:
            print('Something went wrong: %s' % e)

        await asyncio.sleep(5)

if __name__ == '__main__':
    err = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    if not os.path.exists("custom_cogs"):
        try:
            os.makedirs("custom_cogs")
            text = "Hello! Seems like you ran into this folder and don't know what this is for. This folder is meant to hold various custom cogs you can download.\n\n" \
                   "Custom cogs are additional add-ons you can download for the bot which will usually come with additional features and commands.\n\n" \
                   "For more info on what they are, how they can be accessed and downloaded, and how you can make one too, go here: https://github.com/appu1232/Discord-Selfbot/wiki/Other-Add-ons"
            with open("custom_cogs/what_is_this.txt", 'w') as fp:
                fp.write(text)
            site = requests.get('https://github.com/LyricLy/ASCII/tree/master/cogs').text
            soup = BeautifulSoup(site, "html.parser")
            data = soup.find_all(attrs={"class": "js-navigation-open"})
            list = []
            for a in data:
                list.append(a.get("title"))
            for cog in list[2:]:
                for entry in list[2:]:
                    response = requests.get("http://appucogs.tk/cogs/{}".format(entry))
                    found_cog = response.json()
                    filename = found_cog["link"].rsplit("/", 1)[1].rsplit(".", 1)[0]
                    if os.path.isfile("cogs/" + filename + ".py"):
                        os.rename("cogs/" + filename + ".py", "custom_cogs/" + filename + ".py")
        except Exception as e:
            print("Failed to transfer custom cogs to custom_cogs folder. Error: %s" % str(e))
    for extension in os.listdir("cogs"):
        if extension.endswith('.py'):
            try:
                bot.load_extension("cogs." + extension[:-3])
            except Exception as e:
                print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
    for extension in os.listdir("custom_cogs"):
        if extension.endswith('.py'):
            try:
                bot.load_extension("custom_cogs." + extension[:-3])
            except Exception as e:
                print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    sys.stderr = err
    bot.loop.create_task(game_and_avatar(bot))

    while True:
        if heroku:
            token = os.environ['TOKEN']
        else:
            token = get_config_value('config', 'token')
        try:
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
