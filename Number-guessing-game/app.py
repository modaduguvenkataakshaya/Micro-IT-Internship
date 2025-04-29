from flask import Flask, render_template, request, session
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Use a secure random key in production

@app.route('/', methods=['GET', 'POST'])
def game():
    # Handle new game request first
    if request.method == 'POST' and 'new_game' in request.form:
        session.clear()
        session['target_number'] = random.randint(1, 100)
        session['attempts'] = 0
        session['game_over'] = False
        session['message'] = "New game started! Guess a number between 1 and 100!"
    
    # Initialize game if not already started
    if 'target_number' not in session:
        session['target_number'] = random.randint(1, 100)
        session['attempts'] = 0
        session['game_over'] = False
        session['message'] = "Guess a number between 1 and 100!"
    
    # Handle guess submission
    elif request.method == 'POST' and not session['game_over']:
        try:
            guess = int(request.form['guess'])
            session['attempts'] += 1
            
            if guess < session['target_number']:
                session['message'] = f"Too low! Try a higher number. (Attempts: {session['attempts']})"
            elif guess > session['target_number']:
                session['message'] = f"Too high! Try a lower number. (Attempts: {session['attempts']})"
            else:
                session['message'] = f"🎉 Congratulations! You guessed it in {session['attempts']} attempts!"
                session['game_over'] = True
        except ValueError:
            session['message'] = "⚠️ Please enter a valid number between 1 and 100."

    return render_template(
        'game.html',
        message=session['message'],
        game_over=session.get('game_over', False),
        attempts=session.get('attempts', 0)
    )

if __name__ == '__main__':
    app.run(debug=True)
