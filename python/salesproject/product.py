from flask import Flask, render_template, redirect, request, url_for
from db_connection import get_connection
app= Flask(__name__)

@app.route("/",  methods=["GET", "POST"])
def productsection():
    conn = get_connection()
    cur  = conn.cursor()
    if request.method == "POST":
        product_Name = request.form.get("product_Name")
        Manufactura_Name = request.form.get("Manufactura_Name")
        product_ID =  request.form.get("Product_ID")
        bar_code =  request.form.get("bar_code")
        unit_price =  request.form.get("unit_price")
        insert = """INSERT INTO product  (product_Name, Manufactura_Name, Product_ID, bar_code, unit_price)  VALUES (%s, %s, %s, %s, %s)"""
        cur.execute(insert, (product_Name, Manufactura_Name, product_ID, bar_code, unit_price))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("productsection"))
    cur.execute("SELECT product_Name ,  Manufactura_Name, Product_ID , bar_code ,unit_price FROM product")

    users = cur.fetchall()
    return render_template("product.html", users=users)

@app.route("/delete/<int:Product_ID>", methods=["POST", "GET"])
def delete(Product_ID):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM product WHERE Product_ID = %s", (Product_ID,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("productsection"))

@app.route("/update/<int:Product_ID>", methods=["GET", "POST"])
def update(Product_ID):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        product_Name = request.form.get("product_Name")
        Manufactura_Name = request.form.get("Manufactura_Name")
        bar_code = request.form.get("bar_code")
        unit_price = request.form.get("unit_price")

        # ✅ use Product_ID from URL (not from form)
        cur.execute("""
            UPDATE product 
            SET product_Name=%s, Manufactura_Name=%s, bar_code=%s, unit_price=%s
            WHERE Product_ID=%s
        """, (product_Name, Manufactura_Name, bar_code, unit_price, Product_ID))

        conn.commit()
        cur.close()
        conn.close()
        return redirect("/")   # redirect to home after update

    # GET request → fetch current product data
    cur.execute("""
        SELECT product_Name, Manufactura_Name, Product_ID, bar_code, unit_price 
        FROM product 
        WHERE product_ID=%s
    """, (Product_ID,))
    
    user = cur.fetchone()
    cur.close()
    conn.close()
   
    return render_template("product_up.html", user=user)







if __name__ == "__main__":
    app.run(debug=True)


