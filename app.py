from flask import Flask, render_template, request, jsonify, send_file
import math
import random
import base64
import io # Importante para manejar archivos en memoria

app = Flask(__name__)

# --- FUNCIONES RSA (TU CÓDIGO PYTHON) ---
# Mantén estas funciones como están, son las mismas que en la versión anterior
def gen_primos():
    x = random.randint(10, 50)
    for i in range(2, int(math.sqrt(x)) + 1):
        if x % i == 0:
            return gen_primos()
    if x <= 10:
        return gen_primos()
    return x

def condicion(EcEuler):
    d = random.randint(2, EcEuler - 1)
    if (math.gcd(d, EcEuler) == 1):
        return d
    else:
        return condicion(EcEuler)

def generar_claves_rsa_para_web():
    p, q = 0, 0
    while True:
        p = gen_primos()
        q = gen_primos()
        if p != q and p*q > 255:
            break

    n = p * q
    EcEuler = (p - 1) * (q - 1)

    e = 0
    d = 0
    while True:
        e = random.randint(2, EcEuler - 1)
        if math.gcd(e, EcEuler) == 1:
            try:
                d = pow(e, -1, EcEuler)
                if e != d:
                    break
            except ValueError:
                continue
    return p, q, n, e, d, EcEuler

# --- RUTAS DE NAVEGACIÓN ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fundamento_teorico')
def fundamento_teorico():
    return render_template('fundamento_teorico.html')

@app.route('/ejecutar_programa')
def ejecutar_programa():
    return render_template('ejecutar_programa.html')

@app.route('/mi_equipo')
def mi_equipo():
    return render_template('mi_equipo.html')

# --- NUEVAS RUTAS PARA LA LÓGICA RSA CON SUBIDA DE ARCHIVOS ---

@app.route('/api/encrypt_file', methods=['POST'])
def encrypt_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

    if file:
        try:
            # Lee el contenido del archivo subido
            plaintext = file.read().decode('utf-8')
        except UnicodeDecodeError:
            return jsonify({'error': 'El archivo no es un texto UTF-8 válido'}), 400

        p, q, n, e, d, EcEuler = generar_claves_rsa_para_web()

        M = list(plaintext)
        C = []
        char_to_ascii_encrypted_details = []

        for char in M:
            ascii_val = ord(char)
            # Asegurarse de que el valor ASCII esté dentro del rango de n para el cifrado
            if ascii_val >= n:
                 return jsonify({'error': f'El carácter "{char}" (ASCII: {ascii_val}) es demasiado grande para la clave n ({n}). Por favor, elige primos más grandes o un texto con ASCII más bajos.'}), 400
            encrypted_val = pow(ascii_val, e, n)
            C.append(encrypted_val)
            char_to_ascii_encrypted_details.append({
                'char': char,
                'ascii': ascii_val,
                'encrypted': encrypted_val
            })

        byte_array = b''.join(val.to_bytes(4, byteorder='big') for val in C)
        base64_encoded_cipher = base64.b64encode(byte_array).decode('utf-8')

        # Contenido del archivo encriptado que se descargará
        encrypted_file_content = f'{n},{d}\n{base64_encoded_cipher}'

        # Preparar el archivo para descarga en memoria
        buffer = io.BytesIO(encrypted_file_content.encode('utf-8'))
        buffer.seek(0) # Mover el cursor al inicio del buffer

        return jsonify({
            'encrypted_message_base64_display': encrypted_file_content, # Para mostrar en textarea
            'private_key_for_display': f'{n},{d}', # Para mostrar en campo de descifrado
            'file_content_base64': base64.b64encode(buffer.getvalue()).decode('utf-8'), # Contenido completo del archivo para JS
            'public_key': f'{n},{e}',
            'p': p,
            'q': q,
            'n': n,
            'e': e,
            'd': d,
            'euler_phi': EcEuler,
            'char_details': char_to_ascii_encrypted_details
        })

@app.route('/api/decrypt_file', methods=['POST'])
def decrypt_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

    if file:
        try:
            encrypted_file_content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            return jsonify({'error': 'El archivo no es un texto UTF-8 válido'}), 400

        # Parsear el contenido del archivo: primera línea es clave, segunda es mensaje
        lines = encrypted_file_content.split('\n', 1)
        if len(lines) < 2:
            return jsonify({'error': 'Formato de archivo cifrado incorrecto. Debe contener clave y mensaje.'}), 400

        private_key_str = lines[0]
        encrypted_message_base64 = lines[1]

        try:
            n_str, d_str = private_key_str.split(',')
            n = int(n_str)
            d = int(d_str)
        except ValueError:
            return jsonify({'error': 'Formato de clave privada incorrecto en el archivo. Debe ser "n,d"'}), 400

        try:
            byte_array = base64.b64decode(encrypted_message_base64)
        except Exception as e:
            return jsonify({'error': f'Error al decodificar Base64 del mensaje cifrado: {e}'}), 400

        CC = []
        for i in range(0, len(byte_array), 4):
            num = int.from_bytes(byte_array[i: i + 4], byteorder='big')
            CC.append(num)

        D = []
        char_decrypted_details = []

        for encrypted_val in CC:
            try:
                decrypted_ascii = pow(encrypted_val, d, n)
                decrypted_char = chr(decrypted_ascii)
                D.append(decrypted_char)
                char_decrypted_details.append({
                    'encrypted_val': encrypted_val,
                    'decrypted_ascii': decrypted_ascii,
                    'decrypted_char': decrypted_char
                })
            except OverflowError: # Si el resultado es demasiado grande para chr() o hay un problema con la clave
                return jsonify({'error': f'Error de desbordamiento o clave incorrecta para valor cifrado {encrypted_val}. Posiblemente clave incorrecta o mensaje corrupto.'}), 400
            except ValueError: # Si chr() recibe un valor fuera del rango ASCII/Unicode
                return jsonify({'error': f'Valor ASCII descifrado fuera de rango para el carácter {encrypted_val}. Posiblemente clave incorrecta o mensaje corrupto.'}), 400


        decrypted_message = ''.join(D)

        # Preparar el archivo para descarga en memoria
        buffer = io.BytesIO(decrypted_message.encode('utf-8'))
        buffer.seek(0)

        return jsonify({
            'decrypted_message_display': decrypted_message, # Para mostrar en textarea
            'file_content_base64': base64.b64encode(buffer.getvalue()).decode('utf-8'), # Contenido completo del archivo para JS
            'char_details': char_decrypted_details
        })

if __name__ == '__main__':
    app.run(debug=True)