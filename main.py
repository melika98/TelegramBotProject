import telebot
from telebot import types
import pandas as pd


API_KEY = "1740393250:AAGlNHCvNcK8Xz6ztolXME40mrcBgl9omp4"
list_of_actions = ['مشخصات من', 'لیست محصولات', 'کیف پول من', 'افزایش موجودی کیف پول', 'خرید', 'ارتباط با ما', 'انتخاب محصول', 'مشاهده سبد خرید', 'اصلاح سبد خرید', 'تایید سبد خرید', 'فاکتور', 'بازگشت']

product_path         = './products_phone.xlsx'
discount_path        = './discounts.xlsx'
users_info_path      = './users.xlsx'



my_basket = {"who": [], "what": []}
choose_basket_tracker = False
product_data_frame = None
last_factor = None
confirm_factor = False

increase_wallet_tracker = False
buy_product_tracker = False


# dataframe
def read_user_info():
    users_info      = pd.read_excel(users_info_path,engine='openpyxl')
    return users_info

def write_user_info(df):
    df.to_excel(users_info_path, index=False)


def read_product_info():
    users_info      = pd.read_excel(product_path,engine='openpyxl')
    return users_info

def write_product_info(df):
    df.to_excel(product_path, index=False)


def read_discount_info():
    users_info      = pd.read_excel(discount_path,engine='openpyxl')
    return users_info

def write_discount_info(df):
    df.to_excel(discount_path, index=False)


bot = telebot.TeleBot(token=API_KEY) # make a connection between telegram and python using the api key or password



markup_main = types.ReplyKeyboardMarkup()
itembtn1 = types.KeyboardButton('مشخصات من')
itembtn2 = types.KeyboardButton('لیست محصولات')
itembtn3 = types.KeyboardButton('کیف پول من')
itembtn4 = types.KeyboardButton('افزایش موجودی کیف پول')
itembtn5 = types.KeyboardButton('خرید')
itembtn6 = types.KeyboardButton('ارتباط با ما')
markup_main.row(itembtn1, itembtn2, itembtn3) # row 1 -> 3 bottuns
markup_main.row(itembtn4, itembtn5, itembtn6) # row 2 -> 2

markup_purchase = types.ReplyKeyboardMarkup()
itembtn1 = types.KeyboardButton('انتخاب محصول')
itembtn2 = types.KeyboardButton('مشاهده سبد خرید')
itembtn4 = types.KeyboardButton('اصلاح سبد خرید')
itembtn3 = types.KeyboardButton('تایید سبد خرید')
itembtn5 = types.KeyboardButton('فاکتور')
itembtn6 = types.KeyboardButton('بازگشت')
markup_purchase.row(itembtn1, itembtn2, itembtn3)
markup_purchase.row(itembtn4, itembtn5, itembtn6)




@bot.message_handler(commands=['شروع', 'راهنما', 'start'])
def send_welcome(message):
    # print(message.from_user.username)
    bot.send_message(message.chat.id, "سلام. به روبات خرید تلفن همراه خوش آمدید. لطفا گزینه مورد نظر را انتخاب کنید:", reply_markup=markup_main)
    users_info = read_user_info()
    # print(users_info)
    if message.from_user.username not in users_info.name.tolist():
        new_row = {"name": message.from_user.username, "balance": int(0), "nob": int(0)}
        # print(new_row)
        users_info = users_info.append(new_row, ignore_index=True)
        write_user_info(users_info)



@bot.message_handler(regexp=r"^[0-9]+T$")
def add_money(message):
    global increase_wallet_tracker
    if increase_wallet_tracker is False:
        bot.reply_to(message, "دستور مورد نظر یافت نشد. به منظور افزایش موجودی ابتدا بر روی گزینه (افزایش موجودی کیف پول) کلیک کنید و سپس مبلغ مورد نظر را انتخاب کنید.")
    else:

        added_value = int(message.text.replace("T", ""))
        if added_value < 5000:
            bot.reply_to(message, "مبلغ وارد شده کمتر از ۵۰۰۰ تومان می‌باشد. لطفا مبلغ انتخابی را بالای ۵۰۰۰ تومان وارد کنید.")

        username = message.from_user.username
        users_info = read_user_info()

        index = users_info.index[users_info.name == username].tolist()[0]

        old_value = users_info.at[index, "balance"]
        users_info.at[index, "balance"] += added_value

        user_info  = users_info.loc[users_info.name == username]
        results = ''
        results += 'کاربر گرامی '
        results += f"{user_info.name.tolist()[0]}"
        results += ' موجودی حساب شما از '
        results += f'{old_value}'
        results += ' تومان به '
        results += f'{user_info.balance.tolist()[0]}'
        results += ' تومان تغییر کرد.'

        write_user_info(users_info)
        bot.reply_to(message, results)
        increase_wallet_tracker = False


@bot.message_handler(regexp=r"^مشخصات من$")
def my_info(message):
    username = message.from_user.username
    users_info = read_user_info()
    # print(users_info)
    user_info  = users_info.loc[users_info.name == username]
    results = ''
    results += 'کاربر گرامی '
    results += f"{user_info.name.tolist()[0]}"
    results += ' موجودی حساب شما '
    results += f'{user_info.balance.tolist()[0]}'
    results += ' است.'
    bot.reply_to(message, results)



def product_info(message):
    df = read_product_info()
    available_index = []
    results = ""
    results += "لیست محصولات:\n\n"
    for index, row in df.iterrows():
        if row['تعداد'] == 0:
            continue

        available_index.append(index)
        results += f"محصول شماره {index + 1}\n"
        results += "نام محصول: "
        results += f"{row['نام محصول']}\n"

        results += "قیمت: "
        results += f"{row['قیمت']}"
        results += " تومان\n"

        results += "تعداد: "
        results += f"{row['تعداد']}\n"

        results += "برند: "
        results += f"{row['برند']}\n"

        results += "\n\n"
        # print(row['نام محصول'], row['قیمت'], row['تعداد'], row['برند'])
    return results, df, available_index

@bot.message_handler(regexp=r"^لیست محصولات$")
def list_of_product(message):
    results, df, available_index = product_info(message)
    bot.reply_to(message, results)


@bot.message_handler(regexp=r"^کیف پول من$")
def my_wallet(message):
    username = message.from_user.username
    users_info = read_user_info()
    user_info  = users_info.loc[users_info.name == username]
    results = ''
    results += 'کاربر گرامی '
    results += f"{user_info.name.tolist()[0]}"
    results += ' موجودی حساب شما '
    results += f'{user_info.balance.tolist()[0]}'
    results += ' است. به منظور افزایش موجودی حساب خود بر روی گزینه افزایش موجودی کیف پول کلیک کنید.'
    bot.reply_to(message, results)

@bot.message_handler(regexp=r"^افزایش موجودی کیف پول$")
def increase_my_wallet(message):
    username = message.from_user.username
    results = ''
    results += 'کاربر گرامی، لطفا فقط (عدد) مبلغ مورد نظر خود را به فرمت زیر وارد نمایید:'
    results += '\n\n5000T\n\n'
    results += 'که معادل ۵۰۰۰ تومان می‌باشد.'
    global increase_wallet_tracker
    increase_wallet_tracker = True
    bot.reply_to(message, results)



@bot.message_handler(regexp=r"^خرید$")
def purchase_menu(message):
    results = ""
    results += "کاربر گرامی، به قسمت خرید خوش آمدید. لطفا از بین گزینه‌های موجود انتخاب کنید:"
    bot.send_message(message.chat.id, results, reply_markup=markup_purchase)


@bot.message_handler(regexp=r"^انتخاب محصول$")
def choose_item(message):
    results = ""
    # results += list_of_product(message)[0]
    results += "کاربر گرامی لطفا، شماره محصول یا محصولات مورد نظر خود را به فرمت:\n"
    results += "2\n"
    results += "2 3 5\n"
    results += "وارد کنید. دقت شود که بین شماره محصولات حتما فاصله (یا اسپیس) وارد شود:"
    bot.send_message(message.chat.id, results, reply_markup=markup_purchase)



@bot.message_handler(regexp=r"^مشاهده سبد خرید$")
def show_my_basket(message):
    username = message.from_user.username

    global buy_product_tracker, my_basket, product_data_frame
    if buy_product_tracker:
        my_basket, product_data_frame
        log = "سبد خرید شما:\n\n"

        for index, pi in enumerate(my_basket["what"]):
            log += f"محصول شماره {pi + 1}\n"
            log += "نام محصول: "
            log += f"{product_data_frame.at[pi, product_data_frame.columns[0]]}\n"

            log += "قیمت: "
            log += f"{product_data_frame.at[pi, product_data_frame.columns[1]]}"
            log += " تومان\n"

            log += "برند: "
            log += f"{product_data_frame.at[pi, product_data_frame.columns[-1]]}\n"

            log += "\n\n"

        log += "در صورت تمایل به اصلاح/تایید محصولات مورد نظر اقدام کنید."
    else:
        log = "کاربر گرامی، لیست خرید شما خالی است. لطفا اقدام به انتخاب محصول کنید.\n\n"
    bot.send_message(message.chat.id, log, reply_markup=markup_purchase)

@bot.message_handler(regexp=r"^تایید سبد خرید$")
def finalize_my_basket(message):
    username = message.from_user.username
    discount_info = read_discount_info()

    global buy_product_tracker, my_basket, product_data_frame, confirm_factor, last_factor, choose_basket_tracker
    if buy_product_tracker:

        users_info    = read_user_info()
        user_info     = users_info.loc[users_info.name == username]
        user_nob      = user_info.nob.tolist()[0]
        user_balance  = user_info.balance.tolist()[0]

        last_factor = "فاکتور خرید محصول\n\n"


        discount = 0.
        for index, row in discount_info.iterrows():

            if user_nob < row["مشخصات"]:
                discount = float(row["درصد تخفیف"])
                last_factor += "تخفیف: "
                last_factor += f"{row['توضیحات']}\n"
                last_factor += "میزان تخفیف: "
                last_factor += f'{float(row["درصد تخفیف"])*100}% \n'
                break
        sum_of_basket     = 0
        sum_with_discount = 0
        for index, pi in enumerate(my_basket["what"]):

            sum_of_basket     += product_data_frame.at[pi, product_data_frame.columns[1]]
            sum_with_discount += (1. - discount) * product_data_frame.at[pi, product_data_frame.columns[1]]



            last_factor += f"محصول شماره {pi + 1}\n"
            last_factor += "نام محصول: "
            last_factor += f"{product_data_frame.at[pi, product_data_frame.columns[0]]}\n"

            last_factor += "قیمت: "
            last_factor += f"{product_data_frame.at[pi, product_data_frame.columns[1]]}"
            last_factor += " تومان\n"

            last_factor += "برند: "
            last_factor += f"{product_data_frame.at[pi, product_data_frame.columns[-1]]}\n"

            last_factor += "\n\n"
        last_factor += "جمع نهایی: "
        last_factor += f"{sum_of_basket}\n"
        last_factor += "جمع نهایی (با در نظر گرفتن تخفیف): "
        last_factor += f"{sum_with_discount}"



        if sum_with_discount > user_balance:
            bot.send_message(message.chat.id, "کاربر گرامی موجودی حساب شما برای این خرید کافی نیست. لذا به منوی قبل بازگشته و حساب خود را شارژ کنید.", reply_markup=markup_purchase)
        else:
            index = users_info.index[users_info.name == username].tolist()[0]
            users_info.at[index, "balance"] -= sum_with_discount
            users_info.at[index, "nob"]     += len(my_basket["what"])

            write_user_info(users_info)
            bot.send_message(message.chat.id, "کاربر گرامی خرید شما با موفقیت انجام شد. به منظور مشاده فاکتور روی آیتم مربوطه کلیک کنید.", reply_markup=markup_purchase)

            write_product_info(product_data_frame)
            my_basket = {"who": [], "what": []}
            buy_product_tracker = False
            confirm_factor = True
            choose_basket_tracker = False

    else:
        log = "کاربر گرامی، لیست خرید شما خالی است. لطفا اقدام به انتخاب محصول کنید.\n\n"
        bot.send_message(message.chat.id, log, reply_markup=markup_purchase)


@bot.message_handler(regexp=r"^فاکتور$")
def show_factor(message):
    global confirm_factor
    if confirm_factor:
        bot.send_message(message.chat.id, last_factor, reply_markup=markup_purchase)
        confirm_factor = False
    else:
        bot.send_message(message.chat.id, "کاربر گرامی  خریدی برای شما ثبت نگردیده است. لطفا ابتدا خرید بفرمایید.", reply_markup=markup_purchase)


@bot.message_handler(regexp=r"^بازگشت$")
def return_to_main_menu(message):
    bot.send_message(message.chat.id, "بازگشت به منوی اصلی:", reply_markup=markup_main)

@bot.message_handler(regexp=r"^اصلاح سبد خرید$")
def return_to_main_menu(message):
    global product_data_frame
    if product_data_frame is not None:
        logs = "کاربر گرامی، سبد خرید شما خالی شد. لطفا دوباره از گزینه‌ی انتخاب محصول استفاده کنید:\n\n"
        description, ـ, ـ = product_info(message)
        logs += description

        global my_basket, last_factor, confirm_factor, choose_basket_tracker
        my_basket = {"who": [], "what": []}
        product_data_frame = None
        last_factor = None
        confirm_factor = False
        choose_basket_tracker = False

        bot.send_message(message.chat.id, logs, reply_markup=markup_purchase)
    else:
        log = "کاربر گرامی، لیست خرید شما خالی است. لطفا اقدام به انتخاب محصول کنید.\n\n"
        bot.send_message(message.chat.id, log, reply_markup=markup_purchase)

@bot.message_handler(regexp=r"^ارتباط با ما$")
def contact_us(message):
    log = ""
    log += "لطفا پیام خود رو به فرمت زیر وارد کنید:\n\n"
    log += "موضوع پیام: (در این قسمت موضوع و عنوان پیام را وارد کنید)\n"
    log += "متن پیام: (در این قسمت متن پیام را وارد کنید)\n"
    bot.send_message(message.chat.id, log, reply_markup=markup_main)

@bot.message_handler(func=lambda mess: "موضوع پیام" in mess.text)
def process_message(message):
    log = ""
    log += "پیام شما با محتوای :\n\n"
    log += message.text
    log += "\n\nدریافت شد."
    bot.send_message(message.chat.id, log, reply_markup=markup_main)


@bot.message_handler(regexp=r"^(\d+\s?)+$")
def receive_order_number(message):
    text = message.text # "2 3 5"
    product_id            = [int(t)-1 for t in text.split(" ")] # -> ["2", "3", "5"]
    description, df, available_index = product_info(message)

    log = ""

    global my_basket, product_data_frame, buy_product_tracker, choose_basket_tracker
    if (len(my_basket["who"]) == 0) and (not choose_basket_tracker):
        choose_basket_tracker  = True
        for pi in product_id:
            if pi in available_index:
                df.at[pi, "تعداد"] -= 1
                my_basket["who"].append(message.from_user.username)
                my_basket["what"].append(pi)

                log += "محصول با شناسه‌ی "
                log += f"{pi+1}"
                log += " به سبد خرید شما اضافه شد.\n"
            else:
                log += "محصول با شناسه‌ی "
                log += f"{pi+1}"
                log += " یافت نشد/در انبار موجود نمی‌باشد.\n"

        if len(my_basket["who"]) == 0:
            log += "متاسفانه سبد خرید شما خالی است. لطفا با دقت شماره محصولات ارسالی را وارد کنید.\n"
        else:
            buy_product_tracker = True
            log += f"تعداد {len(my_basket['who'])}"
            log += " از "
            log += f"{len(product_id)}"
            log += " محصول شما به سبد خرید اضافه شد. لطفا بر روی مشاهده/تایید/اصلاح سبد خرید کلیک کنید."

        product_data_frame = df
    else:
        log = "شما لیست محصول خود را انتخاب کرده‌اید. لطفا برای تایید یا اصلاح آن از دکمه‌های موجود استفاده کنید."
    bot.reply_to(message, log)

@bot.message_handler(func = lambda m: m.text not in list_of_actions)
def process_message_and_feedabck(message):
    bot.reply_to(message, "دستور ورودی صحیح نیست. لطفا از بین گزینه‌های موجود انتخاب کنید:")



bot.polling()