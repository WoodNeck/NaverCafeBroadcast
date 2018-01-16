# -*- coding: utf-8 -*-
import os
import sys
import time
import logging
import discord
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from utils.botconfig import BotConfig
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

des = "Naver Cafe Chatting Bot"
prefix = "$"

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, command_prefix=prefix, **kwargs)
        self.prefix = prefix
        os.environ["MOZ_HEADLESS"] = '1'
        binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe', log_file=sys.stdout)
        self.driver = webdriver.Firefox(firefox_binary=binary)
        self.naverId = None
        self.naverPwd = None
        self.target = None
        self.textArea = None
        self.sendBtn = None
        self.lastMsg = None
        self.channel = None
    
    def loginToChattingRoom(self):
        self.driver.get(self.target)
        user = self.driver.find_element_by_id("id")
        password = self.driver.find_element_by_id("pw")
        user.send_keys(self.naverId)
        password.send_keys(self.naverPwd)
        loginBtn = self.driver.find_element_by_class_name("btn_global")
        loginBtn.click()
        
        self.textArea = self.driver.find_element_by_id("msgInputArea")
        self.sendBtn = self.driver.find_elements_by_tag_name("button")[4]

        time.sleep(3)
        messages = self.driver.find_elements_by_class_name("msg")
        self.lastMsg = int(messages[-1].get_attribute("msgsn"))

    def listenToChattingRoom(self):
        try:
            while (True):
                msg = self.driver.find_element_by_xpath("//div[@msgsn='{}']".format(self.lastMsg + 1))
                self.lastMsg = int(msg.get_attribute("msgsn"))
                if not "my" in msg.get_attribute("class"):
                    author = msg.find_element_by_class_name("name").text
                    content = msg.find_element_by_class_name("_chat_msg").text
                    asyncio.run_coroutine_threadsafe(self.send_message(self.channel, "{}/{}".format(author, content)),
                                                    self.loop)
        except:
            return
    
    def sendToChattingRoom(self, msg):
        self.textArea.send_keys(msg)
        self.sendBtn.click()
    
def initialize(bot_class=Bot):
    bot = bot_class(description=des)

    @bot.event
    async def on_ready():
        bot.loginToChattingRoom()
        server = None
        for item in bot.servers:
            server = item
        bot.channel = server.default_channel
        print("{}".format(discord.version_info))
        print("{} 준비 다됬어용".format(bot.user))
        await bot.change_presence(game=discord.Game(name="{}".format(prefix)))
        listener = BackgroundScheduler()
        listener.start()
        listener.add_job(bot.listenToChattingRoom, 'interval', seconds = 1)

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return
        if not message.content.startswith(bot.prefix):
            return
        
        author = message.author.nick
        if not author:
            author = message.author.name
        content = message.content[1:]
        if content:
            bot.sendToChattingRoom("{}/{}".format(author, content))

    @bot.event
    async def on_command_error(error, ctx):
        channel = ctx.message.channel
        if isinstance(error, commands.MissingRequiredArgument):
            await bot.send_message(channel, "명령어 인자가 부족해용")
        elif isinstance(error, commands.BadArgument):
            await bot.send_message(channel, "명령어 인자가 잘못되었어용.")
        elif isinstance(error, commands.DisabledCommand):
            await bot.send_message(channel, "비활성화된 명령어에용.")
        elif isinstance(error, commands.CommandInvokeError):
            await bot.send_message(channel, str(error))
            print(error)
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.CheckFailure):
            await bot.send_message(channel, "명령어 실행에 실패했어용: {}".format(error))
        elif isinstance(error, commands.NoPrivateMessage):
            pass
        elif isinstance(error, commands.CommandOnCooldown):
            await bot.send_message(channel, "지금은 할 수가 없어용"
                                            "{:.2f}초 뒤에 다시 해주세용"
                                            "".format(error.retry_after))
    return bot

if __name__ == '__main__':
    bot = initialize()
    config = BotConfig()
    token = config.request("BotUser", "Token")
    bot.naverId = config.request("Naver", "ID")
    bot.naverPwd = config.request("Naver", "PWD")
    bot.target = config.request("Naver", "Target")
    config.save()

    bot.run(token)