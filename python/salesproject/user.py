from flask import Flask, render_template, request , url_for , redirect
from db_connection import get_connection


app = Flask(__name__)


@app.route("/",  methods=["GET", "POST"])
def home():
    conn = get_connection()
    cur = conn.cursor()
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        international_id =  request.form.get("international_id")
        city = request.form.get("city")
        address = request.form.get("address")
        mobile = request.form.get("mobile")
       
        
        insert = "INSERT INTO verify (first_name, last_name , international_id,city , address ,mobile) VALUES (%s, %s, %s ,%s, %s, %s)"
        cur.execute(insert, (first_name, last_name, international_id , city , address ,mobile))
        conn.commit()   # commit only after insert
        cur.close()
        conn.close()
    # ✅ redirect after saving (stops resubmission warning)
        return redirect(url_for("home"))
    cur.execute("SELECT first_name, last_name , international_id , city , address , mobile FROM verify")

    users = cur.fetchall()
    return render_template("index.html", users=users)

@app.route("/delete/<int:international_id>", methods=["POST"  , "GET"])
def delete(international_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM verify WHERE international_id = %s", (international_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("home"))

@app.route("/update/<int:international_id>", methods=["GET", "POST"])
def update(international_id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        city = request.form.get("city")
        address = request.form.get("address")
        mobile = request.form.get("mobile")
        cur.execute("""
            UPDATE verify 
            SET first_name=%s, last_name=%s, city=%s, mobile=%s, address=%s
            WHERE international_id=%s
        """, (first_name, last_name, city, mobile, address, international_id))

        conn.commit()
        cur.close()
        conn.close()
        return redirect("/")   # back to home after update

    # GET request → show form with old data
    cur.execute("""
        SELECT first_name, last_name, international_id, mobile, city, address
        FROM verify WHERE international_id=%s
    """, (international_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    return render_template("update.html", user=user)
    # return render_template("index.html", users=users)
    


if __name__ == "__main__":
    app.run(debug=True)

