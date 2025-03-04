import os
from flask import Flask, render_template, request, send_file
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Dosya formatlarını tanımla
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}

# Dosya formatını kontrol et
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    
    # Dosyanın geçerli formatta olup olmadığını kontrol et
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join('uploads', filename))

        # Dosya türünü kontrol et
        if filename.endswith('.csv'):
            df = pd.read_csv(os.path.join('uploads', filename))
        else:
            df = pd.read_excel(os.path.join('uploads', filename))

        # Veri işleme
        # Gerekli sütunları seç
        df = df[['Order ID', 'Total']]  # Örnek, ihtiyacınıza göre güncelleyebilirsiniz

        # Excel dosyasına dönüştür
        output_filename = os.path.join('uploads', 'output.xlsx')
        df.to_excel(output_filename, index=False)

        return send_file(output_filename, as_attachment=True)

    return 'Invalid file format'

if __name__ == '__main__':
    app.run(debug=True)
