"""DarsPro — tarif (plan) narxlari va cheklovlari.

Yagona haqiqat manbai. CLAUDE.md dagi tariflar jadvaliga mos.
Bu yerdan ham pricing endpoint (`/api/users/plans`), ham admin dashboard
MRR hisobi o'qiydi. Narxlar — so'm/oy.
"""

# Tarif tartibida (free → max)
PLAN_PRICING = {
    "free": {
        "slug": "free",
        "label": "Bepul",
        "price": 0,
        "highlight": False,
        "tagline": "Tanishib chiqish uchun",
        "limits": {
            "library": "limited",
            "monthly_create": 0,
            "class_players": 10,
            "team_mode": False,
            "multi_teacher": 0,
            "ads": True,
        },
        "features": [
            "Cheklangan kutubxona",
            "Sinfda 10 tagacha o'quvchi",
            "Yakka (solo) rejim",
            "Reklama bilan",
        ],
    },
    "start": {
        "slug": "start",
        "label": "Start",
        "price": 19000,
        "highlight": False,
        "tagline": "Yangi boshlovchilar uchun",
        "limits": {
            "library": "full",
            "monthly_create": 15,
            "class_players": 30,
            "team_mode": True,
            "multi_teacher": 0,
            "ads": False,
        },
        "features": [
            "To'liq kutubxona",
            "Oyiga 15 ta o'yin yaratish",
            "Sinfda 30 tagacha o'quvchi",
            "Juft / jamoa rejimi",
            "Reklamasiz",
        ],
    },
    "pro": {
        "slug": "pro",
        "label": "Pro",
        "price": 39000,
        "highlight": True,
        "tagline": "Eng mashhur tanlov",
        "limits": {
            "library": "full",
            "monthly_create": None,  # cheksiz
            "class_players": 100,
            "team_mode": True,
            "multi_teacher": 0,
            "ads": False,
        },
        "features": [
            "To'liq kutubxona",
            "Cheksiz o'yin yaratish",
            "Sinfda 100 tagacha o'quvchi",
            "Juft / jamoa rejimi",
            "Reklamasiz",
        ],
    },
    "max": {
        "slug": "max",
        "label": "Max",
        "price": 79000,
        "highlight": False,
        "tagline": "Maktab va jamoalar uchun",
        "limits": {
            "library": "full",
            "monthly_create": None,  # cheksiz
            "class_players": 500,
            "team_mode": True,
            "multi_teacher": 5,
            "ads": False,
        },
        "features": [
            "To'liq kutubxona",
            "Cheksiz o'yin yaratish",
            "Sinfda 500 tagacha o'quvchi",
            "Juft / jamoa rejimi",
            "5 tagacha o'qituvchi",
            "Reklamasiz",
        ],
    },
}

# Pulli tariflar (MRR / pricing uchun)
PAID_PLANS = ["start", "pro", "max"]


def plan_price(slug):
    """Tarif narxini qaytaradi (noma'lum bo'lsa 0)."""
    plan = PLAN_PRICING.get(slug)
    return plan["price"] if plan else 0


def pricing_list():
    """Pricing endpoint uchun tartiblangan ro'yxat."""
    order = ["free", "start", "pro", "max"]
    return [PLAN_PRICING[slug] for slug in order]
