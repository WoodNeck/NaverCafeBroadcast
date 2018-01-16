# -*- coding: utf-8 -*-
import os
import sys
import logging
import discord
from utils.botconfig import BotConfig
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

des = "Naver Cafe Chatting Bot"
prefix = "$"

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, command_prefix=prefix, **kwargs)
        self.prefix = prefix
        options = Options()  
        options.add_argument("--headless") 
        self.driver = webdriver.Chrome()
        self.naverId = None
        self.naverPwd = None
        self.target = None
    
    def loginToChattingRoom():
        self.driver.get(self.target)
        user = self.driver.find_element_by_id("id")
        password = self.driver.find_element_by_id("pw")
        user.send_keys(self.naverId)
        password.send_keys(self.naverPwd)
        loginBtn = self.driver.find_element_by_class_name("btn_global")
        loginBtn.click()
        
        print(self.driver.current_url)
    
    def sendToChattingRoom():

    
def initialize(bot_class=Bot):
    bot = bot_class(description=des)

    @bot.event
    async def on_ready():
        bot.loginToChattingRoom()
        print("{}".format(discord.version_info))
        print("{} 준비 다됬어용".format(bot.user))
        await bot.change_presence(game=discord.Game(name="{}".format(prefix)))

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return
        if not message.content.startswith(bot.prefix):
            return
        
        content = message[1:]
        if content:
            bot.sendToChattingRoom(content)

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

    user_token = ""
    config = BotConfig()
    token = config.request("BotUser", "Token")
    bot.naverId = config.request("Naver", "ID")
    bot.naverPwd = config.request("Naver", "PWD")
    bot.target = config.request("Naver", "Target")
    config.save()

    bot.run(token)