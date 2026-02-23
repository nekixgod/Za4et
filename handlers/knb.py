import random
from aiogram import Router, F
from aiogram.types import Message
from keyboards.reply import elemental_menu, activities_menu, main_menu

router = Router()

GAME_OPTIONS = {
    "🗿 Камень": "🗿",
    "✂️ Ножницы": "✂️",
    "📄 Бумага": "📄"  # Изменили Пергамент на Бумагу
}

VICTORY_RULES = {
    "🗿": "✂️",  # Камень побеждает ножницы
    "✂️": "📄",  # Ножницы побеждают бумагу
    "📄": "🗿"   # Бумага побеждает камень
}

@router.message(F.text == "✂️ Камень-ножницы-бумага")
async def launch_rps_game(message: Message):
    """
    Запускает игру "Камень, ножницы, бумага".
    """
    await message.answer(
        "Сделайте ваш выбор:",
        reply_markup=elemental_menu
    )

@router.message(F.text.in_(GAME_OPTIONS.keys()))
async def process_player_move(message: Message):
    """
    Обрабатывает ход игрока и определяет результат.
    """
    player_symbol = GAME_OPTIONS[message.text]
    opponent_symbol = random.choice(list(GAME_OPTIONS.values()))

    # Анализируем исход раунда
    if player_symbol == opponent_symbol:
        outcome_text = "*Раунд завершился ничьей!* ⚖️"
        outcome_icon = "⚖️"
    elif VICTORY_RULES[player_symbol] == opponent_symbol:
        outcome_text = "*Победа за вами!* 🏆"
        outcome_icon = "🏆"
    else:
        outcome_text = "_В этом раунде победа у системы._ 💻"
        outcome_icon = "💻"

    # Формируем игровую статистику
    game_report = (
        f"*Ваш символ:* {player_symbol}\n"
        f"*Символ системы:* {opponent_symbol}\n\n"
        f"{outcome_text}\n"
        f"Иконка исхода: {outcome_icon}"
    )

    await message.answer(
        game_report,
        reply_markup=elemental_menu,
        parse_mode="Markdown"
    )

@router.message(F.text == "◀️ К активности")  # ИЗМЕНЕНО
async def return_to_games_list(message: Message):
    """
    Возвращает пользователя к выбору игр.
    """
    await message.answer(
        "Выберите мини-игру:",
        reply_markup=activities_menu
    )

@router.message(F.text == "◀️ Основное меню")  # ИЗМЕНЕНО
async def navigate_to_main_menu(message: Message):
    """
    Возвращает пользователя в главное меню.
    """
    await message.answer(
        "Основное меню:",
        reply_markup=main_menu
    )
