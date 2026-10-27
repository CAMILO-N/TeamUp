from flask import current_app
from wtforms.validators import ValidationError


def is_valid_id_number(id_number):
    """Revisa una cédula ecuatoriana con el algoritmo del Registro Civil (módulo 10)."""
    if len(id_number) != 10 or not id_number.isdigit():
        return False

    province = int(id_number[:2])
    if not (1 <= province <= 24 or province == 30):
        return False

    # El tercer dígito es menor que 6 para personas naturales
    if int(id_number[2]) >= 6:
        return False

    # Los 9 primeros dígitos se multiplican por 2, 1, 2, 1...; si el resultado pasa de 9 se le resta 9
    total = 0
    for position, digit in enumerate(id_number[:9]):
        product = int(digit) * (2 if position % 2 == 0 else 1)
        total += product - 9 if product > 9 else product

    check_digit = (10 - total % 10) % 10
    return check_digit == int(id_number[9])


class EcuadorianIdNumber:
    """Validador de WTForms para la cédula."""

    def __init__(self, message="La cédula no es válida."):
        self.message = message

    def __call__(self, form, field):
        if not is_valid_id_number(field.data or ""):
            raise ValidationError(self.message)


class InstitutionalEmail:
    """Validador de WTForms: el correo debe ser del dominio de la universidad."""

    def __init__(self, message="Usa tu correo institucional."):
        self.message = message

    def __call__(self, form, field):
        domain = current_app.config["ALLOWED_EMAIL_DOMAIN"]
        if not (field.data or "").endswith("@" + domain):
            raise ValidationError(self.message)
