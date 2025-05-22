import os
import random

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

BOT_TOKEN = '8072967467:AAGtvZCul-Vdy-hQCzl9eejTZBJmoz1fJI4'
bot = telebot.TeleBot(BOT_TOKEN)

# Загрузка анекдотов
with open("anekdot.txt", "r", encoding="utf-8") as file:
    aneki = file.readlines()

# Глобальные переменные для игры
user_scores = {}
user_cards = {}
dealer_cards = {}
game_in_progress = {}

# Колода карт
card_deck = [
    '2♠', '3♠', '4♠', '5♠', '6♠', '7♠', '8♠', '9♠', '10♠', 'В♠', 'Д♠', 'К♠', 'Т♠',
    '2♥', '3♥', '4♥', '5♥', '6♥', '7♥', '8♥', '9♥', '10♥', 'В♥', 'Д♥', 'К♥', 'Т♥',
    '2♦', '3♦', '4♦', '5♦', '6♦', '7♦', '8♦', '9♦', '10♦', 'В♦', 'Д♦', 'К♦', 'Т♦',
    '2♣', '3♣', '4♣', '5♣', '6♣', '7♣', '8♣', '9♣', '10♣', 'В♣', 'Д♣', 'К♣', 'Т♣'
]

card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'В': 2, 'Д': 3, 'К': 4, 'Т': 11
}


def calculate_score(cards):
    score = 0
    for card in cards:
        value = card[:-1]  # Убираем масть
        score += card_values[value]
    return score


def deal_card():
    return random.choice(card_deck)


def start_game(message):
    chat_id = message.chat.id
    user_cards[chat_id] = [deal_card(), deal_card()]
    dealer_cards[chat_id] = [deal_card(), deal_card()]
    game_in_progress[chat_id] = True

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Взять карту"), KeyboardButton("Остановиться"))

    user_score = calculate_score(user_cards[chat_id])
    dealer_score = calculate_score([dealer_cards[chat_id][0]])  # Показываем только одну карту дилера

    response = f"Ваши карты: {', '.join(user_cards[chat_id])} ({user_score} очков)\n"
    response += f"Карта дилера: {dealer_cards[chat_id][0]} ({dealer_score} очков)"

    bot.send_message(chat_id, response, reply_markup=markup)

    # Проверка на 21 очко сразу
    if user_score == 21:
        end_game(message, "blackjack")


def hit(message):
    chat_id = message.chat.id
    if not game_in_progress.get(chat_id, False):
        bot.send_message(chat_id, "Игра не начата. Нажмите /start_game чтобы начать.")
        return

    user_cards[chat_id].append(deal_card())
    user_score = calculate_score(user_cards[chat_id])

    response = f"Ваши карты: {', '.join(user_cards[chat_id])} ({user_score} очков)\n"
    response += f"Карта дилера: {dealer_cards[chat_id][0]}"

    if user_score > 21:
        end_game(message, "lose")
    elif user_score == 21:
        end_game(message, "win")
    else:
        bot.send_message(chat_id, response)


def stand(message):
    chat_id = message.chat.id
    if not game_in_progress.get(chat_id, False):
        bot.send_message(chat_id, "Игра не начата. Нажмите /start_game чтобы начать.")
        return

    # Дилер берет карты пока у него меньше 17 очков
    dealer_score = calculate_score(dealer_cards[chat_id])
    while dealer_score < 17:
        dealer_cards[chat_id].append(deal_card())
        dealer_score = calculate_score(dealer_cards[chat_id])

    user_score = calculate_score(user_cards[chat_id])

    response = f"Ваши карты: {', '.join(user_cards[chat_id])} ({user_score} очков)\n"
    response += f"Карты дилера: {', '.join(dealer_cards[chat_id])} ({dealer_score} очков)\n"

    if dealer_score > 21 or user_score > dealer_score:
        response += "\nВы выиграли! 🎉"
    elif user_score == dealer_score:
        response += "\nНичья! 🤝"
    else:
        response += "\nВы проиграли. 😢"

    bot.send_message(chat_id, response, reply_markup=ReplyKeyboardRemove())
    game_in_progress[chat_id] = False


def end_game(message, result):
    chat_id = message.chat.id
    user_score = calculate_score(user_cards[chat_id])
    dealer_score = calculate_score(dealer_cards[chat_id])

    response = f"Ваши карты: {', '.join(user_cards[chat_id])} ({user_score} очков)\n"
    response += f"Карты дилера: {', '.join(dealer_cards[chat_id])} ({dealer_score} очков)\n"

    if result == "blackjack":
        response += "\nBlackjack! Вы выиграли! 🎉"
    elif result == "win":
        response += "\nВы выиграли! 🎉"
    elif result == "lose":
        response += "\nПеребор! Вы проиграли. 😢"

    bot.send_message(chat_id, response, reply_markup=ReplyKeyboardRemove())
    game_in_progress[chat_id] = False


@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("Игра")
    button2 = KeyboardButton("Анекдот")
    markup.add(button1, button2)

    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Анекдот")
def handle_joke(message):
    i = random.randint(0, len(aneki) - 1)
    bot.send_message(message.chat.id, str(aneki[i]).replace("/n", "\n"))


@bot.message_handler(func=lambda message: message.text == "Игра")
def handle_game(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Начать игру"), KeyboardButton("Правила"))
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Начать игру")
def handle_start_game(message):
    start_game(message)


@bot.message_handler(func=lambda message: message.text == "Правила")
def handle_rules(message):
    rules = """
    🎮 Правила игры в 21 очко:

    1. Цель игры - набрать больше очков, чем дилер, но не больше 21.
    2. Карты от 2 до 10 дают очки по номиналу.
    3. Валет, Дама, Король дают 2, 3 и 4 очка соответственно.
    4. Туз дает 11 очков (или 1, если перебор).
    5. Вы можете брать карты или остановиться.
    6. Если у вас больше 21 - вы проиграли.
    7. Дилер берет карты, пока у него меньше 17 очков.
    8. Blackjack - 21 очко с двумя картами (Туз + 10/В/Д/К).
    """
    bot.send_message(message.chat.id, rules)


@bot.message_handler(func=lambda message: message.text == "Взять карту")
def handle_hit(message):
    hit(message)


@bot.message_handler(func=lambda message: message.text == "Остановиться")
def handle_stand(message):
    stand(message)


@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    if game_in_progress.get(message.chat.id, False):
        bot.send_message(message.chat.id, "Игра в процессе. Используйте кнопки 'Взять карту' или 'Остановиться'.")
    else:
        bot.send_message(message.chat.id, "Я не понимаю эту команду. Используйте кнопки меню.")


bot.polling()