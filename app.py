from flask import Flask, request, jsonify
from services.waha import Waha
from bot.ai_bot import AIBot

app = Flask(__name__)

@app.route('/chatbot/webhook/', methods=['POST'])
def webhook():
    data = request.json
    print(f'EVENTO RECEBIDO: {data}')

    waha = Waha()
    bot = AIBot()
  
    chat_id = data['payload']['from']
    message = data['payload']['body']

    waha.start_typing(chat_id=chat_id)
    response = bot.invoke(question=message)

    waha.send_message(
    chat_id=chat_id,
    message=response,

 )
    waha.stop_typing(chat_id=chat_id)
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
 
 app.run(host='0.0.0.0', port=5000, debug=True)