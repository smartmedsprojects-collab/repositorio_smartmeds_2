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

def validar_CPF(cnpj):
    if len(cnpj) == 14:
        return {"valida": False, "mensagem": "O Cnpj deve conter pelo menos 14 caracteres"}

def validar_nome(nome):
    
    if len(nome)<3:
        return{"valida":False,"mensagem":"o nome deve conter pelo menos 3 ou mais caracteres"}
     
    tem_maiuscula=False
    for caractere in nome:
        if caractere.isdigit():
            tem_maiuscula=True
            break
        if not tem_maiuscula:
            return{"valida": False, "mensagem": "A senha deve ter pelo menos uma letra maiúscula."}
        
def validar_email(email):
    if len(email) < 3:
        return {"valida": False, "mensagem": "O email deve ter pelo menos 3 caracteres antes do @ e 3 depois do @"}
    tem_arroba = False
    for caractere in email:
        if caractere.isdigit():
            tem_arroba= True
            break
    if not tem_arroba:
        return {"valida": False, "mensagem": "O email deve ter @"}
    tem_caracteres = False
    for caractere in email:
        if caractere.isupper():
            tem_caracteres = True
            break
    if not tem_caracteres:
        return {"valida": False, "mensagem": "A senha deve ter @."}
    return {"valida": True, "mensagem": "Email válida!"}

def vailadar_fornecedor(cnpj,nome, email):
    validar_email(email)
    validar_CPF(cnpj)
    validar_nome(nome)
    