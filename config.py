import telebot
import os

from dotenv import load_dotenv
from telebot import types

load_dotenv()

bot = telebot.TeleBot(os.getenv("TOKEN"))
removeMarkup = types.ReplyKeyboardRemove()