"""DarsPro — test uchun 100 ta tayyor o'yin (har xil engine) yaratadi.

Idempotent: deterministik UUID (uuid5) + update_or_create. Qayta ishga
tushirilsa dublikat yaratmaydi, mavjudlarini yangilaydi. Topiclar
get_or_create orqali ta'minlanadi. Har bir item saqlashdan oldin
`validate_engine_data` orqali tekshiriladi.

Ishlatish:
    python manage.py seed_games
    python manage.py seed_games --clear   # avval eski seed itemlarni o'chiradi
"""
import uuid

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.content.models import (
    ContentItem,
    ContentSource,
    ContentStatus,
    GameEngine,
    Grade,
    Subject,
    Topic,
)
from apps.content.validators import validate_engine_data

# Seed itemlar uchun barqaror UUID namespace (o'zgartirmang — idempotentlik shunga bog'liq)
SEED_NS = uuid.UUID("5eed0000-0000-4000-8000-000000000000")


# subject_slug, grade_number, topic title, topic slug
TOPICS = {
    "bio_hujayra": ("biologiya", 7, "Hujayra tuzilishi", "hujayra-tuzilishi"),
    "bio_foto": ("biologiya", 7, "Fotosintez", "fotosintez-jarayoni"),
    "bio_organizm": ("biologiya", 6, "Tirik organizmlar", "tirik-organizmlar-seed"),
    "bio_inson": ("biologiya", 8, "Inson tanasi", "inson-tanasi"),
    "mat_kasr": ("matematika", 5, "Oddiy kasrlar", "oddiy-kasrlar-seed"),
    "mat_geom": ("matematika", 7, "Geometriya asoslari", "geometriya-asoslari-seed"),
    "mat_amal": ("matematika", 4, "Arifmetik amallar", "arifmetik-amallar"),
    "mat_foiz": ("matematika", 6, "Foizlar", "foizlar"),
    "fiz_harakat": ("fizika", 7, "Mexanik harakat", "mexanik-harakat"),
    "fiz_energiya": ("fizika", 8, "Energiya turlari", "energiya-turlari"),
    "kim_element": ("kimyo", 8, "Kimyoviy elementlar", "kimyoviy-elementlar"),
    "kim_modda": ("kimyo", 7, "Moddalar va ularning xossalari", "moddalar-xossalari"),
    "geo_qit": ("geografiya", 6, "Qit'alar va okeanlar", "qitalar-okeanlar"),
    "geo_ob": ("geografiya", 8, "Ob-havo va iqlim", "ob-havo-iqlim"),
    "tar_mustaqillik": ("tarix", 9, "O'zbekiston mustaqilligi", "ozbekiston-mustaqilligi"),
    "tar_amir": ("tarix", 7, "Amir Temur davri", "amir-temur-davri"),
    "ona_alifbo": ("ona-tili", 1, "Alifbo va harflar", "alifbo-harflar"),
    "ona_soz": ("ona-tili", 5, "So'z turkumlari", "soz-turkumlari"),
    "eng_animals": ("ingliz-tili", 3, "Animals", "animals-hayvonlar"),
    "eng_colors": ("ingliz-tili", 2, "Colors and Numbers", "colors-numbers"),
}


def q(text, options, answer, t=20):
    return {"text": text, "image": None, "options": options, "answer": answer, "time_limit": t}


# ─────────────────────────── QUIZ (20) ───────────────────────────
QUIZ = [
    ("bio_hujayra", "Hujayra tuzilishi — test", [
        q("Hujayraning eng tashqi qismi qaysi?", ["Yadro", "Sitoplazma", "Membrana", "Vakuol"], 2),
        q("Genetik ma'lumot qayerda saqlanadi?", ["Yadro", "Ribosoma", "Vakuol", "Membrana"], 0),
        q("Energiya ishlab chiqaruvchi organoid?", ["Yadro", "Mitoxondriya", "Vakuol", "Membrana"], 1),
        q("Oqsil sintezi qayerda boradi?", ["Ribosoma", "Yadro", "Vakuol", "Membrana"], 0),
    ]),
    ("bio_foto", "Fotosintez — test", [
        q("Fotosintez uchun zarur gaz?", ["Kislorod", "Karbonat angidrid", "Azot", "Vodorod"], 1),
        q("Yashil pigment nima deyiladi?", ["Gemoglobin", "Xlorofill", "Melanin", "Karotin"], 1),
        q("Fotosintez natijasida ajraladigan gaz?", ["Karbonat angidrid", "Azot", "Kislorod", "Metan"], 2),
    ]),
    ("bio_organizm", "Tirik organizmlar — test", [
        q("Quyidagilardan qaysi biri tirik organizm?", ["Tosh", "Daraxt", "Suv", "Havo"], 1),
        q("O'simliklar oziqni qanday hosil qiladi?", ["Fotosintez", "Nafas olish", "Hazm qilish", "Bo'linish"], 0),
        q("Hayvonlar nima bilan nafas oladi?", ["Faqat teri", "Kislorod", "Azot", "Karbonat angidrid"], 1),
    ]),
    ("bio_inson", "Inson tanasi — test", [
        q("Qonni tana bo'ylab haydaydigan organ?", ["O'pka", "Yurak", "Jigar", "Buyrak"], 1),
        q("Nafas olish organi qaysi?", ["Yurak", "O'pka", "Oshqozon", "Buyrak"], 1),
        q("Suyaklar nimadan tashkil topgan tizim?", ["Asab", "Skelet", "Qon", "Teri"], 1),
    ]),
    ("mat_kasr", "Oddiy kasrlar — test", [
        q("1/2 + 1/2 nechaga teng?", ["1", "1/4", "2/4", "0"], 0),
        q("3/4 kasrning surati qaysi?", ["4", "3", "7", "1"], 1),
        q("1/4 dan kattasi qaysi?", ["1/8", "1/2", "1/10", "0"], 1),
    ]),
    ("mat_geom", "Geometriya — test", [
        q("Uchburchakning nechta tomoni bor?", ["2", "3", "4", "5"], 1, 15),
        q("To'g'ri burchak necha gradus?", ["45", "60", "90", "180"], 2),
        q("Kvadratning nechta teng tomoni bor?", ["2", "3", "4", "6"], 2),
    ]),
    ("mat_amal", "Arifmetik amallar — test", [
        q("7 × 8 nechaga teng?", ["54", "56", "64", "48"], 1, 15),
        q("100 − 37 nechaga teng?", ["63", "73", "67", "53"], 0),
        q("144 : 12 nechaga teng?", ["11", "12", "14", "16"], 1),
    ]),
    ("mat_foiz", "Foizlar — test", [
        q("200 ning 10% qancha?", ["10", "20", "30", "40"], 1),
        q("50 ning 50% qancha?", ["10", "25", "50", "100"], 1),
        q("1000 ning 25% qancha?", ["100", "200", "250", "500"], 2),
    ]),
    ("fiz_harakat", "Mexanik harakat — test", [
        q("Tezlik qaysi birlikda o'lchanadi?", ["kg", "m/s", "N", "J"], 1),
        q("Harakatsiz jism qanday holatda?", ["Tinch", "Tezlanuvchi", "Sekinlashuvchi", "Aylanuvchi"], 0),
        q("Yo'l qaysi birlikda o'lchanadi?", ["soniya", "metr", "kilogramm", "vatt"], 1),
    ]),
    ("fiz_energiya", "Energiya — test", [
        q("Quyosh qaysi energiya manbai?", ["Yadro", "Tabiiy", "Sun'iy", "Kimyoviy"], 1),
        q("Energiya birligi qaysi?", ["Nyuton", "Joul", "Vatt", "Paskal"], 1),
        q("Harakatdagi jism qaysi energiyaga ega?", ["Potensial", "Kinetik", "Issiqlik", "Yorug'lik"], 1),
    ]),
    ("kim_element", "Kimyoviy elementlar — test", [
        q("Suvning kimyoviy formulasi?", ["CO2", "H2O", "O2", "NaCl"], 1),
        q("Kislorod belgisi qaysi?", ["O", "K", "C", "H"], 0),
        q("Osh tuzining formulasi?", ["H2O", "NaCl", "CO2", "KOH"], 1),
    ]),
    ("kim_modda", "Moddalar xossalari — test", [
        q("Suv qaysi holatda muzlaydi?", ["100°C", "0°C", "50°C", "-100°C"], 1),
        q("Suv necha gradusda qaynaydi?", ["50°C", "90°C", "100°C", "120°C"], 2),
        q("Quyidagilardan qaysi biri gaz?", ["Temir", "Kislorod", "Suv", "Tuz"], 1),
    ]),
    ("geo_qit", "Qit'alar — test", [
        q("Eng katta qit'a qaysi?", ["Afrika", "Osiyo", "Yevropa", "Avstraliya"], 1),
        q("O'zbekiston qaysi qit'ada joylashgan?", ["Afrika", "Osiyo", "Yevropa", "Amerika"], 1),
        q("Eng katta okean qaysi?", ["Atlantika", "Tinch", "Hind", "Shimoliy"], 1),
    ]),
    ("geo_ob", "Ob-havo va iqlim — test", [
        q("Yog'ingarchilik nima bilan o'lchanadi?", ["Termometr", "Yomg'ir o'lchagich", "Barometr", "Kompas"], 1),
        q("Havo harorati nima bilan o'lchanadi?", ["Termometr", "Lineyka", "Tarozi", "Soat"], 0),
        q("Quyidagilardan qaysi biri iqlim turi?", ["Tog'", "Cho'l", "Daryo", "Ko'l"], 1),
    ]),
    ("tar_mustaqillik", "Mustaqillik — test", [
        q("O'zbekiston qachon mustaqil bo'ldi?", ["1989", "1991", "1995", "2001"], 1),
        q("Mustaqillik kuni qaysi sanada?", ["1-yanvar", "1-sentyabr", "9-may", "8-dekabr"], 1),
        q("O'zbekiston poytaxti qaysi shahar?", ["Samarqand", "Toshkent", "Buxoro", "Xiva"], 1),
    ]),
    ("tar_amir", "Amir Temur davri — test", [
        q("Amir Temur davlatining poytaxti?", ["Buxoro", "Samarqand", "Xiva", "Toshkent"], 1),
        q("Amir Temur qaysi asrda yashagan?", ["XII", "XIV", "XVI", "XVIII"], 1),
        q("Registon maydoni qaysi shaharda?", ["Toshkent", "Samarqand", "Buxoro", "Xiva"], 1),
    ]),
    ("ona_soz", "So'z turkumlari — test", [
        q("'Kitob' qaysi so'z turkumi?", ["Fe'l", "Ot", "Sifat", "Son"], 1),
        q("'Yugurmoq' qaysi so'z turkumi?", ["Ot", "Fe'l", "Sifat", "Ravish"], 1),
        q("'Qizil' qaysi so'z turkumi?", ["Ot", "Fe'l", "Sifat", "Son"], 2),
    ]),
    ("eng_animals", "Animals — quiz", [
        q("'It' inglizcha qanday?", ["Cat", "Dog", "Bird", "Fish"], 1),
        q("'Mushuk' inglizcha qanday?", ["Dog", "Cat", "Cow", "Horse"], 1),
        q("'Baliq' inglizcha qanday?", ["Fish", "Bird", "Frog", "Bee"], 0),
    ]),
    ("eng_colors", "Colors — quiz", [
        q("'Qizil' inglizcha qanday?", ["Blue", "Red", "Green", "Black"], 1),
        q("'Ko'k' inglizcha qanday?", ["Blue", "Red", "Yellow", "White"], 0),
        q("'Three' o'zbekcha nechaga teng?", ["2", "3", "4", "5"], 1),
    ]),
    ("ona_alifbo", "Alifbo — test", [
        q("'Olma' so'zi qaysi harf bilan boshlanadi?", ["O", "A", "L", "M"], 0, 15),
        q("'Kitob' so'zida nechta harf bor?", ["4", "5", "6", "3"], 1, 15),
        q("Quyidagilardan qaysi biri unli harf?", ["B", "A", "K", "T"], 1, 15),
    ]),
]

# ─────────────────────────── MATCHING (10) ───────────────────────────
MATCHING = [
    ("bio_foto", "Fotosintez juftliklari", [
        ("Xlorofill", "Yashil pigment, yorug'likni yutadi"),
        ("Karbonat angidrid", "O'simlik yutadigan gaz"),
        ("Kislorod", "Fotosintezda ajraladigan gaz"),
        ("Glyukoza", "Hosil bo'ladigan oziq modda"),
    ]),
    ("bio_hujayra", "Hujayra organoidlari", [
        ("Yadro", "Genetik markaz"),
        ("Mitoxondriya", "Energiya stansiyasi"),
        ("Ribosoma", "Oqsil sintezi"),
        ("Membrana", "Tashqi qobiq"),
    ]),
    ("kim_element", "Element va belgisi", [
        ("Kislorod", "O"),
        ("Vodorod", "H"),
        ("Uglerod", "C"),
        ("Temir", "Fe"),
    ]),
    ("mat_geom", "Shakl va tomonlar soni", [
        ("Uchburchak", "3 ta tomon"),
        ("Kvadrat", "4 ta teng tomon"),
        ("Beshburchak", "5 ta tomon"),
        ("Olti burchak", "6 ta tomon"),
    ]),
    ("geo_qit", "Mamlakat va poytaxti", [
        ("O'zbekiston", "Toshkent"),
        ("Qozog'iston", "Ostona"),
        ("Tojikiston", "Dushanbe"),
        ("Qirg'iziston", "Bishkek"),
    ]),
    ("eng_animals", "English — Animals", [
        ("Dog", "It"),
        ("Cat", "Mushuk"),
        ("Cow", "Sigir"),
        ("Horse", "Ot"),
    ]),
    ("eng_colors", "English — Colors", [
        ("Red", "Qizil"),
        ("Blue", "Ko'k"),
        ("Green", "Yashil"),
        ("Yellow", "Sariq"),
    ]),
    ("fiz_harakat", "Kattalik va birligi", [
        ("Tezlik", "m/s"),
        ("Yo'l", "metr"),
        ("Vaqt", "soniya"),
        ("Kuch", "Nyuton"),
    ]),
    ("tar_amir", "Tarixiy obida va shahri", [
        ("Registon", "Samarqand"),
        ("Ark qal'asi", "Buxoro"),
        ("Ichan qal'a", "Xiva"),
        ("Go'ri Amir", "Samarqand"),
    ]),
    ("ona_soz", "So'z va turkumi", [
        ("Daraxt", "Ot"),
        ("Yugurmoq", "Fe'l"),
        ("Baland", "Sifat"),
        ("Besh", "Son"),
    ]),
]

# ─────────────────────────── FLASHCARD (10) ───────────────────────────
FLASHCARD = [
    ("bio_hujayra", "Hujayra atamalari", [
        ("Membrana", "Hujayrani o'rab turuvchi tashqi qatlam"),
        ("Yadro", "Genetik ma'lumotni saqlovchi markaz"),
        ("Sitoplazma", "Hujayra ichini to'ldiruvchi muhit"),
        ("Mitoxondriya", "Energiya ishlab chiqaruvchi organoid"),
    ]),
    ("kim_modda", "Kimyo atamalari", [
        ("Atom", "Moddaning eng kichik bo'lagi"),
        ("Molekula", "Atomlardan tashkil topgan zarra"),
        ("Element", "Bir xil atomlardan iborat modda"),
        ("Reaksiya", "Moddalarning o'zaro ta'siri"),
    ]),
    ("ona_alifbo", "Alifbo kartochkalari", [
        ("A", "Olma"),
        ("B", "Baliq"),
        ("D", "Daraxt"),
        ("K", "Kitob"),
    ]),
    ("eng_animals", "English animals", [
        ("Dog", "It"),
        ("Cat", "Mushuk"),
        ("Bird", "Qush"),
        ("Fish", "Baliq"),
    ]),
    ("eng_colors", "English colors", [
        ("Red", "Qizil"),
        ("Blue", "Ko'k"),
        ("Black", "Qora"),
        ("White", "Oq"),
    ]),
    ("mat_geom", "Geometrik shakllar", [
        ("Uchburchak", "3 burchakli shakl"),
        ("Kvadrat", "Teng tomonli to'rtburchak"),
        ("Aylana", "Markazdan teng uzoqlikdagi nuqtalar"),
        ("To'g'ri burchak", "90 gradusli burchak"),
    ]),
    ("fiz_energiya", "Energiya atamalari", [
        ("Kinetik energiya", "Harakatdagi jism energiyasi"),
        ("Potensial energiya", "Holatga bog'liq energiya"),
        ("Joul", "Energiya o'lchov birligi"),
        ("Quvvat", "Vaqt birligida bajarilgan ish"),
    ]),
    ("geo_ob", "Ob-havo atamalari", [
        ("Termometr", "Haroratni o'lchaydigan asbob"),
        ("Barometr", "Atmosfera bosimini o'lchaydi"),
        ("Iqlim", "Uzoq vaqtli ob-havo holati"),
        ("Yog'in", "Yomg'ir, qor va do'l"),
    ]),
    ("tar_mustaqillik", "Mustaqillik atamalari", [
        ("Mustaqillik", "Erkin va o'z taqdirini o'zi belgilash"),
        ("Konstitutsiya", "Asosiy qonun"),
        ("Bayroq", "Davlat ramzi"),
        ("Madhiya", "Davlat qo'shig'i"),
    ]),
    ("bio_inson", "Inson organlari", [
        ("Yurak", "Qonni haydaydi"),
        ("O'pka", "Nafas olish organi"),
        ("Jigar", "Qonni tozalaydi"),
        ("Buyrak", "Siydik ajratadi"),
    ]),
]

# ─────────────────────────── TRUE / FALSE (10) ───────────────────────────
def tf(text, ans):
    return {"text": text, "answer": ans}


TRUE_FALSE = [
    ("bio_organizm", "Tirik organizmlar — to'g'ri/noto'g'ri", [
        tf("O'simliklar fotosintez qiladi.", True),
        tf("Baliqlar o'pka bilan nafas oladi.", False),
        tf("Hujayra tirik organizmning asosiy birligi.", True),
    ]),
    ("bio_hujayra", "Hujayra — to'g'ri/noto'g'ri", [
        tf("Yadro genetik ma'lumotni saqlaydi.", True),
        tf("Mitoxondriya oqsil sintez qiladi.", False),
        tf("Membrana hujayrani o'rab turadi.", True),
    ]),
    ("mat_amal", "Matematika — to'g'ri/noto'g'ri", [
        tf("2 + 2 = 4", True),
        tf("10 × 10 = 100", True),
        tf("7 − 3 = 5", False),
    ]),
    ("geo_qit", "Geografiya — to'g'ri/noto'g'ri", [
        tf("Osiyo eng katta qit'a.", True),
        tf("O'zbekiston Afrikada joylashgan.", False),
        tf("Tinch okeani eng katta okean.", True),
    ]),
    ("kim_modda", "Kimyo — to'g'ri/noto'g'ri", [
        tf("Suv 100°C da qaynaydi.", True),
        tf("Suv 50°C da muzlaydi.", False),
        tf("Kislorod gaz holatida.", True),
    ]),
    ("fiz_harakat", "Fizika — to'g'ri/noto'g'ri", [
        tf("Tezlik m/s da o'lchanadi.", True),
        tf("Yo'l kilogrammda o'lchanadi.", False),
        tf("Harakatsiz jism tinch holatda.", True),
    ]),
    ("tar_mustaqillik", "Tarix — to'g'ri/noto'g'ri", [
        tf("O'zbekiston 1991-yilda mustaqil bo'ldi.", True),
        tf("Toshkent O'zbekiston poytaxti.", True),
        tf("Mustaqillik kuni 1-yanvarda nishonlanadi.", False),
    ]),
    ("eng_animals", "English — true/false", [
        tf("'Dog' means 'It'.", True),
        tf("'Cat' means 'Sigir'.", False),
        tf("'Fish' means 'Baliq'.", True),
    ]),
    ("bio_inson", "Inson tanasi — to'g'ri/noto'g'ri", [
        tf("Yurak qonni haydaydi.", True),
        tf("O'pka oziqni hazm qiladi.", False),
        tf("Skelet suyaklardan iborat.", True),
    ]),
    ("ona_soz", "Ona tili — to'g'ri/noto'g'ri", [
        tf("'Kitob' — ot.", True),
        tf("'Yugurmoq' — sifat.", False),
        tf("'Qizil' — sifat.", True),
    ]),
]

# ─────────────────────────── POLL (7) ───────────────────────────
POLL = [
    ("bio_organizm", "Eng sevimli hayvoningiz?", ["It", "Mushuk", "Ot", "Quyon"]),
    ("mat_geom", "Qaysi shakl sizga yoqadi?", ["Uchburchak", "Kvadrat", "Aylana", "Yulduz"]),
    ("geo_qit", "Qaysi qit'aga sayohat qilgingiz keladi?", ["Yevropa", "Osiyo", "Afrika", "Amerika"]),
    ("eng_colors", "Eng yoqtirgan rangingiz?", ["Qizil", "Ko'k", "Yashil", "Sariq"]),
    ("ona_soz", "Qaysi fan sizga qiziq?", ["Matematika", "Biologiya", "Tarix", "Ona tili"]),
    ("fiz_energiya", "Qaysi energiya manbai muhim?", ["Quyosh", "Shamol", "Suv", "Yadro"]),
    ("tar_amir", "Qaysi tarixiy shaharni ko'rgingiz keladi?", ["Samarqand", "Buxoro", "Xiva", "Shahrisabz"]),
]

# ─────────────────────────── SPIN WHEEL (7) ───────────────────────────
SPIN = [
    ("ona_alifbo", "O'quvchini tanlash", ["Ali", "Vali", "Maftuna", "Jasur", "Dilnoza", "Sardor"], "students"),
    ("mat_amal", "Misol raqami", ["1", "2", "3", "4", "5", "6"], "numbers"),
    ("bio_organizm", "Mavzu tanlash", ["Hayvonlar", "O'simliklar", "Hasharotlar", "Qushlar"], "topics"),
    ("eng_colors", "Pick a color", ["Red", "Blue", "Green", "Yellow", "Orange"], "topics"),
    ("geo_qit", "Qit'a tanlash", ["Osiyo", "Yevropa", "Afrika", "Amerika", "Avstraliya"], "topics"),
    ("tar_amir", "Savol tanlash", ["1-savol", "2-savol", "3-savol", "4-savol", "5-savol"], "questions"),
    ("kim_element", "Element tanlash", ["Vodorod", "Kislorod", "Uglerod", "Temir", "Oltin"], "topics"),
]

# ─────────────────────────── MEMORY (7) ───────────────────────────
MEMORY = [
    ("bio_organizm", "Hayvonlar xotira", [("🐶", "It"), ("🐱", "Mushuk"), ("🐮", "Sigir"), ("🐴", "Ot")]),
    ("eng_animals", "Animals memory", [("🐶", "Dog"), ("🐱", "Cat"), ("🐦", "Bird"), ("🐟", "Fish")]),
    ("geo_ob", "Ob-havo xotira", [("☀️", "Quyosh"), ("🌧️", "Yomg'ir"), ("❄️", "Qor"), ("⛅", "Bulut")]),
    ("eng_colors", "Colors memory", [("🔴", "Red"), ("🔵", "Blue"), ("🟢", "Green"), ("🟡", "Yellow")]),
    ("mat_geom", "Shakllar xotira", [("🔺", "Uchburchak"), ("🟦", "Kvadrat"), ("⭕", "Aylana"), ("⭐", "Yulduz")]),
    ("kim_element", "Element xotira", [("💧", "Suv"), ("🔥", "Olov"), ("🌬️", "Havo"), ("🪨", "Tosh")]),
    ("bio_foto", "Tabiat xotira", [("🌱", "Maysa"), ("🌳", "Daraxt"), ("🌸", "Gul"), ("🍂", "Barg")]),
]

# ─────────────────────────── SORT ORDER (7) ───────────────────────────
SORT = [
    ("bio_foto", "O'simlik o'sish bosqichlari", [
        ("Urug' ekish", 1), ("Suv berish", 2), ("Unib chiqish", 3), ("Gullash", 4)]),
    ("mat_amal", "Sonlarni o'sish tartibida", [
        ("3", 1), ("7", 2), ("12", 3), ("25", 4)]),
    ("bio_inson", "Ovqat hazm bo'lish yo'li", [
        ("Og'iz", 1), ("Qizilo'ngach", 2), ("Oshqozon", 3), ("Ichak", 4)]),
    ("tar_mustaqillik", "Tarixiy voqealar tartibi", [
        ("Mustaqillik e'lon qilindi", 1), ("Konstitutsiya qabul qilindi", 2),
        ("Milliy valyuta joriy etildi", 3), ("Yangi O'zbekiston", 4)]),
    ("geo_ob", "Suv aylanishi bosqichlari", [
        ("Bug'lanish", 1), ("Bulut hosil bo'lishi", 2), ("Yog'in", 3), ("Daryoga oqish", 4)]),
    ("ona_alifbo", "Alifbo tartibi", [
        ("A", 1), ("B", 2), ("D", 3), ("E", 4)]),
    ("fiz_harakat", "Harakat bosqichlari", [
        ("Tinch holat", 1), ("Tezlanish", 2), ("Bir tekis harakat", 3), ("To'xtash", 4)]),
]

# ─────────────────────────── FILL BLANK (7) ───────────────────────────
FILL = [
    ("bio_hujayra", "Hujayra — bo'sh joyni to'ldiring",
     "Hujayraning genetik markazi ___ deb ataladi, energiya esa ___ da ishlab chiqariladi.",
     ["yadro", "mitoxondriya"], ["organoidlar"]),
    ("tar_mustaqillik", "Mustaqillik — bo'sh joy",
     "O'zbekiston ___ yilda mustaqil bo'ldi, poytaxti ___ shahri.",
     ["1991", "Toshkent"], []),
    ("geo_qit", "Geografiya — bo'sh joy",
     "Eng katta qit'a ___ , eng katta okean esa ___ deb ataladi.",
     ["Osiyo", "Tinch"], []),
    ("kim_modda", "Kimyo — bo'sh joy",
     "Suv ___ gradusda qaynaydi va ___ gradusda muzlaydi.",
     ["100", "0"], ["harorat"]),
    ("mat_geom", "Geometriya — bo'sh joy",
     "Uchburchakning ___ ta tomoni va to'g'ri burchak ___ gradus bo'ladi.",
     ["3", "90"], []),
    ("bio_foto", "Fotosintez — bo'sh joy",
     "Fotosintez jarayonida o'simlik ___ yutadi va ___ ajratadi.",
     ["karbonat angidrid", "kislorod"], []),
    ("ona_soz", "Ona tili — bo'sh joy",
     "Predmetni bildiruvchi so'z ___ , harakatni bildiruvchi so'z ___ deyiladi.",
     ["ot", "fe'l"], ["so'z turkumlari"]),
]

# ─────────────────────────── WORD SEARCH (8) ───────────────────────────
WORDSEARCH = [
    ("bio_hujayra", "Hujayra atamalari — so'z izlash", ["YADRO", "MEMBRANA", "ATOM", "ION"], 12),
    ("kim_element", "Elementlar — so'z izlash", ["TEMIR", "OLTIN", "MIS", "RUX"], 12),
    ("geo_qit", "Qit'alar — so'z izlash", ["OSIYO", "AFRIKA", "YEVROPA"], 12),
    ("eng_animals", "Animals — word search", ["DOG", "CAT", "BIRD", "FISH"], 10),
    ("eng_colors", "Colors — word search", ["RED", "BLUE", "GREEN"], 10),
    ("mat_geom", "Shakllar — so'z izlash", ["KVADRAT", "AYLANA", "UCHBURCHAK"], 14),
    ("tar_amir", "Shaharlar — so'z izlash", ["SAMARQAND", "BUXORO", "XIVA"], 14),
    ("bio_inson", "Organlar — so'z izlash", ["YURAK", "OPKA", "JIGAR", "BUYRAK"], 12),
]

# ─────────────────────────── CROSSWORD (7) ───────────────────────────
CROSSWORD = [
    ("bio_hujayra", "Hujayra — krossvord", [
        ("YADRO", "Genetik markaz"), ("ATOM", "Eng kichik zarra"), ("ION", "Zaryadlangan zarra")]),
    ("kim_element", "Elementlar — krossvord", [
        ("TEMIR", "Fe belgili metall"), ("OLTIN", "Qimmatbaho sariq metall"), ("MIS", "Cu belgili metall")]),
    ("geo_qit", "Geografiya — krossvord", [
        ("OSIYO", "Eng katta qit'a"), ("NIL", "Afrikadagi daryo"), ("TOSHKENT", "O'zbekiston poytaxti")]),
    ("mat_geom", "Geometriya — krossvord", [
        ("KVADRAT", "Teng tomonli to'rtburchak"), ("AYLANA", "Yumaloq shakl"), ("BURCHAK", "Ikki nur orasidagi figura")]),
    ("tar_amir", "Tarix — krossvord", [
        ("TEMUR", "Buyuk sarkarda"), ("SAMARQAND", "Davlat poytaxti"), ("REGISTON", "Mashhur maydon")]),
    ("bio_inson", "Inson tanasi — krossvord", [
        ("YURAK", "Qon haydovchi organ"), ("OPKA", "Nafas olish organi"), ("JIGAR", "Qonni tozalaydi")]),
    ("eng_animals", "Animals — crossword", [
        ("DOG", "It"), ("CAT", "Mushuk"), ("FISH", "Baliq")]),
]


def build_games():
    """(engine_slug, topic_key, title, data) ro'yxatini quradi (jami 100 ta)."""
    games = []
    for key, title, questions in QUIZ:
        games.append(("quiz", key, title, {"questions": questions}))
    for key, title, pairs in MATCHING:
        games.append(("matching", key, title,
                      {"pairs": [{"term": t, "definition": d} for t, d in pairs]}))
    for key, title, cards in FLASHCARD:
        games.append(("flashcard", key, title,
                      {"cards": [{"front": f, "back": b} for f, b in cards]}))
    for key, title, statements in TRUE_FALSE:
        games.append(("true_false", key, title, {"statements": statements}))
    for key, question, options in POLL:
        games.append(("poll", key, question, {"question": question, "options": options}))
    for key, title, items, typ in SPIN:
        games.append(("spin_wheel", key, title, {"items": items, "type": typ}))
    for key, title, pairs in MEMORY:
        games.append(("memory", key, title,
                      {"pairs": [{"a": a, "b": b} for a, b in pairs]}))
    for key, title, items in SORT:
        games.append(("sort_order", key, title,
                      {"title": title, "items": [{"text": t, "order": o} for t, o in items]}))
    for key, title, text, blanks, hints in FILL:
        games.append(("fill_blank", key, title,
                      {"text": text, "blanks": blanks, "hints": hints}))
    for key, title, words, grid in WORDSEARCH:
        games.append(("word_search", key, title, {"words": words, "grid_size": grid}))
    for key, title, words in CROSSWORD:
        games.append(("crossword", key, title,
                      {"words": [{"word": w, "clue": c} for w, c in words]}))
    return games


class Command(BaseCommand):
    help = "Test uchun 100 ta har xil engine o'yinini yaratadi (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Avval eski seed o'yinlarini o'chiradi.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        games = build_games()

        # Sanity: rejaga ko'ra 100 ta
        if len(games) != 100:
            self.stdout.write(
                self.style.WARNING(f"Diqqat: {len(games)} ta o'yin (100 kutilgan).")
            )

        if options["clear"]:
            deleted, _ = ContentItem.objects.filter(
                id__in=[self._pk(slug, i) for i, (slug, *_) in enumerate(games)]
            ).delete()
            self.stdout.write(f"O'chirildi: {deleted} ta eski seed item.")

        engines = self._engines()
        topics = self._topics()

        created = updated = 0
        for i, (engine_slug, topic_key, title, data) in enumerate(games):
            engine = engines.get(engine_slug)
            if engine is None:
                raise CommandError(
                    f"'{engine_slug}' engine topilmadi — fixturelarni yuklang."
                )
            topic = topics[topic_key]

            # Saqlashdan oldin tekshiramiz (xato bo'lsa darhol ko'rinadi)
            validate_engine_data(engine_slug, data)

            _, was_created = ContentItem.objects.update_or_create(
                id=self._pk(engine_slug, i),
                defaults={
                    "topic": topic,
                    "engine": engine,
                    "created_by": None,
                    "title": title,
                    "source": ContentSource.STAFF,
                    "status": ContentStatus.PUBLISHED,
                    "data": data,
                },
            )
            created += was_created
            updated += not was_created

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Tayyor: {created} ta yaratildi, {updated} ta yangilandi "
                f"(jami {len(games)} seed o'yin)."
            )
        )

    @staticmethod
    def _pk(engine_slug, index):
        return uuid.uuid5(SEED_NS, f"seed-game-{engine_slug}-{index}")

    def _engines(self):
        return {e.slug: e for e in GameEngine.objects.all()}

    def _topics(self):
        """TOPICS dan get_or_create — kerakli subject/grade mavjud bo'lishi shart."""
        result = {}
        for key, (subj_slug, grade_num, title, slug) in TOPICS.items():
            try:
                subject = Subject.objects.get(slug=subj_slug)
            except Subject.DoesNotExist:
                raise CommandError(
                    f"Subject '{subj_slug}' topilmadi — `loaddata subjects` qiling."
                )
            try:
                grade = Grade.objects.get(pk=grade_num)
            except Grade.DoesNotExist:
                raise CommandError(
                    f"Grade {grade_num} topilmadi — `loaddata grades` qiling."
                )
            topic, _ = Topic.objects.get_or_create(
                subject=subject,
                grade=grade,
                slug=slug,
                defaults={"title": title, "order": 0, "is_active": True},
            )
            result[key] = topic
        return result
