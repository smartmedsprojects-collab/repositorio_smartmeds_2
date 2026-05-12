import re


class Validator:

    @staticmethod
    def required(value, field_name):

        if value is None or str(value).strip() == "":
            return f"O campo {field_name} é obrigatório."

        return None

    @staticmethod
    def non_negative(value, field_name):

        try:

            if float(value) < 0:
                return f"O campo {field_name} não pode ser negativo."

        except (TypeError, ValueError):

            return f"O campo {field_name} deve ser numérico."

        return None

    @staticmethod
    def positive(value, field_name):

        try:

            if int(value) <= 0:
                return f"O campo {field_name} deve ser maior que zero."

        except (TypeError, ValueError):

            return f"O campo {field_name} deve ser numérico."

        return None

    @staticmethod
    def min_length(value, field_name, size):

        if len(str(value).strip()) < size:
            return f"O campo {field_name} deve ter pelo menos {size} caracteres."

        return None

    @staticmethod
    def email(value):

        regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if not re.match(regex, value):
            return "Email inválido."

        return None

    @staticmethod
    def cnpj(value):

        cnpj = ''.join(filter(str.isdigit, str(value)))

        if len(cnpj) != 14:
            return "CNPJ inválido."

        return None

    @staticmethod
    def only_letters(value, field_name):

        if any(char.isdigit() for char in value):
            return f"O campo {field_name} não pode conter números."

        return None