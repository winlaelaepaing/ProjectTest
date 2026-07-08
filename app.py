import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# Database URL ကို စစ်မယ်။ 
# Render မှာဆိုရင် DATABASE_URL ကို ရွေးမယ်၊ မရှိရင် Windows အတွက် SQLite ကို သုံးမယ်။
db_url = os.environ.get('DATABASE_URL')

if db_url:
    # Render အတွက် (PostgreSQL URL မှာ postgres:// ပါရင် postgresql:// နဲ့ အစားထိုးမှ အလုပ်လုပ်တတ်ပါတယ်)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    # Windows/Local အတွက် SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medicinestest.db'

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

# အဓိက Root
@app.route('/', methods=['GET'])
def index():
    return "Server is running successfully!"

# ဆေးဝါးအားလုံးကို ထုတ်ကြည့်ရန်
@app.route('/medicines', methods=['GET'])
def get_all_medicines():
    medicines = Medicine.query.all()
    output = []
    for m in medicines:
        output.append({
            "id": m.id,
            "name": m.name,
            "category": m.category,
            "description": m.description,
            "usage": m.usage
        })
    return jsonify(output)

# OCR အပိုင်း (Windows မှာပဲ အလုပ်လုပ်ပါမယ်)
# Tesseract ကို Windows မှာပဲ သုံးမှာမို့ ဒီမှာတင်ထားပါတယ်
try:
    import pytesseract
    from PIL import Image, ImageEnhance
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except:
    pass

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
            med = Medicine.query.filter(Medicine.name.ilike(f'%{word}%')).first()
            if med:
                return jsonify({"name": med.name, "category": med.category, "description": med.description, "usage": med.usage})
        
        return jsonify({"error": "ဆေးမတွေ့ရှိပါ", "detected": text}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Local မှာ စမ်းရင် port 8000 နဲ့ run ပါ
    app.run(host='0.0.0.0', port=8000, debug=True)