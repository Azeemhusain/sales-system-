
from flask import Flask, render_template, redirect, url_for, request
from salesproject.db_files.db_connection import get_connection

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def login():
    conn = get_connection()
    cur = conn.cursor()
    if request.method == "POST":
        f_name = request.form.get("First_Name")
        l_name = request.form.get("Last_Name")
        email = request.form.get("Email_Address")
        password = request.form.get("Password")
        gender = request.form.get("Gender")

        insert = """INSERT INTO login_form (First_Name, Last_Name, Email_Address, Password, Gender)
                    VALUES (%s, %s, %s, %s, %s)"""
        cur.execute(insert, (f_name, l_name, email, password, gender))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("login"))

    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
