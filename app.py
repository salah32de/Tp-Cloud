from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

# 🔑 قراءة API Key من متغيرات البيئة في Render
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

@app.route('/')
def home():
    return jsonify({
        "message": "🤖 LLM API يعمل بنجاح!",
        "status": "online",
        "groq_configured": bool(GROQ_API_KEY),
        "endpoints": {
            "chat": "/api/chat (POST)",
            "health": "/health (GET)"
        }
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "✅ API يعمل", 
        "groq_configured": bool(GROQ_API_KEY)
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "❌ أرسل 'message' في body"}), 400
        
        user_message = data['message']
        model = data.get('model', 'llama-3.1-70b-versatile')
        
        # وضع المحاكاة إذا لم يكن هناك API Key
        if not GROQ_API_KEY:
            return jsonify({
                "response": f"📝 (وضع المحاكاة) أنت قلت: {user_message}\n\n⚠️ أضف GROQ_API_KEY في Environment Variables في Render",
                "mode": "simulation",
                "model": model
            })
        
        # إرسال الطلب إلى Groq
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "أنت مساعد ذكي. تجيب بلغة السؤال."},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                "response": result['choices'][0]['message']['content'],
                "model": model,
                "usage": result.get('usage', {})
            })
        else:
            return jsonify({
                "error": f"❌ خطأ من Groq: {response.status_code}",
                "details": response.text
            }), 500
            
    except Exception as e:
        return jsonify({"error": f"❌ خطأ داخلي: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
