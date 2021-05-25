import os
from ibm_watson import LanguageTranslatorV3
from pandas import json_normalize
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from pandas import json_normalize
from os import remove
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import telebot
from telebot.util import content_type_media


def convert_audio_text(video, contentType):
    filename = video

    url_s2t = "---------------------------------"
    iam_apikey_s2t = "-----------------------------"
    authenticator = IAMAuthenticator(iam_apikey_s2t)
    s2t = SpeechToTextV1(authenticator=authenticator)
    s2t.set_service_url(url_s2t)

    with open(filename, mode="rb") as wav:
        response = s2t.recognize(audio=wav, content_type=contentType)

    json_normalize(response.result['results'], "alternatives")
    recognized_text = response.result['results'][0]["alternatives"][0]["transcript"]
    # print(recognized_text)

    url_lt = '-------------------------------------'
    apikey_lt = '---------------------------------------'
    version_lt = '2018-05-01'

    authenticator = IAMAuthenticator(apikey_lt)
    language_translator = LanguageTranslatorV3(
        version=version_lt, authenticator=authenticator)
    language_translator.set_service_url(url_lt)

    json_normalize(
        language_translator.list_identifiable_languages().get_result(), "languages")
    translation_response = language_translator.translate(
        text=recognized_text, model_id='en-ar')

    translation = translation_response.get_result()

    spanish_translation = translation['translations'][0]['translation']
    return spanish_translation


API_TOKEN = '--------------------------------'


bot = telebot.TeleBot(API_TOKEN)
selectedLanguage = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, "Welcome to the translation bot of sounds into Arabic")
    msg = bot.send_message(
        message.chat.id, "Send the voice Please")


@bot.message_handler(content_types=content_type_media)
def voice_processing(message):
    # print(message)
    try:
        fileType = ''
        msg = bot.send_message(message.chat.id, 'اشوية ياخذ وقت انتظروا ')
        if(message.voice):
            fileType = message.voice
            file_info = bot.get_file(fileType.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(fileType.file_id+'.'+str(fileType.mime_type).replace('audio/', ''), 'wb') as new_file:
                new_file.write(downloaded_file)
            msg = bot.send_message(message.chat.id, convert_audio_text(
                fileType.file_id+'.'+str(fileType.mime_type).replace('audio/', ''), str(fileType.mime_type)))

            os.remove(fileType.file_id+'.' +
                      str(fileType.mime_type).replace('audio/', ''))

        # elif(message.audio):
        #     fileType = message.audio
        #     file_info = bot.get_file(fileType.file_id)
        #     downloaded_file = bot.download_file(file_info.file_path)
        #     with open(fileType.file_id+'.'+str('mp3'), 'wb') as new_file:
        #         new_file.write(downloaded_file)
        #     msg = bot.send_message(message.chat.id,convert_audio_text(fileType.file_id+'.mp3','audio/mp3'))
    except:
        msg = bot.send_message(message.chat.id, 'only voice ( بس بصمة )')


bot.polling()
