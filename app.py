import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# ဤနေရာတွင် Project ရဲ့ လက်ရှိတည်နေရာကို အလိုအလျောက်ရှာပေးသည်
basedir = os.path.abspath(os.path.dirname(__file__))

# Database URL ကို စစ်မယ်
db_url = os.environ.get('DATABASE_URL')

if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    
    db_path = os.path.join(basedir, 'medicinestest.db')
    # Render မှာဖြစ်စေ၊ Windows မှာဖြစ်စေ Database ဖိုင်ကို အမြဲရှာတွေ့စေမည့် Path
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

# --- OCR အပိုင်း (Render အတွက် Tesseract ကို Linux မှာ သုံးရန်) ---
try:
    import pytesseract
    from PIL import Image, ImageEnhance
    
    # Windows မှာဆိုရင် path ကို ထည့်ပေးထားပါ
    if os.name == 'nt':
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except:
    pass

@app.route('/', methods=['GET'])
def index():
    return "Server is running successfully!"

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    
    file = request.files['file']
    try:
        img = Image.open(file).convert('L')
        img = ImageEnhance.Contrast(img).enhance(2)
        text = pytesseract.image_to_string(img)
        
        # Database ထဲမှာ ရှာမယ်
        for word in text.split():
            # word အရှည် (၃) လုံးထက်ကျော်မှ ရှာပါ (Error နည်းစေရန်)
            if len(word) > 3:
                med = Medicine.query.filter(Medicine.name.ilike(f'%{word}%')).first()
                if med:
                    return jsonify({"name": med.name, "category": med.category, "description": med.description, "usage": med.usage})
        
        return jsonify({"error": "ဆေးမတွေ့ရှိပါ", "detected": text}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)