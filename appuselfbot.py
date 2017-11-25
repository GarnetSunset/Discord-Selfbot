    if send_type.startswith('embed'):
        if 'ping' in send_type:
            await request_webhook('/{}/{}'.format(channel, token), embeds=[keyword_content.to_dict()], content=bot.user.mention)
        else:
            await request_webhook('/{}/{}'.format(channel, token), embeds=[keyword_content.to_dict()], content=None)
    else:
        if 'ping' in send_type:
            await request_webhook('/{}/{}'.format(channel, token), content=keyword_content + '\n' + bot.user.mention, embeds=None)
        else:
            await request_webhook('/{}/{}'.format(channel, token), content=keyword_content, embeds=None)

# Set/cycle game
async def game_and_avatar(bot):
    await bot.wait_until_ready()
    current_game = next_game = current_avatar = next_avatar = 0

    while True:
        # Cycles game if game cycling is enabled.
        try:
            if hasattr(bot, 'game_time') and hasattr(bot, 'game'):
                if bot.game:
                    if bot.game_interval:
                        game_check = game_time_check(bot.game_time, bot.game_interval)
                        if game_check:
                            bot.game_time = game_check
                            with open('settings/games.json', encoding="utf8") as g:
                                games = json.load(g)
                            if games['type'] == 'random':
                                while next_game == current_game:
                                    next_game = random.randint(0, len(games['games']) - 1)
                                current_game = next_game
                                bot.game = games['games'][next_game]
                                if bot.is_stream and '=' in games['games'][next_game]:
                                    g, url = games['games'][next_game].split('=')
                                    await bot.change_presence(game=discord.Game(name=g, type=1,
                                                                                url=url),
                                                              status=set_status(bot), afk=True)
                                else:
                                    await bot.change_presence(game=discord.Game(name=games['games'][next_game], type=bot.status_type), status=set_status(bot), afk=True)
                            else:
                                if next_game+1 == len(games['games']):
                                    next_game = 0
                                else:
                                    next_game += 1
                                bot.game = games['games'][next_game]
                                if bot.is_stream and '=' in games['games'][next_game]:
                                    g, url = games['games'][next_game].split('=')
                                    await bot.change_presence(game=discord.Game(name=g, type=1, url=url), status=set_status(bot), afk=True)
                                else:
                                    await bot.change_presence(game=discord.Game(name=games['games'][next_game], type=bot.status_type), status=set_status(bot), afk=True)

                    else:
                        game_check = game_time_check(bot.game_time, 180)
                        if game_check:
                            bot.game_time = game_check
                            with open('settings/games.json', encoding="utf8") as g:
                                games = json.load(g)

                            bot.game = games['games']
                            if bot.is_stream and '=' in games['games']:
                                g, url = games['games'].split('=')
                                await bot.change_presence(game=discord.Game(name=g, type=1, url=url), status=set_status(bot), afk=True)
                            else:
                                await bot.change_presence(game=discord.Game(name=games['games'], type=bot.status_type), status=set_status(bot), afk=True)

            # Cycles avatar if avatar cycling is enabled.
            if hasattr(bot, 'avatar_time') and hasattr(bot, 'avatar'):
                if bot.avatar:
                    if bot.avatar_interval:
                        avi_check = avatar_time_check(bot.avatar_time, bot.avatar_interval)
                        if avi_check:
                            bot.avatar_time = avi_check
                            with open('settings/avatars.json', encoding="utf8") as g:
                                avi_config = json.load(g)
                            all_avis = os.listdir('avatars')
                            all_avis.sort()
                            if avi_config['type'] == 'random':
                                while next_avatar == current_avatar:
                                    next_avatar = random.randint(0, len(all_avis) - 1)
                                current_avatar = next_avatar
                                bot.avatar = all_avis[next_avatar]
                                with open('avatars/%s' % bot.avatar, 'rb') as fp:
                                    await bot.user.edit(password=avi_config['password'], avatar=fp.read())
                            else:
                                if next_avatar + 1 == len(all_avis):
                                    next_avatar = 0
                                else:
                                    next_avatar += 1
                                bot.avatar = all_avis[next_avatar]
                                with open('avatars/%s' % bot.avatar, 'rb') as fp:
                                    await bot.user.edit(password=avi_config['password'], avatar=fp.read())

            # Sets status to default status when user goes offline (client status takes priority when user is online)
            if hasattr(bot, 'refresh_time'):
                refresh_time = has_passed(bot.refresh_time)
                if refresh_time:
                    bot.refresh_time = refresh_time
                    if bot.game and bot.is_stream and '=' in bot.game:
                        g, url = bot.game.split('=')
                        await bot.change_presence(game=discord.Game(name=g, type=1, url=url), status=set_status(bot), afk=True)
                    elif bot.game and not bot.is_stream:
                        await bot.change_presence(game=discord.Game(name=bot.game, type=bot.status_type),
                                                  status=set_status(bot), afk=True)
                    else:
                        await bot.change_presence(status=set_status(bot), afk=True)

            if hasattr(bot, 'gc_time'):
                gc_t = gc_clear(bot.gc_time)
                if gc_t:
                    gc.collect()
                    bot.gc_time = gc_t

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
