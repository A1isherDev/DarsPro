"""DarsPro — join_code generatsiyasi (ADR #4): DRS-XXXX format, 8 belgi."""
import secrets

# Chalkash belgilarsiz (0/O, 1/I yo'q)
_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_join_code():
    suffix = "".join(secrets.choice(_ALPHABET) for _ in range(4))
    return f"DRS-{suffix}"


def unique_join_code(model):
    """model (GameSession) uchun takrorlanmaydigan kod qaytaradi."""
    for _ in range(20):
        code = generate_join_code()
        if not model.objects.filter(join_code=code).exists():
            return code
    raise RuntimeError("Noyob join_code yaratib bo'lmadi.")
