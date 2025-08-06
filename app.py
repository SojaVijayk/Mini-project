# If you see "Import 'flask_mysqldb' could not be resolved", install it with:
# pip install flask-mysqldb

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__, template_folder="app/templates")
app.secret_key = "your_secret_key"  # Needed for flash messages

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_mysql_user'
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
app.config['MYSQL_DB'] = 'your_database_name'

mysql = MySQL(app)

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user_table WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        cur.close()
        if user:
            return redirect(url_for("landing"))
        else:
            flash("Invalid username or password", "error")
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
