from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

app = Flask(__name__)
CORS(app)  # السماح بالوصول من أي مصدر

# إعدادات API الخارجي (Groq - مجاني وسريع)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

@app.route('/')
def home():
    return jsonify({
        "message": "🤖 LLM API جاهز للاستخدام!",
        "endpoints": {
            "chat": "/api/chat (POST)",
            "models": "/api/models (GET)",
            "health": "/health (GET)"
        },
        "docs": "أرسل POST إلى /api/chat مع JSON يحتوي على 'message'"
    })

@app.route('/health')
def health():
    return jsonify({"status": "✅ API يعمل بنجاح"})

@app.route('/api/models')
def get_models():
    """الحصول على قائمة النماذج المتاحة"""
    models = [
        {"id": "llama-3.1-70b-versatile", "name": "Llama 3.1 70B", "provider": "Meta"},
        {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B", "provider": "Meta"},
        {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B", "provider": "Mistral"},
        {"id": "gemma2-9b-it", "name": "Gemma 2 9B", "provider": "Google"}
    ]
    return jsonify({"models": models})

@app.route('/api/chat', methods=['POST'])
def chat():
    """الدردشة مع LLM"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "❌ يرجى إرسال 'message' في body"}), 400
        
        user_message = data['message']
        model = data.get('model', 'llama-3.1-70b-versatile')
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 1000)
        
        # إذا لم يكن هناك مفتاح API، نعيد رسالة توضيحية
        if not GROQ_API_KEY:
            return jsonify({
                "response": f"📝 (وضع المحاكاة) أنت قلت: {user_message}\n\n⚠️ أضف GROQ_API_KEY في متغيرات البيئة لتفعيل الردود الحقيقية",
                "model": "simulation-mode",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0}
            })
        
        # إرسال الطلب إلى Groq API
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "أنت مساعد ذكي متعدد اللغات. تجيب بالعربية أو الإنجليزية حسب لغة السؤال."},
                {"role": "user", "content": user_message}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                "response": result['choices'][0]['message']['content'],
                "model": model,
                "usage": result.get('usage', {}),
                "finish_reason": result['choices'][0].get('finish_reason')
            })
        else:
            return jsonify({
                "error": f"❌ خطأ من API الخارجي: {response.status_code}",
                "details": response.text
            }), 500
            
    except Exception as e:
        return jsonify({"error": f"❌ خطأ داخلي: {str(e)}"}), 500

# للتشغيل المحلي
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)