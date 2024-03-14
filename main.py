from telebot import TeleBot
from telebot.types import Message
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv('.env')
TG_TOKEN = os.getenv('TG_TOKEN')

bot = TeleBot(TG_TOKEN)


class Purchase:
    def __init__(self, item_name, price):
        self.item_name = item_name
        self.price = price
        self.purchase_date = datetime.now().strftime("%d-%m-%Y")

    def __str__(self):
        return f"{self.item_name} - {self.price} руб. ({self.purchase_date})"


class Client:
    def __init__(self, user_id, first_name, last_name, bird_date, card_id):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.bird_data = bird_date
        self.card_id = card_id
        self.purchases = []  # Покупки клиентов


clients = []  # Список хранения информации о клиентах


def add_client(user_id, first_name, last_name, bird_date, card_id):
    check_client = next((client for client in clients if str(client.card_id) == str(card_id)), None)
    if check_client:
        bot.send_message(user_id, "Клиент с указанным идентификатором уже существует")
    else:
        new_client = Client(user_id, first_name, last_name, bird_date, card_id)
        clients.append(new_client)
        bot.send_message(user_id, "Новый клиент добавлен в базу. Для просмотра списка введите /show_base")


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: Message) -> None:
    """Отправляет приветствие и инструкцию по работе с ботом"""
    welcome_text = """
    Привет! Я бот по управлению задачами. Вот как со мной работать:
    - Чтобы добавить клиента отправьте в одном сообщении /add_client Имя, Фамилия, Дата рождения (ДД.ММ.ГГГГ), ID карты
    - Для просмотра базы клиентов введите /show_base
    - Для просмотра подробной информации о клиенте введите /info_client и номер клиента
    - Для удаления клиента из базы введите /delite_client и его номер
    - Для добавления покупки введите /add_purchase card_id, наименование товара, цена
    - Чтобы вернуться к инструкции введите /help
    """

    user_id: int = message.chat.id
    bot.send_message(user_id, welcome_text)


@bot.message_handler(commands=['add_client'])
def handle_add_client(message: Message) -> None:
    user_id: int = message.chat.id
    text: str = message.text[11:].strip()  # Берем текст после /add_client
    if not text:
        bot.send_message(user_id, "Введите данные клиента")
        return
    else:
        client_data = text.split(", ")  # Для разделения текста
        add_client(user_id, *client_data,)


@bot.message_handler(commands=['show_base'])
def show_base(message: Message) -> None:
    """Выводит базу клиентов"""
    user_id: int = message.chat.id
    message_text = "Ваши клиенты:\n"
    message_text_1 = """
    Для более подробной информации о клиенте отправьте /client_info и номер клиента.
    Для удаления клиента из базы отправьте /delite_client и номер клиента
    """
    for i, client in enumerate(clients, start=1):
        message_text += f"{i}. {client.first_name}{client.last_name}{client.card_id}\n"
    bot.send_message(user_id, message_text + message_text_1)


@bot.message_handler(commands=['info_client'])
def client_info(message: Message) -> None:
    """Выводит подробную информацию о клиенте"""
    user_id: int = message.chat.id
    text = message.text[12:].strip()
    try:
        client_number = int(text)
        client_info = clients[client_number - 1]  # с учетом индексации
        full_info = (
            f"Имя:{client_info.first_name}\n"
            f"Фамилия:{client_info.last_name}\n"
            f"Дата рождения:{client_info.birth_date}\n"
            f"id-карта:{client_info.card_id}\n"
        )
        if client_info.purchases:
            purchases_info = "\nПокупки:\n"
            for purchase in client_info.purchases:
                purchases_info += str(purchase) + "\n"
                full_info += purchases_info
            else:
                full_info += "\nПокупок нет"
                bot.send_message(user_id, full_info)
    except (ValueError, IndexError):
        bot.send_message(user_id, "Некорректный номер клиента! Введите корректный номер!")


@bot.message_handler(commands=['add_purchase'])
def handle_add_purchase(message: Message) -> None:
    """Добавляет товар"""
    user_id: int = message.chat.id
    text: str = message.text[13:].strip()
    try:
        parts = text.split(", ")
        card_id = int(parts[0])
        item_name = parts[1]
        price = float(parts[2])
        purchase_date = datetime.now().strftime("%d-%m-%Y")
        check_client = next((client for client in clients if str(client.card_id) == str(card_id)), None)
        if check_client:
            new_purchase = Purchase(item_name, price)
            new_purchase.purchase_data = purchase_date  # Создали покупку
            check_client.purchases.append(new_purchase)
            bot.send_message(user_id,
                             f"Покупка для клиента{check_client.first_name}{check_client.last_name}"
                             f" добавлена")
        else:
            bot.send_message(user_id, "Клиент с указанным номером не найден")
    except (ValueError, IndexError, TypeError):
        bot.send_message(user_id, "Некорректный формат ввода! Введите корректный формат!")


@bot.message_handler(commands=['delite_client'])
def delite_client(message: Message) -> None:
    user_id: int = message.chat.id
    text = message.text[14:].strip()
    client_index = int(text)
    if 1 <= client_index <= len(clients):
        clients.pop(client_index - 1)  # Удаляет выбранного клиента
        bot.send_message(user_id, "Клиент удален! Для просмотра базы клиентов отправьте /show_base")
    else:
        bot.send_message(user_id, "Некорректный номер клиента! Введите корректный номер!")


if __name__ == "__main__":
    bot.infinity_polling()
