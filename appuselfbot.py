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
