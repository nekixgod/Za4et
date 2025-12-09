from aiogram import Router, F
from aiogram.types import Message
from keyboards.reply import main_menu, activities_menu
from handlers.auth import USER_PROFILES

router = Router()

@router.message(F.text == "👤 Моя анкета")
async def display_user_profile(message: Message):
    """
    Отображает профиль пользователя.
    """
    user_profile = USER_PROFILES.get(message.from_user.id)

    if not user_profile:
        await message.answer(
            "⚠️ Анкета не обнаружена. Пройдите регистрацию через команду /start."
        )
        return

    # Формируем информацию профиля
    profile_lines = []

    # Основная информация
    profile_lines.append(f"👤 <b>{user_profile['bio']['first_name']} {user_profile['bio']['last_name']}</b>")

    # Демографические данные
    if user_profile["bio"].get("birth_year"):
        profile_lines.append(f"🎂 Год рождения: {user_profile['bio']['birth_year']}")

    if user_profile["bio"].get("gender"):
        gender_display = "Мужчина" if user_profile['bio']['gender'] == "man" else "Женщина"
        profile_lines.append(f"⚧️ Пол: {gender_display}")

    # Локация
    if user_profile["geo_info"].get("city"):
        profile_lines.append(f"📍 Город: {user_profile['geo_info']['city']}")

    # Интересы
    if user_profile["preferences"].get("hobby"):
        profile_lines.append(f"❤️ Увлечение: {user_profile['preferences']['hobby']}")

    # Контакт
    if user_profile["contacts"].get("phone_number"):
        profile_lines.append(f"📱 Контакт: {user_profile['contacts']['phone_number']}")

    profile_text = "\n".join(profile_lines)

    # Отправляем с фото или без
    if user_profile["media_content"].get("profile_image"):
        await message.answer_photo(
            photo=user_profile["media_content"]["profile_image"],
            caption=profile_text,
            parse_mode="HTML"
        )
    else:
        await message.answer(
            profile_text,
            parse_mode="HTML"
        )

@router.message(F.text == "🎮 Развлечения")  # ИСПРАВЛЕНО!
async def present_games_selection(message: Message):
    """
    Отображает меню доступных игр.
    """
    await message.answer(
        "Выберите игру из списка:",
        reply_markup=activities_menu
    )

@router.message(F.text == "📘 Справка")
async def project_information(message: Message):
    """
    Показывает информацию о возможностях бота.
    """
    await message.answer(
        "🤖 <b>Добро пожаловать в Fantasy Companion!</b>\n\n"

        "<b>🎮 Доступные игры:</b>\n"
        "✂️ <b>Камень-ножницы-бумага</b>\n"
        "— Сделайте выбор из трех элементов.\n"
        "— Система генерирует свой вариант.\n"
        "— Камень побеждает ножницы, ножницы — бумага, бумага — камень.\n\n"

        "🎲 <b>Бросок кубика</b>\n"
        "— Предположите число от 1 до 6.\n"
        "— Виртуальный кубик будет брошен.\n"
        "— Совпадение приносит победу! 🎯\n\n"

        "<b>📚 Читалка:</b>\n"
        "— Статьи о русских богатырях и мифических существах.\n"
        "— Навигация по текстам с закладками.\n"
        "— Сохранение позиции чтения.\n\n"

        "<b>👤 Персональный профиль:</b>\n"
        "— Хранение данных пользователя.\n"
        "— Возможность просмотра анкеты.\n\n"

        "Приятного использования! ✨",
        reply_markup=main_menu,
        parse_mode="HTML"
    )

@router.message()
async def process_unrecognized_input(message: Message):
    """
    Обрабатывает неподдерживаемые сообщения.
    """
    error_gif = "https://media1.tenor.com/m/eBWplvjY4RUAAAAC/mi.gif"

    await message.answer_animation(
        animation=error_gif,
        caption=(
            "К сожалению, я не распознал ваш запрос.\n\n"
            "Пожалуйста, используйте кнопки навигации "
            "или доступные команды меню."
        ),
        reply_markup=main_menu
    )