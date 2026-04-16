# =============================================================================
# Telegram-бот «Путеводитель по сакральным местам Павлодарской области»
# aiogram 3.x | современные функции | inline-режим | веб-приложение | статистика
# Автор проекта: Маулет Адижан, 3«Ж», СОШ №29
# =============================================================================

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InputMediaPhoto,
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
)

# ── КОНФИГ ────────────────────────────────────────────────────────────────────
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")

PHOTOS_DIR = Path("photos")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# ── СТАТИСТИКА ────────────────────────────────────────────────────────────────
user_stats: Dict[int, Dict] = {}
favorites: Dict[int, Set[str]] = {}
search_history: Dict[int, List[str]] = {}

# ── ДАННЫЕ ОБ ОБЪЕКТАХ ────────────────────────────────────────────────────────
OBJECTS = {
    "akkelln": {
        "name": "🏛 Комплекс Аккелин (Муса Шорманов)",
        "district": "Баянаульский район, с. Тендик",
        "info": (
            "🏛 <b>Историко-мемориальный комплекс Аккелин</b>\n"
            "<b>Усадьба и мавзолей Мусы Шорманова</b>\n\n"
            "📍 <i>с. Тендик, Баянаульский район, Павлодарская область</i>\n\n"
            "<b>Муса Шорманов (1818–1884)</b> — глава Баянаульского внешнего округа, "
            "государственный деятель, этнограф, фольклорист и просветитель. Он оставил "
            "заметный след в истории изучения культуры казахов Среднего жуза, был дядей "
            "и духовным наставником первого казахского учёного <b>Шокана Валиханова</b>.\n\n"
            "Благодаря его просветительской деятельности открылись первые казахские школы. "
            "В 1881 году на Всероссийской ярмарке в Москве были представлены экспонаты "
            "казахского прикладного искусства, переданные Мусой Шормановым.\n\n"
            "🕌 <b>О мавзолее:</b>\n"
            "Мавзолей из белого камня возведён в <b>2018 году</b> на берегу реки Ащису. "
            "Строители из Мангыстауской области работали три месяца. "
            "Высота — <b>9 метров</b>, площадь — <b>500 кв. м</b>. "
            "Верхняя часть выполнена в форме <b>короны</b> — символ sultanского рода. "
            "Две тонны ракушек для строительства привезли из Актау. "
            "В ходе раскопок обнаружены останки <b>26 человек</b>."
        ),
        "photos": ["мш1.jpg", "мш2.jpg"],
        "maps_url": "https://www.google.com/maps/place/50.6326025,74.7682104",
        "maps_label": "📍 Открыть на карте",
    },
    "mashkur": {
        "name": "📚 Мавзолей Машхур Жусуп Копеева",
        "district": "Баянаульский район",
        "info": (
            "📚 <b>Мавзолей Машхур Жусуп Копеева</b>\n\n"
            "📍 <i>Баянаульский район, Павлодарская область</i>\n\n"
            "<b>Машхур Жусуп Копеев</b> — учёный, фольклорист, историк, философ и поэт. "
            "Имя «Машхур» (с арабского — <i>«знаменитый»</i>) ему дал Муса Шорманов, "
            "поражённый способностями девятилетнего Жусупа. Копеев оставил наследие "
            "объёмом <b>30 томов</b>. В 1989 году шежире нескольких родов вышло тиражом "
            "30 000 экземпляров и было раскуплено за несколько недель.\n\n"
            "Как провидец, Машхур Жусуп знал дату своей смерти: в 1930 году он созвал "
            "поминальный ас по себе, объявив, что проживёт ровно 73 года. Спустя 20 лет "
            "после смерти его тело оставалось <b>нетленным</b>. Мазар снесли в <b>1952 году</b>, "
            "восстановили в 1978-м, а нынешний мавзолей возведён в <b>2006 году</b>.\n\n"
            "🕌 <b>Особенности мавзолея:</b>\n"
            "• Входная дверь — с <b>северной</b> стороны (личное пожелание Копеева)\n"
            "• Сочетает <b>древнетюркские и исламские</b> архитектурные традиции\n"
            "• Внутри — гранитные камни с именами <b>семи предков</b>\n"
            "• Гранитное надгробие весит <b>9 тонн</b>\n"
            "• Вниз ведут <b>73 ступеньки</b> — по числу прожитых лет"
        ),
        "photos": ["мж1.jpg", "мж2.jpg", "мж3.jpg", "мж4.jpg"],
        "maps_url": "https://www.google.com/maps/place/51.1374791,74.9392722",
        "maps_label": "📍 Открыть на карте",
    },
    "konyр": {
        "name": "🏔 Пещера Коныр-Аулие",
        "district": "Баянаульский район",
        "info": (
            "🏔 <b>Пещера Коныр-Аулие (Аулиетас)</b>\n\n"
            "📍 <i>Баянаульский район, Павлодарская область</i>\n\n"
            "Ещё в середине XVIII века молва о пещере, в которую казахи «ходят купаться "
            "и верят, якобы через то купание вылечиваются от разных болезней», достигла "
            "<b>П. И. Рычкова</b> — первого члена-корреспондента Императорской Академии Наук. "
            "Упоминания встречаются в трудах <b>Шокана Валиханова</b> и <b>Григория Потанина</b>.\n\n"
            "Путевые заметки Н. Коншина описывают: <i>«Пещера находится выше чем на середине "
            "горы и кажется издали какой-то чёрной дырой. Вход в пещеру значительно выше "
            "роста человека, имеет треугольную форму».</i>\n\n"
            "🗺 <b>О пещере сегодня:</b>\n"
            "• Зал длиной около <b>30 м</b>, переходящий в узкий коридор\n"
            "• Подъём оборудован лестницами длиной <b>110 метров</b>\n"
            "• Информационные щиты, дорожные указатели\n"
            "• Развитая инфраструктура для паломников и туристов\n\n"
            "К пещере ездят молиться больные, бездетные женщины и паломники — "
            "традиция, не прерывающаяся несколько столетий."
        ),
        "photos": ["коныр1.jpg", "коныр2.jpg", "коныр3.jpg", "коныр4.jpg"],
        "maps_url": "https://www.google.com/maps/place/50.8086314,75.5098587",
        "maps_label": "📍 Открыть на карте",
    },
    "zhasyb": {
        "name": "⚔️ Могила Жасыбай батыра",
        "district": "Баянаульский район",
        "info": (
            "⚔️ <b>Могила Жасыбай батыра</b>\n\n"
            "📍 <i>Баянаульский район, старый перевал у дороги к озеру Жасыбай</i>\n\n"
            "<b>Жасыбай батыр Омирулы</b> — легендарный казахский батыр, защитник Родины, "
            "сражавшийся против джунгар. Из рода аргын, племени басентиин. "
            "Племянник знаменитого батыра <b>Олжабая</b>.\n\n"
            "В конце 30-х — начале 40-х гг. XVIII в. отряды казахов во главе с Жасыбаем "
            "вытесняли джунгар с Баянаульских гор. Батыр пал от стрелы врага. "
            "Час возмездия настал в местечке <b>«Сериктас»</b> — казахское ополчение "
            "под командованием Олжабай батыра нанесло врагу сокрушительное поражение. "
            "Эта местность получила название <b>«Қалмаққырған»</b> — "
            "«место истребления калмыков».\n\n"
            "Тело батыра предали земле у берегов Шойындыколь — с тех пор "
            "это озеро зовётся <b>Жасыбай</b>.\n\n"
            "🪨 Могила представляет собой каменную насыпь и памятник, "
            "установленный потомками в <b>2005 году</b>."
        ),
        "photos": ["жас1.jpg", "жас2.jpg", "жас3.jpg", "жас 4.jpg"],
        "maps_url": "https://www.google.com/maps/place/50.8004646,75.6253325",
        "maps_label": "📍 Открыть на карте",
    },
    "aulie": {
        "name": "🏺 Археологический комплекс Аулиеколь",
        "district": "Экибастузский регион",
        "info": (
            "🏺 <b>Археологический комплекс Аулиеколь</b>\n\n"
            "📍 <i>60 км северо-западнее г. Экибастуз, Павлодарская область</i>\n\n"
            "Открыт павлодарскими археологами на берегу озера Аулиеколь. "
            "Некрополь <b>XIV–XV вв.</b> возник в период расцвета Золотой Орды "
            "и функционировал до образования Казахского ханства.\n\n"
            "⛩ <b>Первый мавзолей-кумбез (19×12 м):</b>\n"
            "• <i>Зиаратхана</i> — восьмигранный зал под куполом для молитв и поминовения\n"
            "• <i>Гурхана</i> — усыпальница кочевой элиты\n"
            "• Стены украшены терракотовыми плитками с <b>арабской вязью</b> "
            "и геометрическим орнаментом\n\n"
            "💎 <b>Уникальные находки:</b>\n"
            "• Свёрток дорогой ткани с золотой вышивкой — изображения оленя, цветов, "
            "символов веры и надпись <i>«Ас-Султан ал-Гадыл»</i> (Султан справедливый)\n"
            "• Десятки <b>серебряных монет</b> ханов Золотой Орды\n"
            "• Купол второго мавзолея покрыт <b>голубой глазурью</b>"
        ),
        "photos": ["аулиеколь1.jpg", "аулиеколь2.jpg", "аулиеколь3.jpg", "аулиеколь4.jpg"],
        "maps_url": "https://www.google.com/maps/search/52.3683344,64.111533",
        "maps_label": "📍 Открыть на карте",
    },
    "isabeк": {
        "name": "🕌 Мавзолей Исабек ишан хазрета",
        "district": "Экибастузский регион",
        "info": (
            "🕌 <b>Мавзолей Исабек ишан хазрета</b>\n\n"
            "📍 <i>Экибастузский регион, Павлодарская область</i>\n\n"
            "<b>Исабек ишан хазрет</b> — известный духовно-религиозный деятель. "
            "Родился во второй половине XVIII в. в урочище <b>Шакшан</b>, "
            "в предгорьях Баянаула. Происходит из рода кожа, "
            "потомок Акку ишана, сын Мурат ишана.\n\n"
            "С семи лет обучался в медресе <b>г. Бухары</b>. "
            "По возвращении в Прииртышье в местности <b>Акколь-Жайильма</b> "
            "построил мечеть и открыл медресе. Посвятил жизнь религиозному "
            "просвещению и распространению ислама.\n\n"
            "До сих пор ходят легенды о <b>чудесных исцелениях</b> больных "
            "различными недугами.\n\n"
            "🕍 В <b>2011 году</b> над захоронением хазрета возведены "
            "каменные мавзолеи, построена мечеть и дом для паломников. "
            "У стен — стелы с фрагментами <b>жоктау</b>, посвящённого "
            "Исабек ишану Машхур Жусупом Копеевым."
        ),
        "photos": ["хаз1.jpg", "хаз2.jpg", "хаз 3.jpg", "хаз4.jpg"],
        "maps_url": "https://www.google.com/maps/place/52.2544484,74.9255673",
        "maps_label": "📍 Открыть на карте",
    },
    "sultan": {
        "name": "👑 Усадьба Султанбет султана",
        "district": "г. Павлодар",
        "info": (
            "👑 <b>Усадьба Султанбет султана</b>\n\n"
            "📍 <i>Исторический центр г. Павлодар</i>\n\n"
            "<b>Султанбет султан</b> — выдающийся казахский государственный деятель XVIII в., "
            "один из сподвижников и двоюродный брат <b>Абылай хана</b>. "
            "Многолетний правитель улуса Среднего Жуза, основная территория которого "
            "соответствует современной Павлодарской области. "
            "Сыграл важную роль в укреплении казахской государственности "
            "в восточных и северо-восточных землях.\n\n"
            "🏗 <b>О реконструкции:</b>\n"
            "Восстановление усадьбы инициировано в <b>2017 году</b> ректором ПГПУ "
            "<b>А. Нухулы</b>. Коллектив университета и потомки султана "
            "воссоздали резиденцию по архивным описаниям и чертежам.\n\n"
            "🚪 Сегодня усадьба <b>открыта для всех</b> жителей и гостей Павлодара."
        ),
        "photos": ["СС1.jpg", "СС2.jpg"],
        "maps_url": "https://www.google.com/maps/place/52.2761619,76.9402393",
        "maps_label": "📍 Открыть на карте",
    },
}

# ── КЛАВИАТУРЫ ────────────────────────────────────────────────────────────────
def main_menu_kb(user_id: int = None) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=data["name"], callback_data=f"obj:{key}")]
        for key, data in OBJECTS.items()
    ]
    buttons.append([
        InlineKeyboardButton(text="⭐️ Избранное", callback_data="favorites"),
        InlineKeyboardButton(text="🔍 Поиск", callback_data="search")
    ])
    buttons.append([
        InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
        InlineKeyboardButton(text="ℹ️ О проекте", callback_data="about")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def object_kb(key: str, user_id: int = None) -> InlineKeyboardMarkup:
    obj = OBJECTS[key]
    is_favorite = user_id and key in favorites.get(user_id, set())
    fav_text = "💔 Убрать из избранного" if is_favorite else "❤️ В избранное"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=obj["maps_label"], url=obj["maps_url"])],
        [InlineKeyboardButton(text=fav_text, callback_data=f"fav:{key}")],
        [InlineKeyboardButton(text="📤 Поделиться", switch_inline_query=key)],
        [InlineKeyboardButton(text="◀️ К списку объектов", callback_data="menu")],
    ])


def after_photos_kb(key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад к объекту", callback_data=f"obj:{key}")],
        [InlineKeyboardButton(text="🏠 Главное меню",    callback_data="menu")],
    ])


def about_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")],
    ])

# ── ХЭНДЛЕРЫ ──────────────────────────────────────────────────────────────────

def track_user_action(user_id: int, action: str, object_key: str = None) -> None:
    """Отслеживание действий пользователя"""
    if user_id not in user_stats:
        user_stats[user_id] = {
            "first_visit": datetime.now(),
            "last_visit": datetime.now(),
            "views": {},
            "total_actions": 0
        }

    user_stats[user_id]["last_visit"] = datetime.now()
    user_stats[user_id]["total_actions"] += 1

    if object_key:
        if object_key not in user_stats[user_id]["views"]:
            user_stats[user_id]["views"][object_key] = 0
        user_stats[user_id]["views"][object_key] += 1


async def cmd_start(message: Message) -> None:
    user_id = message.from_user.id
    track_user_action(user_id, "start")

    await message.answer(
        "🇰🇿 <b>Сакральный Павлодар</b>\n"
        "<i>Путеводитель по сакральным местам Павлодарской области</i>\n\n"
        "В рамках программы <b>«Рухани жаңғыру»</b> собраны материалы "
        "о семи объектах республиканского значения.\n\n"
        "✨ <b>Новые возможности:</b>\n"
        "• ⭐️ Добавляйте объекты в избранное\n"
        "• 🔍 Поиск по названию и описанию\n"
        "• 📤 Делитесь объектами через inline-режим\n"
        "• 📊 Смотрите свою статистику просмотров\n\n"
        "Выбери объект, чтобы узнать его историю 👇",
        reply_markup=main_menu_kb(user_id),
        parse_mode=ParseMode.HTML,
    )


async def cmd_help(message: Message) -> None:
    await message.answer(
        "📖 <b>Команды бота:</b>\n\n"
        "/start — главное меню\n"
        "/help — эта справка\n"
        "/search — поиск объектов\n"
        "/favorites — избранные объекты\n"
        "/stats — ваша статистика\n\n"
        "<b>Inline-режим:</b>\n"
        "Напишите <code>@your_bot_name</code> в любом чате, "
        "чтобы поделиться информацией об объектах.\n\n"
        "Нажми на любой объект в меню, чтобы узнать его историю, "
        "посмотреть фото и открыть на карте.",
        parse_mode=ParseMode.HTML,
    )


async def cb_menu(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    await callback.message.edit_text(
        "🇰🇿 <b>Сакральный Павлодар</b>\n\n"
        "Выбери объект 👇",
        reply_markup=main_menu_kb(user_id),
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


async def cb_search(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "🔍 <b>Поиск объектов</b>\n\n"
        "Введите название объекта или ключевое слово для поиска.\n"
        "Например: <code>Машхур</code>, <code>пещера</code>, <code>мавзолей</code>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="menu")]
        ]),
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


async def cb_favorites(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    user_favs = favorites.get(user_id, set())

    if not user_favs:
        await callback.message.edit_text(
            "⭐️ <b>Избранное пусто</b>\n\n"
            "Добавьте объекты в избранное, нажав ❤️ на странице объекта.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ Назад", callback_data="menu")]
            ]),
            parse_mode=ParseMode.HTML,
        )
    else:
        buttons = [
            [InlineKeyboardButton(text=OBJECTS[key]["name"], callback_data=f"obj:{key}")]
            for key in user_favs if key in OBJECTS
        ]
        buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="menu")])

        await callback.message.edit_text(
            f"⭐️ <b>Избранное ({len(user_favs)})</b>\n\n"
            "Ваши сохранённые объекты:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
            parse_mode=ParseMode.HTML,
        )
    await callback.answer()


async def cb_stats(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    stats = user_stats.get(user_id, {})

    if not stats:
        text = "📊 <b>Статистика</b>\n\nДанных пока нет."
    else:
        first_visit = stats.get("first_visit", datetime.now())
        last_visit = stats.get("last_visit", datetime.now())
        total_actions = stats.get("total_actions", 0)
        views = stats.get("views", {})

        text = (
            f"📊 <b>Ваша статистика</b>\n\n"
            f"👤 Первый визит: {first_visit.strftime('%d.%m.%Y %H:%M')}\n"
            f"🕐 Последний визит: {last_visit.strftime('%d.%m.%Y %H:%M')}\n"
            f"🎯 Всего действий: {total_actions}\n"
            f"⭐️ В избранном: {len(favorites.get(user_id, set()))}\n\n"
        )

        if views:
            text += "<b>Просмотренные объекты:</b>\n"
            sorted_views = sorted(views.items(), key=lambda x: x[1], reverse=True)
            for key, count in sorted_views[:5]:
                obj_name = OBJECTS[key]["name"].split(" ", 1)[1] if key in OBJECTS else key
                text += f"• {obj_name}: {count} раз\n"

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="menu")]
        ]),
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


async def cb_favorite_toggle(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    key = callback.data.split(":", 1)[1]

    if user_id not in favorites:
        favorites[user_id] = set()

    if key in favorites[user_id]:
        favorites[user_id].remove(key)
        await callback.answer("💔 Удалено из избранного", show_alert=False)
    else:
        favorites[user_id].add(key)
        await callback.answer("❤️ Добавлено в избранное!", show_alert=False)

    obj = OBJECTS[key]
    await callback.message.edit_reply_markup(reply_markup=object_kb(key, user_id))


async def cb_about(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "ℹ️ <b>О проекте</b>\n\n"
        "Telegram-бот <b>«Путеводитель по сакральным местам Павлодарской области»</b> "
        "разработан в рамках школьного проекта.\n\n"
        "👦 <b>Автор:</b> Маулет Адижан\n"
        "🏫 <b>Школа:</b> СОШ №29, 3 «Ж» класс\n\n"
        "Бот позволяет в короткие сроки получить информацию "
        "об исторических объектах с фотографиями и ссылками на карту.\n\n"
        "🗺 В Павлодарской области насчитывается <b>7 объектов</b> "
        "республиканского значения и более <b>36 памятников</b> "
        "регионального уровня в рамках программы «Рухани жаңғыру».",
        reply_markup=about_kb(),
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


async def cb_object(callback: CallbackQuery) -> None:
    key = callback.data.split(":", 1)[1]
    user_id = callback.from_user.id
    track_user_action(user_id, "view_object", key)

    obj = OBJECTS[key]
    await callback.answer("Загружаю информацию…")

    # Отправляем фотографии
    media = []
    for i, filename in enumerate(obj["photos"]):
        path = PHOTOS_DIR / filename
        if not path.exists():
            log.warning(f"Файл не найден: {path}")
            continue

        # К первому фото добавляем полное описание
        if i == 0:
            media.append(InputMediaPhoto(
                media=FSInputFile(path),
                caption=obj["info"],
                parse_mode=ParseMode.HTML,
            ))
        else:
            media.append(InputMediaPhoto(media=FSInputFile(path)))

    if media:
        # Удаляем старое сообщение
        try:
            await callback.message.delete()
        except:
            pass

        # Отправляем фото с описанием
        await callback.message.answer_media_group(media)

        # Отправляем кнопки управления
        await callback.message.answer(
            "Выберите действие:",
            reply_markup=object_kb(key, user_id),
        )
    else:
        # Если фото не найдены, показываем только текст
        await callback.message.edit_text(
            obj["info"] + "\n\n⚠️ Фотографии не найдены.",
            reply_markup=object_kb(key, user_id),
            parse_mode=ParseMode.HTML,
        )


async def cb_photos(callback: CallbackQuery) -> None:
    key = callback.data.split(":", 1)[1]
    user_id = callback.from_user.id
    track_user_action(user_id, "view_photos", key)

    obj = OBJECTS[key]
    await callback.answer("Загружаю фотографии…")

    media = []
    for i, filename in enumerate(obj["photos"]):
        path = PHOTOS_DIR / filename
        if not path.exists():
            log.warning(f"Файл не найден: {path}")
            continue
        media.append(InputMediaPhoto(
            media=FSInputFile(path),
            caption=f"📸 {obj['name']}\n📍 {obj['district']}" if i == 0 else None,
            parse_mode=ParseMode.HTML,
        ))

    if media:
        await callback.message.answer_media_group(media)
    else:
        await callback.message.answer(
            "⚠️ Фотографии не найдены.\n"
            "Убедитесь, что папка <code>photos/</code> находится рядом с <code>bot.py</code>.",
            parse_mode=ParseMode.HTML,
        )

    await callback.message.answer(
        "Что дальше?",
        reply_markup=after_photos_kb(key),
    )


async def handle_search(message: Message) -> None:
    """Обработка поискового запроса"""
    query = message.text.lower().strip()
    user_id = message.from_user.id

    if user_id not in search_history:
        search_history[user_id] = []
    search_history[user_id].append(query)

    results = []
    for key, obj in OBJECTS.items():
        if (query in obj["name"].lower() or
            query in obj["info"].lower() or
            query in obj["district"].lower()):
            results.append((key, obj))

    if not results:
        await message.answer(
            f"🔍 По запросу <b>«{message.text}»</b> ничего не найдено.\n\n"
            "Попробуйте другие ключевые слова.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")]
            ]),
            parse_mode=ParseMode.HTML,
        )
    else:
        buttons = [
            [InlineKeyboardButton(text=obj["name"], callback_data=f"obj:{key}")]
            for key, obj in results
        ]
        buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")])

        await message.answer(
            f"🔍 Найдено объектов: <b>{len(results)}</b>\n\n"
            f"По запросу: <b>«{message.text}»</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
            parse_mode=ParseMode.HTML,
        )


async def inline_query_handler(inline_query: InlineQuery) -> None:
    """Обработка inline-запросов для sharing"""
    query = inline_query.query.lower().strip()
    results = []

    items = OBJECTS.items()
    if query:
        items = [(k, v) for k, v in items if query in v["name"].lower() or query in k]

    for key, obj in list(items)[:10]:
        results.append(
            InlineQueryResultArticle(
                id=key,
                title=obj["name"],
                description=obj["district"],
                input_message_content=InputTextMessageContent(
                    message_text=f"{obj['info']}\n\n📍 {obj['maps_label']}: {obj['maps_url']}",
                    parse_mode=ParseMode.HTML,
                ),
                thumbnail_url="https://via.placeholder.com/150",
            )
        )

    await inline_query.answer(results, cache_time=300)

# ── ЗАПУСК ────────────────────────────────────────────────────────────────────
async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Команды
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command("help"))

    # Callback-кнопки
    dp.callback_query.register(cb_menu, F.data == "menu")
    dp.callback_query.register(cb_about, F.data == "about")
    dp.callback_query.register(cb_search, F.data == "search")
    dp.callback_query.register(cb_favorites, F.data == "favorites")
    dp.callback_query.register(cb_stats, F.data == "stats")
    dp.callback_query.register(cb_object, F.data.startswith("obj:"))
    dp.callback_query.register(cb_photos, F.data.startswith("photos:"))
    dp.callback_query.register(cb_favorite_toggle, F.data.startswith("fav:"))

    # Inline-режим
    dp.inline_query.register(inline_query_handler)

    # Обработка текстовых сообщений (поиск)
    dp.message.register(handle_search, F.text & ~F.text.startswith("/"))

    log.info("🚀 Бот запущен с новыми функциями!")
    log.info("✨ Доступны: inline-режим, избранное, поиск, статистика")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())