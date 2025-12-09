import logging
from typing import List
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.reply import main_menu, activities_menu

router = Router()
reader_sessions = {}

def format_markdown(text: str) -> str:
    """
    Экранирует специальные символы для MarkdownV2.
    """
    special_chars = r'_*[]()~`>#+-=|{}.!'
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    return text

# СТАТИЧЕСКАЯ БАЗА ЗНАНИЙ - Русские богатыри и мифические существа
FANTASY_ARTICLES = [
    {
        "title": "Илья Муромец",
        "content": """*Илья Муромец* — самый известный и почитаемый богатырь русского былинного эпоса.

*Основные подвиги:*
• Победа над Соловьём-разбойником
• Освобождение Чернигова от осады
• Битва с Идолищем поганым
• Победа над Калином-царём

*Особенности:*
До 33 лет Илья был парализован, но исцелился благодаря старцам-странникам. Получив невиданную силу, он отправился на службу к князю Владимиру в Киев. Его меч-кладенец и могучий конь Бурушка стали легендарными.

*Интересный факт:*
Илья Муромец — реальная историческая личность. Его мощи покоятся в Киево-Печерской лавре, где он провёл последние годы жизни в монашестве."""
    },
    {
        "title": "Алёша Попович",
        "content": """*Алёша Попович* — младший из трёх главных русских богатырей, известный своей хитростью и смекалкой.

*Характерные черты:*
• Сын ростовского попа
• Не обладал огромной физической силой
• Побеждал врагов умом и хитростью
• Отличный стрелок из лука

*Главные подвиги:*
1. Победа над Тугарином Змеевичем
2. Освобождение Забавы Путятичны
3. Помощь в обороне Киева

*Особенности:*
Алёша часто действовал не силой, а умом. Его история с женитьбой на Настасье Микулишне показывает как хитростью можно добиться того, что не под силу другим богатырям.

*Легенда:*
Согласно былинам, Алёша Попович погиб в знаменитой битве на Калке в 1223 году."""
    },
    {
        "title": "Добрыня Никитич",
        "content": """*Добрыня Никитич* — второй по значимости богатырь после Ильи Муромца, известный своей образованностью и дипломатичностью.

*Происхождение:*
Родился в Рязани, племянник князя Владимира. Обладал не только силой, но и образованностью: умел читать, писать, играть на гуслях.

*Основные подвиги:*
• Победа над Змеем Горынычем
• Освобождение Забавы Путятичны
• Дипломатические миссии
• Защита Киева от кочевников

*Особенности:*
Добрыня часто выступал в роли дипломата и советника князя. Его женитьба на Настасье Микулишне (дочери Микулы Селяниновича) стала одним из центральных сюжетов былин.

*Интересный факт:*
Добрыня считается прообразом воеводы Добрыни, дяди и воспитателя князя Владимира Святославича."""
    },
    {
        "title": "Святогор",
        "content": """*Святогор* — древнейший и могучий богатырь, олицетворение стихийных сил природы.

*Особенности:*
• Невероятная сила и рост
• Не мог жить среди людей
• Обитал в Святых горах
• Символизировал древнюю, дохристианскую эпоху

*Основной сюжет:*
Встреча с Ильёй Муромцем, когда Святогор пытается поднять суму перемётную, но не может, а Илья сдвигает её с места. Поражённый силой Ильи, Святогор передаёт ему часть своей силы перед смертью.

*Символическое значение:*
Святогор представляет древнюю, языческую Русь, уступающую место новой, христианской эпохе в лице Ильи Муромца.

*Легенда о смерти:*
Святогор погиб, пытаясь поднять гроб, который оказался ему предназначен."""
    },
    {
        "title": "Микула Селянинович",
        "content": """*Микула Селянинович* — богатырь-пахарь, олицетворение крестьянской силы и связи с землёй.

*Особенности:*
• Не воин, а земледелец
• Невероятная физическая сила
• Отец Настасьи Микулишны
• Символ народной, земной силы

*Знаменитый эпизод:*
Встреча с Вольгой Святославичем, когда княжеская дружина не может вытащить соху, которую Микула вонзил одной рукой.

*Символика:*
Микула представляет народную, земную силу, которая превосходит княжескую военную мощь. Его соха тяжелее всего княжеского оружия.

*Народная мудрость:*
«От труда земного богатырская сила рождается» — основной мотив былин о Микуле."""
    },
    {
        "title": "Баба-Яга",
        "content": """*Баба-Яга* — один из самых известных персонажей славянской мифологии, хозяйка леса и повелительница зверей.

*Внешность:*
• Костяная нога
• Длинный нос
• Летает в ступе
• Живёт в избушке на курьих ножках

*Двойственная природа:*
1. *Злая* — похищает детей, вредит людям
2. *Помощница* — даёт советы, волшебные предметы

*Особенности:*
• Хранительница границы между мирами
• Обладает магическими знаниями
• Может быть и врагом, и помощником

*Волшебные атрибуты:*
• Клубок, указывающий дорогу
• Ковёр-самолёт
• Сапоги-скороходы
• Шапка-невидимка

*Современное значение:*
Баба-Яга остаётся популярным персонажем в сказках, мультфильмах и современной культуре."""
    },
    {
        "title": "Кощей Бессмертный",
        "content": """*Кощей Бессмертный* — главный антагонист русских сказок, олицетворение смерти и темных сил.

*Происхождение имени:*
От слова «кость» — тощий, похожий на скелет. Также связывают с «кощун» — колдун, волшебник.

*Особенности:*
• Крайняя худоба
• Обладает несметными богатствами
• Бессмертен (смерть спрятана в яйце)
• Похищает красавиц

*Смерть Кощея:*
Находится на конце иглы, которая в яйце, яйцо в утке, утка в зайце, заяц в сундуке, сундук на дубе, дуб на острове.

*Символическое значение:*
• Олицетворение зла и смерти
• Испытание для героя
• Преодоление страха смерти

*В современной культуре:*
Часто появляется в фильмах, мультфильмах и литературе как архетипический злодей."""
    },
    {
        "title": "Змей Горыныч",
        "content": """*Змей Горыныч* — трёхглавый огнедышащий дракон, главный противник русских богатырей.

*Внешность:*
• Три (иногда шесть, девять или двенадцать) голов
• Огнедышащая пасть
• Крылья как у летучей мыши
• Чешуйчатое тело

*Особенности:*
• Летает по небу
• Изрыгает пламя
• Похищает людей
• Требует дань

*Знаменитые битвы:*
1. С Добрыней Никитичем (7 дней)
2. С Иваном-царевичем
3. С другими богатырями

*Символика:*
• Олицетворение вражеских нашествий
• Стихийные бедствия
• Тёмные, разрушительные силы

*Происхождение:*
Связан с древними мифами о драконах и змеях-искусителях. Возможно, отражает память о реальных набегах кочевников.

*В современности:*
Популярный персонаж игр, фильмов и мультфильмов."""
    }
]

def break_text_into_chunks(text_content: str, chunk_limit: int = 1900) -> List[str]:
    """
    Разбивает текст на части заданного размера.
    """
    fragments = []
    while len(text_content) > chunk_limit:
        split_position = text_content.rfind("\n", 0, chunk_limit)
        if split_position == -1:
            split_position = text_content.rfind(" ", 0, chunk_limit)
        if split_position == -1:
            split_position = chunk_limit
        fragments.append(text_content[:split_position].rstrip())
        text_content = text_content[split_position:].lstrip()
    if text_content:
        fragments.append(text_content)
    return fragments

def generate_navigation(article_idx: int, part_idx: int, total_articles: int, has_saved_position: bool, total_parts: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру навигации для чтения.
    """
    part_navigation = []
    if part_idx > 0:
        part_navigation.append(InlineKeyboardButton(
            text="◀️ Предыдущий фрагмент",
            callback_data=f"nav_prev_part_{article_idx}_{part_idx}"
        ))
    if part_idx + 1 < total_parts:
        part_navigation.append(InlineKeyboardButton(
            text="▶️ Следующий фрагмент",
            callback_data=f"nav_next_part_{article_idx}_{part_idx}"
        ))

    article_navigation = []
    if article_idx > 0:
        article_navigation.append(InlineKeyboardButton(
            text="⏪ Предыдущий персонаж",
            callback_data=f"nav_prev_article_{article_idx}"
        ))
    if article_idx + 1 < total_articles:
        article_navigation.append(InlineKeyboardButton(
            text="⏩ Следующий персонаж",
            callback_data=f"nav_next_article_{article_idx}"
        ))

    button_rows = []
    if part_navigation:
        button_rows.append(part_navigation)
    if article_navigation:
        button_rows.append(article_navigation)

    button_rows.append([InlineKeyboardButton(
        text="📍 Вернуться к метке" if has_saved_position else "🔖 Сохранить позицию",
        callback_data="reader_goto_marker" if has_saved_position else "reader_set_marker"
    )])

    return InlineKeyboardMarkup(inline_keyboard=button_rows)

async def display_wiki_entry(context_obj, user_identifier: int, article_idx: int, part_idx: int = 0):
    """
    Отображает статью с навигацией.
    """
    if article_idx < 0 or article_idx >= len(FANTASY_ARTICLES):
        status_msg = "📚 База знаний пуста."
        if isinstance(context_obj, Message):
            await context_obj.answer(status_msg, reply_markup=main_menu)
        else:
            await context_obj.message.edit_text(status_msg, reply_markup=main_menu)
        reader_sessions.pop(user_identifier, None)
        return

    wiki_entry = FANTASY_ARTICLES[article_idx]
    article_content = wiki_entry["content"]

    text_segments = break_text_into_chunks(article_content, 1900)
    if part_idx >= len(text_segments):
        part_idx = len(text_segments) - 1

    current_segment = text_segments[part_idx]
    segments_count = len(text_segments)

    safe_title = format_markdown(wiki_entry['title'])
    safe_content = format_markdown(current_segment)

    message_text = f"📖 *{safe_title}* \\| Фрагмент {part_idx + 1}/{segments_count}\n\n{safe_content}"

    has_saved_position = (
        reader_sessions.get(user_identifier, {}).get("saved_article") is not None and
        reader_sessions.get(user_identifier, {}).get("saved_part") is not None
    )

    navigation = generate_navigation(article_idx, part_idx, len(FANTASY_ARTICLES), has_saved_position, segments_count)

    if isinstance(context_obj, Message):
        await context_obj.answer(message_text, reply_markup=navigation, parse_mode="MarkdownV2")
    else:
        await context_obj.message.edit_text(message_text, reply_markup=navigation, parse_mode="MarkdownV2")
        await context_obj.answer()

@router.message(F.text == "📚 Читалка")
async def launch_reader(message: Message):
    """
    Запускает режим чтения.
    """
    user_identifier = message.from_user.id
    reader_sessions[user_identifier] = {
        "article_index": 0,
        "part_index": 0,
        "saved_article": None,
        "saved_part": None
    }
    await display_wiki_entry(message, user_identifier, 0, 0)

@router.callback_query(F.data.startswith("nav_next_part_"))
async def navigate_next_part(callback: CallbackQuery):
    """
    Переход к следующему фрагменту статьи.
    """
    try:
        _, _, _, article_idx, part_idx = callback.data.split("_")
        article_idx, part_idx = int(article_idx), int(part_idx)
        user_identifier = callback.from_user.id
        session_data = reader_sessions.get(user_identifier)

        if not session_data:
            return

        if part_idx + 1 < len(break_text_into_chunks(FANTASY_ARTICLES[article_idx]["content"], 1900)):
            session_data["part_index"] = part_idx + 1
            await display_wiki_entry(callback, user_identifier, article_idx, session_data["part_index"])
        else:
            await callback.answer("Достигнут конец статьи.", show_alert=True)
    except Exception as e:
        logging.error(f"Ошибка в navigate_next_part: {e}")
        await callback.answer("Произошла техническая ошибка.", show_alert=True)

@router.callback_query(F.data.startswith("nav_prev_part_"))
async def navigate_previous_part(callback: CallbackQuery):
    """
    Переход к предыдущему фрагменту статьи.
    """
    try:
        _, _, _, article_idx, part_idx = callback.data.split("_")
        article_idx, part_idx = int(article_idx), int(part_idx)
        user_identifier = callback.from_user.id
        session_data = reader_sessions.get(user_identifier)

        if not session_data:
            return

        if part_idx > 0:
            session_data["part_index"] = part_idx - 1
            await display_wiki_entry(callback, user_identifier, article_idx, session_data["part_index"])
        else:
            await callback.answer("Это начало статьи.", show_alert=True)
    except Exception as e:
        logging.error(f"Ошибка в navigate_previous_part: {e}")
        await callback.answer("Произошла техническая ошибка.", show_alert=True)

@router.callback_query(F.data.startswith("nav_next_article_"))
async def navigate_next_article(callback: CallbackQuery):
    """
    Переход к следующему персонажу.
    """
    try:
        _, _, _, article_idx = callback.data.split("_")
        article_idx = int(article_idx)
        user_identifier = callback.from_user.id
        session_data = reader_sessions.get(user_identifier)

        if not session_data:
            return

        if article_idx + 1 < len(FANTASY_ARTICLES):
            session_data["article_index"] = article_idx + 1
            session_data["part_index"] = 0
            await display_wiki_entry(callback, user_identifier, session_data["article_index"], 0)
        else:
            await callback.answer("Это последний персонаж в коллекции.", show_alert=True)
    except Exception as e:
        logging.error(f"Ошибка в navigate_next_article: {e}")
        await callback.answer("Произошла техническая ошибка.", show_alert=True)

@router.callback_query(F.data.startswith("nav_prev_article_"))
async def navigate_previous_article(callback: CallbackQuery):
    """
    Переход к предыдущему персонажу.
    """
    try:
        _, _, _, article_idx = callback.data.split("_")
        article_idx = int(article_idx)
        user_identifier = callback.from_user.id
        session_data = reader_sessions.get(user_identifier)

        if not session_data:
            return

        if article_idx > 0:
            session_data["article_index"] = article_idx - 1
            session_data["part_index"] = 0
            await display_wiki_entry(callback, user_identifier, session_data["article_index"], 0)
        else:
            await callback.answer("Это первый персонаж в коллекции.", show_alert=True)
    except Exception as e:
        logging.error(f"Ошибка в navigate_previous_article: {e}")
        await callback.answer("Произошла техническая ошибка.", show_alert=True)

@router.callback_query(F.data == "reader_set_marker")
async def save_reading_position(callback: CallbackQuery):
    """
    Сохраняет текущую позицию чтения.
    """
    user_identifier = callback.from_user.id
    session_data = reader_sessions.get(user_identifier)

    if session_data is not None:
        session_data["saved_article"] = session_data["article_index"]
        session_data["saved_part"] = session_data["part_index"]
        await callback.answer("📍 Позиция сохранена!", show_alert=True)

@router.callback_query(F.data == "reader_goto_marker")
async def restore_reading_position(callback: CallbackQuery):
    """
    Возвращает к сохраненной позиции чтения.
    """
    user_identifier = callback.from_user.id
    session_data = reader_sessions.get(user_identifier)

    if session_data and session_data["saved_article"] is not None and session_data["saved_part"] is not None:
        session_data["article_index"] = session_data["saved_article"]
        session_data["part_index"] = session_data["saved_part"]
        await display_wiki_entry(callback, user_identifier, session_data["article_index"], session_data["part_index"])
    else:
        await callback.answer("Нет сохраненной позиции.", show_alert=True)

@router.message(F.text == "◀️ К активности")
async def exit_to_activities_menu(message: Message):
    """
    Возврат к выбору активностей.
    """
    user_identifier = message.from_user.id
    reader_sessions.pop(user_identifier, None)  # Очищаем сессию чтения
    await message.answer(
        "Выберите активность:",
        reply_markup=activities_menu
    )

@router.message(F.text == "◀️ Основное меню")
async def exit_to_main_menu(message: Message):
    """
    Возврат в главное меню.
    """
    user_identifier = message.from_user.id
    reader_sessions.pop(user_identifier, None)  # Очищаем сессию чтения
    await message.answer(
        "Основное меню:",
        reply_markup=main_menu
    )