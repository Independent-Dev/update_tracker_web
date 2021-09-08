from flask import Blueprint

NAME = 'user'
bp = Blueprint(NAME, __name__, url_prefix=f'/{NAME}')
