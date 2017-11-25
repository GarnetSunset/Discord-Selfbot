        await ctx.send(bot.bot_prefix + 'Reloaded {} of {} modules.'.format(l, len(utils)))


# On all messages sent (for quick commands, custom commands, and logging messages)
@bot.event
async def on_message(message):

    if hasattr(bot, 'message_count'):
        bot.message_count += 1

    # If the message was sent by me
    if message.author.id == bot.user.id:
        if hasattr(bot, 'icount'):
            bot.icount += 1
        try:
            if hasattr(bot, 'ignored_servers'):
                if any(str(message.guild.id) == str(guild_id) for guild_id in bot.ignored_servers['servers']):
                    return
        except AttributeError:  # Happens when it's a direct message.
            pass
        if hasattr(bot, 'self_log'):
            try:
                if str(message.channel.id) not in bot.self_log:
                    bot.self_log[str(message.channel.id)] = collections.deque(maxlen=100)
            except AttributeError:
                return
            bot.self_log[str(message.channel.id)].append(message)
            if message.content.startswith(bot.customcmd_prefix):
                response = custom(message.content.lower().strip())
                if response:
                    await message.delete()
                    if get_config_value('optional_config', 'rich_embed') == 'on':
                        if response[0] == 'embed' and embed_perms(message):
                            try:
                                if get_config_value('optional_config', 'customcmd_color'):
                                    color = int('0x' + get_config_value('optional_config', 'customcmd_color'), 16)
                                    await message.channel.send(content=None, embed=discord.Embed(colour=color).set_image(url=response[1]))
                                else:
                                    await message.channel.send(content=None, embed=discord.Embed().set_image(url=response[1]))
                            except:
                                await message.channel.send(response[1])
                        else:
                            await message.channel.send(response[1])
                    else:
                        await message.channel.send(response[1])
            else:
                response = quickcmds(message.content.lower().strip())
                if response:
                    await message.delete()
                    await message.channel.send(response)

    notified = message.mentions
    if notified:
        for i in notified:
            if i.id == bot.user.id:
                bot.mention_count += 1

    if not hasattr(bot, 'log_conf'):
        bot.log_conf = load_log_config()

    # Keyword logging.
    if bot.log_conf['keyword_logging'] == 'on' and isinstance(message.channel, discord.abc.GuildChannel):

        try:
            word_found = False
            if (bot.log_conf['allservers'] == 'True' or str(message.guild.id) in bot.log_conf['servers']) and (str(message.guild.id) not in bot.log_conf['blacklisted_servers'] and str(message.channel.id) not in bot.log_conf['blacklisted_channels']):
                add_alllog(str(message.channel.id), str(message.guild.id), message)
                if message.author.id != bot.user.id and (not message.author.bot and not any(x in str(message.author.id) for x in bot.log_conf['blacklisted_users'])) and message.author not in bot.user.blocked:
                    for word in bot.log_conf['keywords']:
                        if ' [server]' in word:
                            word, guild = word.split(' [server]')
                            if str(message.guild.id) != guild:
                                continue
                        elif ' [channel]' in word:
                            word, channel = word.split(' [channel]')
                            if str(message.channel.id) != channel:
                                continue
                        if word.startswith('[isolated]'):
                            word = word[10:].lower()
                            found = re.findall('\\b' + word + '\\b', message.content.lower())
                            if found:
                                word_found = True
                                break
                        else:
                            if word.lower() in message.content.lower():
                                word_found = True
                                break

                    for x in bot.log_conf['blacklisted_words']:
                        if '[server]' in x:
                            bword, id = x.split('[server]')
                            if bword.strip().lower() in message.content.lower() and str(message.guild.id) == id:
                                word_found = False
                                break
                        elif '[channel]' in x:
                            bword, id = x.split('[channel]')
                            if bword.strip().lower() in message.content.lower() and str(message.channel.id) == id:
                                word_found = False
                                break
                        if x.lower() in message.content.lower():
                            word_found = False
                            break

            user_found = False
            if bot.log_conf['user_logging'] == 'on':
                if '{} {}'.format(str(message.author.id), str(message.guild.id)) in bot.log_conf['keyusers']:
                    user = '{} {}'.format(str(message.author.id), str(message.guild.id))
                    cd_active, user_p = user_post(bot.key_users, user)
                    if cd_active:
                        bot.log_conf['keyusers'][user] = bot.key_users[user] = user_p
                        user_found = message.author.name

                elif '{} all'.format(str(message.author.id)) in bot.log_conf['keyusers']:
                    user = '{} all'.format(str(message.author.id), str(message.guild.id))
                    cd_active, user_p = user_post(bot.key_users, user)
                    if cd_active:
                        bot.log_conf['keyusers'][user] = bot.key_users[user] = user_p
                        user_found = message.author.name

            if word_found is True or user_found:
                if bot.log_conf['user_location'] != bot.log_conf['log_location'] and bot.log_conf['user_location'] != '' and not word_found:
                    location = bot.log_conf['user_location'].split()
                    is_separate = True
                else:
                    location = bot.log_conf['log_location'].split()
                    is_separate = False
                guild = bot.get_guild(int(location[1]))
                if str(message.channel.id) != location[0]:
                    msg = message.clean_content.replace('`', '')

                    context = []
                    total_context = 0
                    try:
                        for i in range(1, min(int(bot.log_conf['context_len']), len(bot.all_log[str(message.channel.id) + ' ' + str(message.guild.id)]))):
                            context.append(bot.all_log[str(message.channel.id) + ' ' + str(message.guild.id)][len(bot.all_log[str(message.channel.id) + ' ' + str(message.guild.id)])-i-1])
                            total_context += 1
                    except IndexError:  # This usually means that the bot's internal log has not been sufficiently populated yet
                        pass
                    msg = ''
                    for i in range(0, total_context):
                        temp = context[len(context)-i-1][0]
                        if temp.clean_content:
                            msg += 'User: %s | %s\n' % (temp.author.name, temp.created_at.replace(tzinfo=timezone.utc).astimezone(tz=None).__format__('%x @ %X')) + temp.clean_content.replace('`', '') + '\n\n'
                    msg += 'User: %s | %s\n' % (message.author.name, message.created_at.replace(tzinfo=timezone.utc).astimezone(tz=None).__format__('%x @ %X')) + message.clean_content.replace('`', '')
                    part = int(math.ceil(len(msg) / 1950))
                    if user_found:
                        title = '%s posted' % user_found
                    else:
                        title = '%s mentioned: %s' % (message.author.name, word)
                    if part == 1:
                        em = discord.Embed(timestamp=message.created_at, color=0xbc0b0b, title=title, description='Server: ``%s``\nChannel: <#%s> | %s\n\n**Context:**' % (str(message.guild), str(message.channel.id), message.channel.name))
                        while context:
                            temp = context.pop()
                            if temp[0].clean_content:
                                em.add_field(name='%s' % temp[0].author.name, value=temp[0].clean_content, inline=False)
                        em.add_field(name='%s' % message.author.name, value=message.clean_content, inline=False)
                        try:
                            em.set_thumbnail(url=message.author.avatar_url)
                        except:
                            pass
                        if bot.notify['type'] == 'msg':
                            await webhook(em, 'embed', is_separate)
                        elif bot.notify['type'] == 'ping':
                            await webhook(em, 'embed ping', is_separate)
                        else:
                            await guild.get_channel(int(location[0])).send(embed=em)
                    else:
                        split_list = [msg[i:i + 1950] for i in range(0, len(msg), 1950)]
                        all_words = []
                        split_msg = ''
                        for i, blocks in enumerate(split_list):
                            for b in blocks.split('\n'):
                                split_msg += b + '\n'
                            all_words.append(split_msg)
                            split_msg = ''
                        if user_found:
                            logged_msg = '``%s`` posted' % user_found
                        else:
                            logged_msg = '``%s`` mentioned' % word
                        for b, i in enumerate(all_words):
                            if b == 0:
                                if bot.notify['type'] == 'msg':
                                    await webhook(bot.bot_prefix + '%s in server: ``%s`` Context: Channel: <#%s> | %s\n\n```%s```' % (logged_msg, str(message.guild), str(message.channel.id), message.channel.name, i), 'message', is_separate)
                                elif bot.notify['type'] == 'ping':
                                    await webhook(bot.bot_prefix + '%s in server: ``%s`` Context: Channel: <#%s> | %s\n\n```%s```' % (logged_msg, str(message.guild), str(message.channel.id), message.channel.name, i), 'message ping', is_separate)
                                else:
                                    await guild.get_channel(int(location[0])).send(bot.bot_prefix + '%s in server: ``%s`` Context: Channel: <#%s>\n\n```%s```' % (logged_msg, str(message.guild), str(message.channel.id), i))
                            else:
                                if bot.notify['type'] == 'msg':
                                    await webhook('```%s```' % i, 'message', is_separate)
                                elif bot.notify['type'] == 'ping':
                                    await webhook('```%s```' % i, 'message ping', is_separate)
                                else:
                                    await guild.get_channel(int(location[0])).send('```%s```' % i)
                    bot.keyword_log += 1

        # Bad habit but this is for skipping errors when dealing with Direct messages, blocked users, etc. Better to just ignore.
        except (AttributeError, discord.errors.HTTPException):
            pass

    await bot.process_commands(message)


def add_alllog(channel, guild, message):
    if not hasattr(bot, 'all_log'):
        bot.all_log = {}
    if channel + ' ' + guild in bot.all_log:
        bot.all_log[channel + ' ' + guild].append((message, message.clean_content))
    else:
        bot.all_log[channel + ' ' + guild] = collections.deque(maxlen=int(get_config_value('log', 'log_size', 25)))
        bot.all_log[channel + ' ' + guild].append((message, message.clean_content))


def remove_alllog(channel, guild):
    del bot.all_log[channel + ' ' + guild]


# Webhook for keyword notifications
async def webhook(keyword_content, send_type, is_separate):
    if not is_separate:
        temp = bot.log_conf['webhook_url'].split('/')
    else:
        temp = bot.log_conf['webhook_url2'].split('/')
    channel = temp[len(temp) - 2]
    token = temp[len(temp) - 1]
    webhook_class = Webhook(bot)
    request_webhook = webhook_class.request_webhook
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
