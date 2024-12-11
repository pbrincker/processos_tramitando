from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime
import os

def numero_por_extenso(numero):
    unidades = ['', 'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove']
    dezenas = ['', 'dez', 'vinte', 'trinta', 'quarenta', 'cinquenta', 'sessenta', 'setenta', 'oitenta', 'noventa']
    teens = ['dez', 'onze', 'doze', 'treze', 'quatorze', 'quinze', 'dezesseis', 'dezessete', 'dezoito', 'dezenove']
    centenas = ['', 'cento', 'duzentos', 'trezentos', 'quatrocentos', 'quinhentos', 'seiscentos', 'setecentos', 'oitocentos', 'novecentos']
    
    if numero == 0:
        return 'zero'
    elif numero == 100:
        return 'cem'
    
    num_str = str(int(numero))
    length = len(num_str)
    
    if length == 1:
        return unidades[int(num_str)]
    elif length == 2:
        if int(num_str[0]) == 1:
            return teens[int(num_str[1])]
        else:
            return dezenas[int(num_str[0])] + (' e ' + unidades[int(num_str[1])] if int(num_str[1]) > 0 else '')
    elif length == 3:
        centena = centenas[int(num_str[0])]
        dezena = int(num_str[1:])
        if dezena == 0:
            return centena
        return centena + ' e ' + numero_por_extenso(dezena)
    else:
        return str(numero)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Convert postgres:// to postgresql:// in database URL
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    # Add sslmode=require only if not already present
    if 'sslmode=' not in database_url:
        database_url += "?sslmode=require"
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Registra o filtro personalizado
app.jinja_env.filters['number_to_words'] = numero_por_extenso

# Função para obter a data/hora atual no template
@app.context_processor
def utility_processor():
    return {'now': datetime.now}

from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
