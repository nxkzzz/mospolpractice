# Этапы создания Telegram-бота для учёта расходов

## 1. Получение токена от BotFather

Чтобы начать создание Telegram-бота, необходимо получить **токен** — уникальный ключ, который используется для взаимодействия с API Telegram.

**Шаги:**
1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather).
2. Отправьте команду `/start`, затем `/newbot`.
3. Укажите имя и уникальное имя пользователя для бота (должно заканчиваться на `bot`).
4. Скопируйте полученный токен — он понадобится для настройки бота в коде.

---

## 2. Подключение необходимых библиотек

```python
import logging
import pandas as pd
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from io import BytesIO
```

---

## 3. Настройка логирования

```python
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
```

---

## 4. Работа с Excel-файлом

Создание файла, если он ещё не существует:

```python
EXCEL_FILE = 'expenses.xlsx'

def create_expenses_file():
    try:
        df = pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Дата", "Сумма", "Описание"])
        df.to_excel(EXCEL_FILE, index=False)
```

---

## 5. Запись нового расхода

```python
def record_expense(date: str, amount: float, description: str):
    df = pd.read_excel(EXCEL_FILE)
    new_row = pd.DataFrame({"Дата": [date], "Сумма": [amount], "Описание": [description]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
```

---

## 6. Просмотр расходов

```python
def show_expenses(date: str = None):
    df = pd.read_excel(EXCEL_FILE)
    df['Дата'] = pd.to_datetime(df['Дата'])

    if date:
        filtered_df = df[df['Дата'].dt.strftime('%Y-%m-%d') == date]
    else:
        filtered_df = df

    if filtered_df.empty:
        return "Нет расходов за указанную дату."
    
    return "\n".join([
        f"{row['Дата'].strftime('%Y-%m-%d')} - {row['Сумма']} - {row['Описание']}" 
        for _, row in filtered_df.iterrows()
    ])
```

---

## 7. Отправка Excel-файла

```python
async def send_expense_file(update: Update):
    df = pd.read_excel(EXCEL_FILE)
    with BytesIO() as output:
        df.to_excel(output, index=False)
        output.seek(0)
        await update.message.reply_document(document=output, filename="expenses.xlsx")
```

---

## 8. Команды Telegram-бота

```python
async def start(update: Update, context: CallbackContext) -> None:
    welcome_text = (
        "Привет! Я помогу тебе вести учёт твоих расходов. Вот что я умею:\n\n"
        "*Команды:*\n"
        "/add <сумма> <описание> — добавить расход\n"
        "/show <дата> — показать расходы за дату\n"
        "/show — показать все расходы\n"
        "/file — получить Excel-файл"
    )
    await update.message.reply_text(welcome_text)

async def add_expense(update: Update, context: CallbackContext) -> None:
    try:
        date = datetime.now().strftime('%Y-%m-%d')
        amount = float(context.args[0])
        description = " ".join(context.args[1:])
        record_expense(date, amount, description)
        await update.message.reply_text(f"Расход {amount} за {date} успешно добавлен!")
    except (IndexError, ValueError):
        await update.message.reply_text("Ошибка. Формат: /add <сумма> <описание>")

async def show_expenses_command(update: Update, context: CallbackContext) -> None:
    try:
        date = context.args[0] if context.args else None
        expenses = show_expenses(date)
        await update.message.reply_text(expenses)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def file(update: Update, context: CallbackContext) -> None:
    await send_expense_file(update)
```

---

## 9. Запуск бота

```python
def main():
    create_expenses_file()
    TOKEN = 'ВАШ_ТОКЕН_ОТ_BOTFATHER'
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_expense))
    application.add_handler(CommandHandler("show", show_expenses_command))
    application.add_handler(CommandHandler("file", file))

    application.run_polling()

if __name__ == '__main__':
    main()
```

---

## 10. Видеоинструкция по созданию Telegram-бота

Для наглядного понимания процесса вы можете посмотреть это видео:

[![Смотреть видео](https://img.youtube.com/vi/H4rX1NhJNWM/0.jpg)](https://youtu.be/H4rX1NhJNWM)

---

## Заключение

Теперь вы знаете, как создать Telegram-бота для учёта личных расходов. Такой бот позволяет удобно записывать траты, просматривать историю и выгружать их в Excel. Отличное решение для личного финансового учёта!