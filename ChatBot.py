from flask import Flask, render_template, request, session
from translate import Translator
import openai
from openai import ChatCompletion

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management
openai.api_key = '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'
model_engine = 'gpt-3.5-turbo'

def translate_text(input_text, source_lang, target_lang):
    translator = Translator(from_lang=source_lang, to_lang=target_lang)
    translation = translator.translate(input_text)
    return translation

def generate_response(question):
    user_input_en = translate_text(question, 'az', 'en')
    parts = user_input_en.split('?')
    bot_responses = []

    for part in parts:
        if part.strip():
            messages = [
                {"role": "user", "content": part + "?"}
            ]

            response = ChatCompletion.create(
                model=model_engine,
                messages=messages,
                max_tokens=50,
                n=1,
                stop=None,
                temperature=0.7
            )

            bot_response_en = response.choices[0].message.content.strip()

            if "OpenAI" in bot_response_en:
                bot_response_en = bot_response_en.replace("OpenAI", "Ferid & Rustam")

            bot_response = translate_text(bot_response_en, 'en', 'az')
            bot_responses.append(bot_response)

    return ' '.join(bot_responses)

@app.route('/')
def home():
    if 'conversation' not in session:
        session['conversation'] = []  # Initialize conversation for the session
    return render_template('index.html', conversation=session['conversation'])

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['user_input']
    session['conversation'].append(('İstifadəçi', user_input))

    response = generate_response(user_input)
    session['conversation'].append(('Bot', response))

    return render_template('index.html', conversation=session['conversation'])

@app.route('/restart_conversation', methods=['POST'])
def restart_conversation():
    session.pop('conversation', None)  # Remove conversation data from session
    return render_template('index.html', conversation=session['conversation'])

if __name__ == '__main__':
    app.run(debug=True)