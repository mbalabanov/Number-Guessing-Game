import random
from flask import Flask, render_template, request, make_response, redirect, url_for
from model import User, db

app = Flask(__name__)
db.create_all()

# <a style="background-color:black;color:white;text-decoration:none;padding:4px 6px;font-family:-apple-system, BlinkMacSystemFont, &quot;San Francisco&quot;, &quot;Helvetica Neue&quot;, Helvetica, Ubuntu, Roboto, Noto, &quot;Segoe UI&quot;, Arial, sans-serif;font-size:12px;font-weight:bold;line-height:1.2;display:inline-block;border-radius:3px" href="https://unsplash.com/@rihok?utm_medium=referral&amp;utm_campaign=photographer-credit&amp;utm_content=creditBadge" target="_blank" rel="noopener noreferrer" title="Download free do whatever you want high-resolution photos from Riho Kroll"><span style="display:inline-block;padding:2px 3px"><svg xmlns="http://www.w3.org/2000/svg" style="height:12px;width:auto;position:relative;vertical-align:middle;top:-2px;fill:white" viewBox="0 0 32 32"><title>unsplash-logo</title><path d="M10 9V0h12v9H10zm12 5h10v18H0V14h10v9h12v-9z"></path></svg></span><span style="display:inline-block;padding:2px 3px">Riho Kroll</span></a>

@app.route("/", methods=["GET"])
def index():
    email = request.cookies.get("email")

    if email:
        user = db.query(User).filter_by(email=email).first()
    else:
        user = None

    return render_template("index.html", user=user)

@app.route("/initiate", methods=["POST"])
def initiate():

    # Input aus dem Login/Registrierungsformular
    name = request.form.get("name")
    email = request.form.get("email")
    secret = random.randint(1, 50)

    # User in Datenbank finden
    user = db.query(User).filter_by(email=email).first()

    # User hinzufügen, falls noch nicht vorhanden
    if not user:
        user = User(name=name, email=email, secret=secret)
        db.add(user)
        db.commit()

    # User Email-Adresse als Cookie eintragen (ist aber eine böse Lösung)
    response = make_response(redirect(url_for('game')))
    response.set_cookie("email", email)
    return response

@app.route("/logout")
def logout():
        delcookie = make_response(render_template("index.html"))
        delcookie.delete_cookie('email')
        return delcookie

@app.route("/game")
def game():
    # Nachprüfen, ob der User eh eingeloggt ist.
    email = request.cookies.get("email")
    user = db.query(User).filter_by(email=email).first()
    return render_template("game.html")

@app.route("/results", methods=["POST"])
def results():
    guess = int(request.form.get("guess"))

    # Nachprüfen, ob der User eh eingeloggt ist.
    email = request.cookies.get("email")
    user = db.query(User).filter_by(email=email).first()

    if guess == user.secret:
        smessage = 'Congratulations!'
        message = "Your guess is right! {0} is the secret number.".format(str(guess))
        new_secret = random.randint(1, 50)
        user.secret = new_secret
        db.add(user)
        db.commit()

    elif guess > user.secret:
        message = "Too high, the secret number is smaller."
        smessage = "Lower!"

    elif guess < user.secret:
        message = "Too low, the secret number is bigger."
        smessage = "Higher!"

    return render_template("results.html", message=message, successmessage=smessage)

if __name__ == '__main__':
    app.run(debug=True)