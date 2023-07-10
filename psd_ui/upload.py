import re
import requests
import subprocess
import json

TARMAC_TOML = '''name = "{0}"

[[inputs]]
glob = "{1}/*.png"
codegen = true
codegen-path = "{1}/assetids.lua"
codegen-base-path = "{1}"'''


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return json.loads(myjson)


def VerifyUsername(cookie):
    try:
        response = requests.get("https://roblox.com/my/profile", cookies={".ROBLOSECURITY": cookie})
        isJson = is_json(response.text)

        if isJson == False: 
            print("Something was wrong with the cookie provided. Ensure it's a valid account cookie.")
        else: 
            return "y" == input("The username associated with this cookie is " + isJson["Username"] + ". Is this correct? (y/n) : ")
    except Exception as e:
        print(e)
        print("Something was wrong with the cookie provided. Ensure it's a valid account cookie.")
        return False


def TarmacSync(outputPath, cookie):
    parentPath = outputPath.parent
    subPath = "/".join(outputPath.parts[-1:])

    f = open(parentPath.as_posix() + "/tarmac.toml", "w")
    f.write(TARMAC_TOML.format(parentPath.stem, subPath))
    f.close()

    subprocess.run([
        "tarmac", "sync",
        "--target", "roblox",
        "--retry", "10",
        "--retry-delay", "60",
        "--auth", cookie
    ], cwd=parentPath.as_posix())

    f = open(outputPath.as_posix() + "/assetids.lua", "r")
    matches = re.findall(r'\S+_(\d+) = "(rbxassetid://\d+)"', f.read())

    arr = []
    for match in matches:
        index = int(match[0]) - 1
        arr.insert(index, match[1])

    return arr
