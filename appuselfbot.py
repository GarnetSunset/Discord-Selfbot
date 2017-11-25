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
