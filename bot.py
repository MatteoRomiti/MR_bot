import time
import schedule
import config
import threading
import telegram
import pandas as pd 
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

#### CONSTANTS ####
boring_time = '11:00' # daily song suggested at this time
music_file = 'MariaMusic.tsv' # where the music comes from

music_df = pd.read_csv(music_file, sep='\t', dtype=(str))
number_of_tracks = music_df.shape[0]

# TODO: remove hard-coded list and fix the following 2 lines
# music_df.mood = music_df.mood.apply(lambda x: x.split())
# possible_moods = list(set(' '.join([mood for mood in music_df.mood.unique()]).split(" ")))
# possible_moods.remove("")
possible_moods = ['energico',
 'trasportante',
 'profondo',
 'pensieroso',
 'romantico',
 'particolare',
 'malinconico',
 'triste',
 'veloce',
 'allegro',
 'lento',
 'variabile',
 'positivo',
 'calmo',
 'potente',
 'cantato',
 'soft']
possible_lengths = music_df.duration.unique().tolist()

possible_lengths_int = [int(d) for d in music_df.duration.unique().tolist()]
possible_lengths_int.sort()
possible_moods.sort()
possible_lengths_s = " ".join([str(d) for d in possible_lengths])
possible_moods_s = " ".join(possible_moods)

def daily_song(bot):
	global boring_time
	schedule.every().day.at(boring_time).do(boring_job, bot)
	while True:
		schedule.run_pending()
		time.sleep(1)

def get_song(l=False, m=None):
	global music_df
	# print(l)
	# print(m)
	if not l:
		song = 'Randomly selected:\n'
		song += music_df.sample(1).link.values[0]
	else:
		if music_df[music_df.mood.str.contains(m)].shape[0] == 0:
			song = 'Aw, come on! Choose a proper mood!'
		else:
			if music_df[(music_df.mood.str.contains(m)) & (music_df.duration == l)].shape[0] == 0:
				song = 'Sorry! Lengths available for this mood are:\n'
				for d in music_df[music_df.mood.str.contains(m)].duration.unique():
					song += d + " "
			else:
				song = music_df[(music_df.mood.str.contains(m)) & (music_df.duration == l)].sample(1).link.values[0]
	return song

def boring_job(bot):
	song = 'It\'s Boring Time!\n'
	song = get_song()
	bot.send_message(chat_id=update.message.chat_id, text=song)


def start(bot, update):
	global music_df
	msg = "So, you want some music that I selected for Maria, huh?!\nOK...\nI currently have " + str(number_of_tracks) + " boring pieces. \nTry /music or /help"
	bot.send_message(chat_id=update.message.chat_id, text=msg)

def help(bot, update):
	global possible_moods
	global possible_lengths
	msg = 'Possible actions:\n\
		/music to get a random boring piece\n\
		/filters to set filters on length in minutes and mood (example: /filters 4 soft) \n\
		\n\
		Possible lengths:\n' + possible_lengths_s + '\n\
		Possible moods:\n' + possible_moods_s + '\n\nYes, in Italian! You have to know some basic Italian!\
		'
	bot.send_message(chat_id=update.message.chat_id, text=msg)

def stop(bot, update):
	msg = 'You still can\'t stop me!'
	bot.send_message(chat_id=update.message.chat_id, text=msg)

def music(bot, update):
	song = get_song()
	bot.send_message(chat_id=update.message.chat_id, text=song)

def filters(bot, update, args):
	song = get_song(args[0], args[1])
	bot.send_message(chat_id=update.message.chat_id, text=song)

def unknown(bot, update):
	msg = 'Nope! That\'s not working, sorry!'
	bot.send_message(chat_id=update.message.chat_id, text=msg)

def main():
	bot = telegram.Bot(config.credentials['TELEGRAM_TOKEN'])
	updater = Updater(config.credentials['TELEGRAM_TOKEN'])
	updater.dispatcher.add_handler(CommandHandler('start', start))
	updater.dispatcher.add_handler(CommandHandler('stop', stop))
	updater.dispatcher.add_handler(CommandHandler('music', music))
	updater.dispatcher.add_handler(CommandHandler('filters', filters, pass_args=True))
	updater.dispatcher.add_handler(CommandHandler('help', help))
	unknown_handler = MessageHandler(Filters.command, unknown)
	updater.dispatcher.add_handler(unknown_handler)

	t = threading.Thread(target=daily_song, args=(bot,), daemon=True)
	t.start()
	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	music_df = pd.read_csv(music_file, sep='\t', dtype=(str))
	main()

