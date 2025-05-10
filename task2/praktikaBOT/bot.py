import logging
import pandas as pd
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from io import BytesIO

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Имя файла Excel для хранения данных
EXCEL_FILE = 'expenses.xlsx'

# Заготовка для таблицы расходов, если файл ещё не существует
def create_expenses_file():
    try:
        df = pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Дата", "Сумма", "Описание"])
        df.to_excel(EXCEL_FILE, index=False)

# Функция для записи расходов в файл
def record_expense(date: str, amount: float, description: str):
    df = pd.read_excel(EXCEL_FILE)
    new_row = pd.DataFrame({"Дата": [date], "Сумма": [amount], "Описание": [description]})
    df = pd.concat([df, new_row], ignore_index=True)  # Добавляем новую строку
    df.to_excel(EXCEL_FILE, index=False)

# Функция для отображения всех расходов за определенную дату или период
def show_expenses(date: str = None):
    df = pd.read_excel(EXCEL_FILE)
    df['Дата'] = pd.to_datetime(df['Дата'])

    if date:
        filtered_df = df[df['Дата'].dt.strftime('%Y-%m-%d') == date]
    else:
        filtered_df = df

    if filtered_df.empty:
        return "Нет расходов за указанную дату."
    
    return "\n".join([f"{row['Дата'].strftime('%Y-%m-%d')} - {row['Сумма']} - {row['Описание']}" 
                      for index, row in filtered_df.iterrows()])

# Функция для отправки файла Excel с расходами
async def send_expense_file(update: Update):
    df = pd.read_excel(EXCEL_FILE)
    
    # Сохраняем таблицу в BytesIO, чтобы отправить как файл
    with BytesIO() as output:
        df.to_excel(output, index=False)
        output.seek(0)
        # Отправляем файл пользователю
        await update.message.reply_document(document=output, filename="expenses.xlsx")

# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    welcome_text = (
        "Привет! Я помогу тебе вести учёт твоих расходов. Вот что я умею:\n\n"
        
        "*Команды для работы с расходами:*\n"
        "/add <сумма> <описание> - Добавить новый расход\n"
        "Пример: /add 500 ужин с друзьями\n\n"
        
        "/show <дата> - Показать все расходы за определённую дату (формат даты: YYYY-MM-DD)\n"
        "Пример: /show 2025-05-09\n\n"
        
        "/show - Показать все расходы за весь период\n\n"
        
        "/file - Получить файл Excel с расходами\n\n"
        
        "Если у тебя есть вопросы или ты хочешь начать, используй команду /add или /show!"
    )

    await update.message.reply_text(welcome_text)

# Команда /add для добавления расхода
async def add_expense(update: Update, context: CallbackContext) -> None:
    try:
        date = datetime.now().strftime('%Y-%m-%d')  # Дата будет текущей
        amount = float(context.args[0])  # Сумма расхода
        description = " ".join(context.args[1:])  # Описание расхода

        record_expense(date, amount, description)
        await update.message.reply_text(f"Расход {amount} за {date} успешно добавлен!")
    except (IndexError, ValueError):
        await update.message.reply_text("Ошибка. Используй команду в формате: /add <сумма> <описание>")

# Команда /show для отображения расходов за дату или период
async def show_expenses_command(update: Update, context: CallbackContext) -> None:
    try:
        date = context.args[0] if context.args else None
        expenses = show_expenses(date)
        await update.message.reply_text(expenses)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

# Команда /file для отправки Excel-файла с расходами
async def file(update: Update, context: CallbackContext) -> None:
    await send_expense_file(update)

def main():
    # Создаем или загружаем файл Excel
    create_expenses_file()

    # Токен бота
    TOKEN = '7214829955:AAGXeJAjzHRSFIHh-XarjCo6Ie5y24SIlYU'
    
    # Используем Application вместо Updater
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_expense))
    application.add_handler(CommandHandler("show", show_expenses_command))
    application.add_handler(CommandHandler("file", file))

    # Начинаем работу бота
    application.run_polling()

if __name__ == '__main__':
    main()
