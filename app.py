import os
import sqlite3
import pytesseract
from PIL import Image, ImageEnhance
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Tesseract Path ကို အပေါ်မှာ သေချာသတ်မှတ်ပါ
#if os.name == 'nt':
    #pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)
CORS(app)

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
db_url = os.environ.get('DATABASE_URL')

if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'medicinestest.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Medicine(db.Model):
    __tablename__ = 'medicines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    category = db.Column(db.Text)
    description = db.Column(db.Text)
    usage = db.Column(db.Text)

@app.route('/', methods=['GET'])
def index():
    return "Server is running successfully!"

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    try:
        # Image Preprocessing
        img = Image.open(file).convert('L')
        img = ImageEnhance.Contrast(img).enhance(2)
        
        # OCR
        text = pytesseract.image_to_string(img)
        print(f"OCR ဖတ်လို့ရတဲ့စာသား: {text}")
        
        # Database Search
        # သင့်စက်ထဲက Database ဖိုင်လမ်းကြောင်းအမှန်ကို ထည့်ပါ
        db_path = r'C:\NewProjects\my_new_medicine_app\Backend_Python\medicinestest.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        found_data = None
        for word in text.split():
            if len(word) > 3:
                cursor.execute("SELECT name, category, description, usage FROM medicines WHERE name LIKE ?", ('%' + word.lower() + '%',))
                row = cursor.fetchone()
                if row:
                    found_data = {"name": row[0], "category": row[1], "description": row[2], "usage": row[3]}
                    break
        conn.close()
        
        if found_data:
            return jsonify(found_data)
        else:
            return jsonify({"error": "ဆေးမတွေ့ရှိပါ", "detected": text}), 404
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # ဖုန်းနဲ့ ချိတ်ဖို့အတွက် host 0.0.0.0 ကို သုံးပါ
    app.run(host='0.0.0.0', port=8000)