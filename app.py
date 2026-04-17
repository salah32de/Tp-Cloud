from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

# 🔑 API Key من متغيرات البيئة
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# واجهة الدردشة HTML
CHAT_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 مساعد الذكاء الاصطناعي</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chat-container {
            width: 90%;
            max-width: 800px;
            height: 90vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .chat-header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
            gap: 10px;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            flex-direction: row-reverse;
        }
        
        .message-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            flex-shrink: 0;
        }
        
        .message.user .message-avatar {
            background: #667eea;
        }
        
        .message.bot .message-avatar {
            background: #28a745;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            line-height: 1.6;
            word-wrap: break-word;
        }
        
        .message.user .message-content {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        .message.bot .message-content {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 4px;
        }
        
        .message.loading .message-content {
            background: #f0f0f0;
            color: #666;
        }
        
        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 5px 0;
        }
        
        .typing-indicator span {
            width: 8px;
            height: 8px;
            background: #999;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        
        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        
        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .chat-input-wrapper {
            display: flex;
            gap: 10px;
        }
        
        #messageInput {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        #messageInput:focus {
            border-color: #667eea;
        }
        
        #sendButton {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        #sendButton:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        #sendButton:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .model-selector {
            padding: 10px 20px;
            background: #f8f9fa;
            border-top: 1px solid #e0e0e0;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 14px;
        }
        
        .model-selector label {
            color: #666;
        }
        
        .model-selector select {
            padding: 5px 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background: white;
            cursor: pointer;
        }
        
        .welcome-message {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .welcome-message h2 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .error-message {
            background: #fee !important;
            color: #c33 !important;
            border-color: #fcc !important;
        }
        
        /* شريط التمرير */
        .chat-messages::-webkit-scrollbar {
            width: 8px;
        }
        
        .chat-messages::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        
        .chat-messages::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 4px;
        }
        
        .chat-messages::-webkit-scrollbar-thumb:hover {
            background: #a1a1a1;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 مساعد الذكاء الاصطناعي</h1>
            <p>اسألني أي شيء - أجيب بالعربية والإنجليزية</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="welcome-message">
                <h2>👋 مرحباً!</h2>
                <p>أنا هنا للمساعدة. ابدأ المحادثة بالأسفل.</p>
            </div>
        </div>
        
        <div class="model-selector">
            <label>🧠 النموذج:</label>
            <select id="modelSelect">
                <option value="llama-3.1-70b-versatile">Llama 3.1 70B (الأقوى)</option>
                <option value="llama-3.1-8b-instant">Llama 3.1 8B (الأسرع)</option>
                <option value="mixtral-8x7b-32768">Mixtral 8x7B</option>
                <option value="gemma2-9b-it">Gemma 2 9B</option>
            </select>
        </div>
        
        <div class="chat-input-container">
            <div class="chat-input-wrapper">
                <input 
                    type="text" 
                    id="messageInput" 
                    placeholder="اكتب رسالتك هنا..." 
                    autocomplete="off"
                >
                <button id="sendButton">إرسال</button>
            </div>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const modelSelect = document.getElementById('modelSelect');
        
        let isLoading = false;
        
        // إضافة رسالة للشات
        function addMessage(text, sender, isError = false) {
            const welcomeMessage = document.querySelector('.welcome-message');
            if (welcomeMessage) {
                welcomeMessage.remove();
            }
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = sender === 'user' ? '👤' : '🤖';
            
            const content = document.createElement('div');
            content.className = 'message-content';
            if (isError) content.classList.add('error-message');
            content.textContent = text;
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(content);
            chatMessages.appendChild(messageDiv);
            
            scrollToBottom();
        }
        
        // إضافة مؤشر الكتابة
        function addTypingIndicator() {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot loading';
            messageDiv.id = 'typingIndicator';
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = '🤖';
            
            const content = document.createElement('div');
            content.className = 'message-content';
            content.innerHTML = `
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            `;
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(content);
            chatMessages.appendChild(messageDiv);
            
            scrollToBottom();
        }
        
        // إزالة مؤشر الكتابة
        function removeTypingIndicator() {
            const indicator = document.getElementById('typingIndicator');
            if (indicator) indicator.remove();
        }
        
        // التمرير للأسفل
        function scrollToBottom() {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        // إرسال الرسالة
        async function sendMessage() {
            const text = messageInput.value.trim();
            if (!text || isLoading) return;
            
            // إضافة رسالة المستخدم
            addMessage(text, 'user');
            messageInput.value = '';
            messageInput.focus();
            
            // مؤشر الكتابة
            isLoading = true;
            sendButton.disabled = true;
            addTypingIndicator();
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: text,
                        model: modelSelect.value
                    })
                });
                
                const data = await response.json();
                removeTypingIndicator();
                
                if (data.error) {
                    addMessage(data.error, 'bot', true);
                } else {
                    addMessage(data.response, 'bot');
                }
                
            } catch (error) {
                removeTypingIndicator();
                addMessage('❌ حدث خطأ في الاتصال. حاول مرة أخرى.', 'bot', true);
            }
            
            isLoading = false;
            sendButton.disabled = false;
        }
        
        // الأحداث
        sendButton.addEventListener('click', sendMessage);
        
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // التركيز التلقائي
        messageInput.focus();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """الصفحة الرئيسية - واجهة الدردشة"""
    return render_template_string(CHAT_HTML)

@app.route('/health')
def health():
    """فحص الحالة"""
    return jsonify({
        "status": "✅ API يعمل",
        "groq_configured": bool(GROQ_API_KEY)
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """API الدردشة"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "❌ أرسل 'message' في body"}), 400
        
        user_message = data['message']
        model = data.get('model', 'llama-3.1-70b-versatile')
        
        # وضع المحاكاة إذا لم يكن هناك API Key
        if not GROQ_API_KEY:
            return jsonify({
                "response": f"📝 (وضع المحاكاة) أنت قلت: {user_message}\n\n⚠️ أضف GROQ_API_KEY في Environment Variables",
                "mode": "simulation"
            })
        
        # إرسال الطلب إلى Groq
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "أنت مساعد ذكي متعدد اللغات. تجيب بلغة السؤال (عربي/إنجليزي)."},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
        
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
        return jsonify({"error": f"❌ خطأ: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
