                    config["token"] = token
                    fp.seek(0)
                    fp.truncate()
                    json.dump(config, fp, indent=4)
                continue
        break
