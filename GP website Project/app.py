from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from nltk.chat.util import Chat, reflections
import os
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///RealExample.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#  user table model details
class users(db.Model):
    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(20))
    email = db.Column(db.String(30))
    FirstName = db.Column(db.String(15))
    LastName = db.Column(db.String(20))
    DateOfBirth = db.Column(db.String(10))
    Gender = db.Column(db.String(10))

# creating a table for storing chat responses
class chat_answer(db.Model):
    user_input = db.Column(db.String(255), primary_key=True)
    bot_response = db.Column(db.String(255))

# Loading NLTK chat data which will be used to by chatbot to response user queries.
def load_chat_pairs():
    pairs = [
        (
            r"(.*) your name",
            ["I am a Medicalbot.", "You can call me MedicalChatBot."]
        ),
        (
            r"how are you",
            ["I'm doing well, thank you!", "I'm just a computer program, so I don't have feelings, but I'm here to help."]
        ),
    ]

    # creating the chat_answer table if it doesn't exist
    with app.app_context():
        db.create_all()

        # checking if the Chat_answer table exists
        connection = db.engine.connect()
        table_exists = connection.dialect.has_table(connection, "chat_answer")
        connection.close()

        if not table_exists:
            #creating the chat_answer table
            db.session.execute('''
                CREATE TABLE IF NOT EXISTS chat_answer (
                    user_input TEXT PRIMARY KEY,
                    bot_response TEXT
                )
            ''')
            db.session.commit()

        # Combine NLTK chat pairs with responses from the database
        chat_rows = chat_answer.query.all()
        for row in chat_rows:
            user_input = row.user_input
            bot_response = [row.bot_response]
            pairs.append((user_input, bot_response))

    return pairs

# creating a chatbot
chatbot = Chat(load_chat_pairs(), reflections)

def generate_follow_up_question():
    return "Any more questions?"

# function to handle user input and get bot response with follow-up question
def get_bot_response(user_input):
    response = chatbot.respond(user_input)

    
    if response:
        follow_up_question = generate_follow_up_question()
        if follow_up_question:
            return f"{response}\n{follow_up_question}"

    if not response:
        response = "I'm sorry, I don't understand."

    return response  

# follow of how to display the results with response and follow-up question on separate lines
user_input = "Hello, chatbot!"
result = get_bot_response(user_input)

# displaying results on separate lines
print(result)

# displaying the results with response and follow-up question on separate lines
user_input = "Hello, chatbot!"
result = get_bot_response(user_input)

# Displaying results on separate lines
print(result)


# function to register a new user
def register_user(username, password, email, FirstName, LastName, DateOfBirth, Gender):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    new_user = users(
        username=username,
        password=hashed_password,
        email=email,
        FirstName=FirstName,
        LastName=LastName,
        DateOfBirth=DateOfBirth,
        Gender=Gender
    )
    db.session.add(new_user)
    db.session.commit()

# function to authenticate a user
def authenticate_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = users.query.filter_by(username=username, password=hashed_password).first()
    return user is not None

# routes to all the the pages connected to the webapp
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/diagnosis')
def diagnosis():
    return render_template('diagnosis.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if authenticate_user(username, password):
            return render_template('dashboard.html', username=username)
        else:
            return render_template('login.html', message='Invalid username or password. Please try again.')

    return render_template('login.html', message='')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        FirstName = request.form['FirstName']
        LastName = request.form['LastName']
        DateOfBirth = request.form['DateOfBirth']
        Gender = request.form['Gender']

        # checking if the username already exists
        if users.query.filter_by(username=username).first() is not None:
            return render_template('register.html', message='Username already in use. Please choose another one.')

        register_user(username, password, email, FirstName, LastName, DateOfBirth, Gender)
        return render_template('dashboard.html', username=username)

    return render_template('register.html', message='')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_input = request.form['user_input']
        bot_response = get_bot_response(user_input)
        return render_template('chat.html', user_input=user_input, bot_response=bot_response)

    return render_template('chat.html', user_input='', bot_response='', follow_up_question='')

if __name__ == '__main__':
    app.run(debug=True)

app = Flask(__name__)

@app.route('/index', methods=['GET', 'POST'])
def lionel(): 
    return render_template('index.html')


if __name__ == '__main__':
    app.run()



