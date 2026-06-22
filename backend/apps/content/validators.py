"""DarsPro — engine `data` JSONB sxema validatsiyasi.

Har engine slug uchun `data` strukturasini tekshiradi. ContentItem POST/PATCH
da chaqiriladi. Xato bo'lsa ValidationError ko'taradi (o'zbekcha xabar bilan).

MVP: quiz, matching, flashcard to'liq tekshiriladi. Qolgan enginelar uchun
yengil tekshiruv (skeleton) — keyingi fazada to'ldiriladi.
"""
import json

from rest_framework import serializers

# DoS oldini olish uchun cheklovlar
MAX_DATA_BYTES = 100 * 1024  # data JSONB ≤ 100KB
MAX_ITEMS = 200  # ro'yxat-asosli enginelar uchun element soni
MAX_QUESTIONS = 100
MAX_OPTIONS = 8
MAX_TEXT = 1000  # matn uzunligi


def _require(condition, message):
    if not condition:
        raise serializers.ValidationError({"data": message})


def _cap_items(items, label, limit=MAX_ITEMS):
    _require(len(items) <= limit, f"{label}: juda ko'p element (maks {limit}).")


def validate_quiz(data):
    questions = data.get("questions")
    _require(isinstance(questions, list) and questions, "quiz: kamida bitta savol kerak.")
    _cap_items(questions, "quiz", MAX_QUESTIONS)
    for i, q in enumerate(questions):
        _require(isinstance(q, dict), f"quiz: {i+1}-savol obyekt bo'lishi kerak.")
        _require(q.get("text"), f"quiz: {i+1}-savol matni bo'sh.")
        _require(len(q["text"]) <= MAX_TEXT, f"quiz: {i+1}-savol matni juda uzun.")
        opts = q.get("options")
        _require(
            isinstance(opts, list) and 2 <= len(opts) <= MAX_OPTIONS,
            f"quiz: {i+1}-savolda 2–{MAX_OPTIONS} variant bo'lishi kerak.",
        )
        ans = q.get("answer")
        _require(
            isinstance(ans, int) and 0 <= ans < len(opts),
            f"quiz: {i+1}-savolda 'answer' indeksi noto'g'ri.",
        )
        ans = q.get("answer")
        _require(
            isinstance(ans, int) and 0 <= ans < len(opts),
            f"quiz: {i+1}-savolda 'answer' indeksi noto'g'ri.",
        )


def validate_matching(data):
    pairs = data.get("pairs")
    _require(isinstance(pairs, list) and pairs, "matching: kamida bitta juftlik kerak.")
    for i, p in enumerate(pairs):
        _require(
            isinstance(p, dict) and p.get("term") and p.get("definition"),
            f"matching: {i+1}-juftlikda 'term' va 'definition' kerak.",
        )


def validate_flashcard(data):
    cards = data.get("cards")
    _require(isinstance(cards, list) and cards, "flashcard: kamida bitta karta kerak.")
    for i, c in enumerate(cards):
        _require(
            isinstance(c, dict) and c.get("front") and c.get("back"),
            f"flashcard: {i+1}-kartada 'front' va 'back' kerak.",
        )


def validate_spin_wheel(data):
    items = data.get("items")
    _require(
        isinstance(items, list) and len(items) >= 2,
        "spin_wheel: kamida 2 ta element kerak.",
    )
    for it in items:
        _require(
            isinstance(it, str) and it.strip(),
            "spin_wheel: elementlar bo'sh bo'lmasligi kerak.",
        )


def validate_memory(data):
    pairs = data.get("pairs")
    _require(isinstance(pairs, list) and pairs, "memory: kamida bitta juftlik kerak.")
    for i, p in enumerate(pairs):
        _require(
            isinstance(p, dict) and p.get("a") and p.get("b"),
            f"memory: {i+1}-juftlikda 'a' va 'b' kerak.",
        )


def validate_crossword(data):
    words = data.get("words")
    _require(isinstance(words, list) and words, "crossword: kamida bitta so'z kerak.")
    for i, w in enumerate(words):
        _require(
            isinstance(w, dict) and w.get("word") and w.get("clue"),
            f"crossword: {i+1}-so'zda 'word' va 'clue' kerak.",
        )


def validate_sort_order(data):
    items = data.get("items")
    _require(
        isinstance(items, list) and len(items) >= 2,
        "sort_order: kamida 2 ta element kerak.",
    )
    for i, it in enumerate(items):
        _require(
            isinstance(it, dict)
            and it.get("text")
            and isinstance(it.get("order"), int),
            f"sort_order: {i+1}-elementda 'text' va butun 'order' kerak.",
        )


def validate_fill_blank(data):
    text = data.get("text")
    blanks = data.get("blanks")
    _require(
        isinstance(text, str) and "___" in text,
        "fill_blank: matnda kamida bitta ___ bo'lishi kerak.",
    )
    _require(
        isinstance(blanks, list) and blanks,
        "fill_blank: javoblar (blanks) bo'sh bo'lmasligi kerak.",
    )
    _require(
        text.count("___") == len(blanks),
        "fill_blank: ___ soni javoblar soniga teng bo'lishi kerak.",
    )


def validate_word_search(data):
    words = data.get("words")
    grid = data.get("grid_size")
    _require(isinstance(words, list) and words, "word_search: kamida bitta so'z kerak.")
    _require(
        isinstance(grid, int) and 5 <= grid <= 20,
        "word_search: grid_size 5–20 oralig'ida bo'lishi kerak.",
    )
    for w in words:
        _require(
            isinstance(w, str) and 0 < len(w) <= grid,
            f"word_search: '{w}' grid o'lchamiga sig'maydi.",
        )


def validate_true_false(data):
    statements = data.get("statements")
    _require(
        isinstance(statements, list) and statements,
        "true_false: kamida bitta bayonot kerak.",
    )
    for i, s in enumerate(statements):
        _require(
            isinstance(s, dict) and s.get("text") and isinstance(s.get("answer"), bool),
            f"true_false: {i+1}-bayonotda 'text' va boolean 'answer' kerak.",
        )


def validate_poll(data):
    _require(data.get("question"), "poll: savol matni kerak.")
    options = data.get("options")
    _require(
        isinstance(options, list) and len(options) >= 2,
        "poll: kamida 2 ta variant kerak.",
    )
    for o in options:
        _require(isinstance(o, str) and o.strip(), "poll: variantlar bo'sh bo'lmasin.")


def _validate_skeleton(data):
    """Noma'lum engine uchun — bo'sh bo'lmasligini tekshiramiz."""
    _require(isinstance(data, dict) and data, "data bo'sh bo'lishi mumkin emas.")


# Engine slug -> validator
VALIDATORS = {
    "quiz": validate_quiz,
    "matching": validate_matching,
    "flashcard": validate_flashcard,
    "spin_wheel": validate_spin_wheel,
    "memory": validate_memory,
    "crossword": validate_crossword,
    "sort_order": validate_sort_order,
    "fill_blank": validate_fill_blank,
    "word_search": validate_word_search,
    "true_false": validate_true_false,
    "poll": validate_poll,
}


def validate_engine_data(engine_slug, data):
    """engine_slug ga mos validatorni chaqiradi."""
    data = data or {}
    # Umumiy hajm chegarasi (DoS oldini olish)
    try:
        size = len(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    except (TypeError, ValueError):
        raise serializers.ValidationError({"data": "data JSON'ga aylantirilmadi."})
    _require(size <= MAX_DATA_BYTES, "data juda katta (maks 100KB).")
    validator = VALIDATORS.get(engine_slug, _validate_skeleton)
    validator(data)
