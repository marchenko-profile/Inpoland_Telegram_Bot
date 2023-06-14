import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import telebot
from telebot import types
import time
import schedule

from backround import keep_alive


# Здесь указываем токен вашего Telegram-бота
bot_token = '6181577945:AAFN6_WEnpSBU6FkiR8rTkBLQ6XTd3d-VAs'
# Здесь указываем ваш Telegram-идентификатор
chat_id = '-1001957447975'

# Create a bot instance
bot = telebot.TeleBot(bot_token)

# Define the base URL for the website
base_url = 'https://inpoland.net.pl/novosti/'

# Variable to store the latest ad URL
latest_ad_url = None

# Function to check for new ads
def check_for_new_ads():
    global latest_ad_url

    url = 'https://inpoland.net.pl/novosti/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Check if the request was successful
    if response.status_code == 200:
        # Find the first ad on the page
        ad = soup.find('article', {'class': 'equalheight'})

        # Get the URL of the first ad
        ad_url = ad.find('div', {'class': 'news-comment readmore'}).find('a')['href']

        # Check if the latest ad URL is different from the current ad URL
        if latest_ad_url != ad_url:
            latest_ad_url = ad_url
            parse_ads()

    else:
        bot.send_message(chat_id, 'Error while making a request.')





# Function to parse ads
def parse_ads():
    news_limit = 10  # Количество новостей для парсинга при запуске

    url = 'https://inpoland.net.pl/novosti/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Check if the request was successful
    if response.status_code == 200:
        # Find all ads on the page
        ads = soup.find_all('article', {'class': 'equalheight'})

        # Limit the number of ads to parse
        ads = ads[:news_limit]

        # Iterate over the ads
        for ad in ads:
            try:
                # Extract photo, title, description, and ad URL
                photos = ad.find_all('img')
                photo_urls = [urljoin(base_url, photo['src']) for photo in photos]
                title = ad.find('h3', {'class': 'news-title'}).find('a').text
                description = ad.find('div', {'class': 'news-block-content'}).text
                ad_url = ad.find('a')['href']

                # Check if the ad URL is already parsed
                if is_ad_parsed(ad_url):
                    continue

                # Create a message with the ad and a button to open the ad URL
                message = ''

                # Add photos to the message
                for photo_url in photo_urls:
                    message += f'<a href="{photo_url}">&#8203;</a>'

                # Add title and description of the ad
                message += f'<b>{title}</b>\n'
                message += f'{description}\n'

                # Create an InlineKeyboardMarkup object for the buttons
                keyboard = types.InlineKeyboardMarkup()

                # Add the "Читати повністю" button
                if ad_url:
                    button = types.InlineKeyboardButton(text='Читати повністю', url=ad_url)
                    keyboard.add(button)

                # Add the "Підтримай та підпишись" button
                youtube_url = 'https://www.youtube.com/channel/UCj5kIQ79engOuAk50n_uj5w?sub_confirmation=1'
                youtube_button = types.InlineKeyboardButton(text='Підтримай та підпишись', url=youtube_url)
                keyboard.add(youtube_button)

                # Remove the link from the ad
                message_without_link = message.replace(ad_url, '')

                # Send the message to Telegram with photos, title, description, and buttons
                bot.send_message(chat_id, message_without_link, parse_mode='HTML', reply_markup=keyboard)

                # Mark the ad as parsed
                mark_ad_as_parsed(ad_url)

            except Exception as e:
                print(f'Error processing ad: {e}')

    else:
        bot.send_message(chat_id, 'Error while making a request.')

# Function to check if an ad is already parsed
def is_ad_parsed(ad_url):
    with open('inparsed_ads.txt', 'r') as file:
        parsed_ads = file.read().splitlines()

    return ad_url in parsed_ads

# Function to mark an ad as parsed
def mark_ad_as_parsed(ad_url):
    with open('inparsed_ads.txt', 'a') as file:
        file.write(ad_url + '\n')

# Handler for the /start command
@bot.message_handler(commands=['start'])
def start(message):
    parse_ads()
    bot.reply_to(message, 'Ads successfully loaded!')

# Schedule the job every 2 minutes
schedule.every(1).minutes.do(check_for_new_ads)


keep_alive()
# Run the bot
while True:
    schedule.run_pending()
    time.sleep(60)