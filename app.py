 
from flask import Flask, render_template, request, send_file
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "Dosya bulunamadı", 400
    
    file = request.files['file']
    marketplace = request.form.get('marketplace')  # Pazaryeri seçimi

    if file.filename == "":
        return "Dosya seçilmedi", 400

    if not marketplace:
        return "Lütfen bir pazaryeri seçin", 400

    try:
        # CSV dosyasını oku (Otto dosyalarında genellikle ";" ile ayrılmıştır)
        df = pd.read_csv(file, encoding="utf-8", sep=";" if marketplace == "otto" else ",")

        # Pazaryerine göre sütunları belirle
        if marketplace == "amazon":
            possible_order_id = ["Order ID", "Sipariş No."]
            possible_total_product_charges = ["Total Product Charges", "Toplam ürün fiyatları"]
            possible_other = ["Other", "Diğer"]
        elif marketplace == "otto":
            possible_order_id = ["Auftragsnummer"]  # Otto için sipariş numarası
            possible_total = ["Betrag"]  # Otto için toplam tutar

        # Dosyanın içindeki gerçek sütun isimlerini bul
        found_order_id = next((col for col in possible_order_id if col in df.columns), None)

        if marketplace == "amazon":
            found_total_product_charges = next((col for col in possible_total_product_charges if col in df.columns), None)
            found_other = next((col for col in possible_other if col in df.columns), None)
        elif marketplace == "otto":
            found_total = next((col for col in possible_total if col in df.columns), None)

        # Eğer gerekli sütunlar varsa işlemi yap
        if found_order_id:
            df_result = pd.DataFrame()
            df_result["Order ID"] = df[found_order_id]

            if marketplace == "amazon":
                # Eğer "Toplam ürün fiyatları" ve "Diğer" sütunları varsa topla
                if found_total_product_charges and found_other:
                    df_result["Total"] = df[found_total_product_charges] + df[found_other]
                elif found_total_product_charges:  # Sadece "Toplam ürün fiyatları" varsa
                    df_result["Total"] = df[found_total_product_charges]
                elif found_other:  # Sadece "Diğer" varsa
                    df_result["Total"] = df[found_other]
                else:
                    return "Gerekli sütunlar bulunamadı", 400  # İkisinden biri olmalı
            elif marketplace == "otto":
                if found_total:
                    # Otto'nun "Betrag" sütunundaki yanlış sayı formatını düzelt
                    df_result["Total"] = df[found_total].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)
                else:
                    return "Gerekli sütunlar bulunamadı", 400

            # Boş veya "---" olan satırları kaldır + NaN değerleri sil
            df_result = df_result.dropna(subset=["Order ID"])  # NaN olanları kaldır
            df_result = df_result[~df_result["Order ID"].astype(str).str.strip().isin(["", "---"])]  # Boş veya "---" olanları kaldır

            output_path = 'output.xlsx'
            df_result.to_excel(output_path, index=False)

            return send_file(output_path, as_attachment=True)
        else:
            return "Gerekli sütunlar bulunamadı", 400

    except Exception as e:
        return f"Hata oluştu: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
