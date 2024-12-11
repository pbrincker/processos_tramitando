from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime
import os

def numero_por_extenso(numero):
    if not numero:
        return 'zero'
        
    try:
        numero = float(numero)
    except (ValueError, TypeError):
        return str(numero)
        
    if numero == 0:
        return 'zero'
    
    parte_inteira = int(numero)
    parte_decimal = int((numero - parte_inteira) * 100)
    
    unidades = ['', 'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove']
    dezenas = ['', 'dez', 'vinte', 'trinta', 'quarenta', 'cinquenta', 'sessenta', 'setenta', 'oitenta', 'noventa']
    teens = ['dez', 'onze', 'doze', 'treze', 'quatorze', 'quinze', 'dezesseis', 'dezessete', 'dezoito', 'dezenove']
    centenas = ['', 'cento', 'duzentos', 'trezentos', 'quatrocentos', 'quinhentos', 'seiscentos', 'setecentos', 'oitocentos', 'novecentos']
    
    def converter_grupo(n):
        if n == 0:
            return ''
        elif n == 100:
            return 'cem'
            
        s = ''
        n_str = str(n).zfill(3)
        
        # Centenas
        if int(n_str[0]) > 0:
            s += centenas[int(n_str[0])]
            if int(n_str[1:]) > 0:
                s += ' e '
        
        # Dezenas e unidades
        dezena = int(n_str[1])
        unidade = int(n_str[2])
        
        if dezena == 1:  # Casos especiais (11-19)
            s += teens[unidade]
        else:
            if dezena > 0:
                s += dezenas[dezena]
                if unidade > 0:
                    s += ' e '
            if unidade > 0:
                s += unidades[unidade]
                
        return s.strip()
    
    texto = converter_grupo(parte_inteira)
    if parte_decimal > 0:
        texto += f' reais e {converter_grupo(parte_decimal)} centavos'
    else:
        texto += ' reais'
    
    return texto.strip()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Convert postgres:// to postgresql:// in database URL
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Parse and rebuild the URL with correct SSL parameters
    if '?' in database_url:
        base_url, params = database_url.split('?', 1)
        params = dict(param.split('=') for param in params.split('&'))
    else:
        base_url, params = database_url, {}
    
    # Set required SSL parameters
    params.update({
        'sslmode': 'require',
        'connect_timeout': '10',
        'keepalives': '1',
        'keepalives_idle': '30',
        'keepalives_interval': '10',
        'keepalives_count': '5',
        'sslcert': None
    })
    
    # Rebuild URL with parameters
    database_url = base_url + '?' + '&'.join(f"{k}={v}" for k, v in params.items())

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_timeout': 30,
    'pool_recycle': 1800,
    'max_overflow': 2
}

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
