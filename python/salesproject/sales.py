
from flask import Flask, render_template, redirect, request, url_for , flash
from db_connection import get_connection
from datetime import date
import os 
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = os.urandom(24) 

@app.route("/", methods=["GET", "POST"])

def sales():
    conn = get_connection()
    cur = conn.cursor()

    # Fetch lookup data for dropdowns
    cur.execute("SELECT product_ID, product_Name FROM product")
    products = cur.fetchall()  # 👈 Keep this list for template dropdown
    product_lookup = {row[0]: row[1] for row in products}

    cur.execute("SELECT international_id, first_name, last_name FROM verify")
    customers = cur.fetchall()  # 👈 Keep this list for template dropdown
    customer_lookup = {row[0]: row[1] for row in customers}

    if request.method == "POST":
        quantity = request.form.get("quantity")
        unit_price = request.form.get("unit_price")
        sales_id = request.form.get("sales_id")
        total_price = request.form.get("total_price")
        sale_date = request.form.get("sale_date") or date.today()
        cash_received = request.form.get("cash_received")
        remaining_amount = request.form.get("remaining_amount")
        international_id = int(request.form.get("User"))
        Product_ID = int(request.form.get("product_name"))
        product_Name = product_lookup.get(Product_ID)
        first_name = customer_lookup.get(international_id)

        insert = """
            INSERT INTO sales 
            (quantity, unit_price, sales_id, total_price, sale_date, cash_received, remaining_amount, Product_ID, international_id , product_Name ,first_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s , %s , %s , %s)
        """
        cur.execute(insert, (
            quantity, unit_price, sales_id, total_price, sale_date,
            cash_received, remaining_amount, Product_ID, international_id ,product_Name ,first_name
        ))
        conn.commit()
        return redirect(url_for("sales"))

    # Fetch all sales
    cur.execute("""
        SELECT quantity, unit_price, total_price, sale_date, cash_received, 
               remaining_amount, sales_id, Product_ID, international_id , first_name , product_Name
        FROM sales
    """)
    all_sales = cur.fetchall()

    # Replace IDs with names
    sales_data = []
    for s in all_sales:
        row = list(s)
        Product_ID = s[7]
        international_id = s[8]
        row.append(product_lookup.get(Product_ID, "Unknown Product"))
        row.append(customer_lookup.get(international_id, "Unknown Customer"))
        sales_data.append(row)

    cur.close()
    conn.close()

    return render_template(
        "sales.html",
        sales=sales_data,
        users=products,  # 👈 for product dropdown
        user=customers   # 👈 for customer dropdown
    )



@app.route("/delete/<sales_id>", methods=["POST", "GET"])
def delete(sales_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sales WHERE sales_id = %s", (sales_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("sales"))

@app.route("/updatesales/<sales_id>", methods=["POST", "GET"])
def update(sales_id):
    conn = get_connection()
    cur = conn.cursor()

    # Fetch lookup data
    cur.execute("SELECT product_id, product_Name FROM product")
    product = cur.fetchall()
    product_lookup = {row[0]: row[1] for row in product}

    cur.execute("SELECT international_id, first_name, last_name FROM verify")
    customer = cur.fetchall()
    customer_lookup = {row[0]: row[1] for row in customer}

    if request.method == "POST":
        # ✅ Use route parameter `sales_id` (do NOT override it)
        quantity = request.form.get("quantity")
        unit_price = request.form.get("unit_price")
        total_price = request.form.get("total_price")
        sale_date = request.form.get("sale_date") or date.today()
        cash_received = request.form.get("cash_received")
        remaining_amount = request.form.get("remaining_amount")
        international_id = int(request.form.get("User"))
        Product_ID = int(request.form.get("product_name"))
        product_Name = product_lookup.get(Product_ID)
        first_name = customer_lookup.get(international_id)

        # ✅ Safe update query (no insert, no PK modification)
        update_query = """
            UPDATE sales 
            SET quantity=%s,
                unit_price=%s,
                total_price=%s,
                sale_date=%s,
                cash_received=%s,
                remaining_amount=%s,
                Product_ID=%s,
                international_id=%s,
                product_Name=%s,
                first_name=%s
            WHERE sales_id=%s
        """
        cur.execute(update_query, (
            quantity, unit_price, total_price, sale_date, cash_received,
            remaining_amount, Product_ID, international_id, product_Name,
            first_name, sales_id  # use route parameter
        ))
        conn.commit()
        return redirect(url_for("sales"))

    # Fetch the record to pre-fill the form
    cur.execute("""
        SELECT quantity, unit_price, total_price, sale_date, cash_received, 
               remaining_amount, sales_id, Product_ID, international_id
        FROM sales WHERE sales_id=%s
    """, (sales_id,))
    current_sale = cur.fetchone()

    # Fetch all sales for the table list
    cur.execute("""
        SELECT quantity, unit_price, total_price, sale_date, cash_received, 
               remaining_amount, sales_id, Product_ID, international_id, first_name, product_Name
        FROM sales
    """)
    all_sales = cur.fetchall()

    sales_data = []
    for s in all_sales:
        row = list(s)
        Product_ID = s[7]
        international_id = s[8]
        row.append(product_lookup.get(Product_ID, "Unknown Product"))
        row.append(customer_lookup.get(international_id, "Unknown Customer"))
        sales_data.append(row)

    cur.close()
    conn.close()

    return render_template(
        "sales.html",
        sales=sales_data,
        users=product,
        user=customer,
        current_sale=current_sale
    )



# ---------- FUNCTION: GET LOOKUPS FROM DATABASE ----------
# ---------- FUNCTION: GET LOOKUPS FROM DATABASE ----------
def get_lookups():
    conn = get_connection()
    cur = conn.cursor()

    # Fetch product lookup
    cur.execute("SELECT product_ID, product_Name FROM product")
    products = cur.fetchall()
    product_lookup = {row[0]: row[1] for row in products}

    # Fetch customer lookup
    cur.execute("SELECT international_id, first_name, last_name FROM verify")
    customers = cur.fetchall()
    customer_lookup = {row[0]: f"{row[1]} {row[2]}" for row in customers}

    conn.close()
    return product_lookup, customer_lookup


# ---------- FUNCTION: CREATE RECEIPT ----------
def print_receipt(product_name, quantity, unit_price, total_price, sale_date,
                  cash_received, remaining_amount, customer_name, sales_id):

    STORE_NAME = "AZEEM STORE"
    GREETING = "Welcome to our store"
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    receipt = f"""
    ===============================================================
                        {STORE_NAME}
    ===============================================================
    {GREETING}
    Time: {current_time}
    ---------------------------------------------------------------
    BILL SECTION
    ---------------------------------------------------------------
    Product              Qty      Unit Price        Total
    ---------------------------------------------------------------
    {product_name:<20} {quantity:<5}   ${float(unit_price):<12.2f} ${float(total_price):.2f}
    ---------------------------------------------------------------
    SALE DETAILS
    Sale ID: {sales_id}
    Date: {sale_date}
    Cash Received: ${cash_received}
    Remaining Amount: ${remaining_amount}
    ---------------------------------------------------------------
    CUSTOMER SECTION
    Name: {customer_name}
    ---------------------------------------------------------------
    GRAND TOTAL: ${float(total_price):.2f}
    ---------------------------------------------------------------
    Thank you for shopping with us!
    Visit again soon 😊
    ===============================================================
    """

    folder = "receipts"
    os.makedirs(folder, exist_ok=True)

    # ✅ Set file path
    filename = os.path.join(folder, f"receipt_{sales_id}.pdf")

    # ✅ Create PDF canvas
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # ✅ Write receipt text line by line
    y = height - 50  # starting position
    for line in receipt.split("\n"):
        c.drawString(50, y, line)
        y -= 15  # move down for next line

        # Avoid writing beyond bottom of page
        if y < 50:
            c.showPage()
            y = height - 50

    # ✅ Save the PDF
    c.save()

    print(f"✅ Receipt saved as: {filename}")
    return filename


# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/print", methods=["POST"])
def print_sale():
    product_lookup, customer_lookup = get_lookups()

    # Fetch values from form
    quantity = request.form.get("quantity")
    unit_price = request.form.get("unit_price")
    sales_id = request.form.get("sales_id")
    total_price = request.form.get("total_price")
    sale_date = request.form.get("sale_date") or date.today()
    cash_received = request.form.get("cash_received")
    remaining_amount = request.form.get("remaining_amount")

    # Convert IDs (safe conversion)
    product_id = request.form.get("product_id")
    customer_id = request.form.get("customer_id")

    if not product_id or not customer_id:
        flash("❌ Missing product or customer ID in form data.", "error")
        return redirect(url_for("index"))

    try:
        product_id = int(product_id)
        customer_id = int(customer_id)
    except ValueError:
        flash("❌ Invalid ID format.", "error")
        return redirect(url_for("index"))

    # Get names from lookups
    product_name = product_lookup.get(product_id, "Unknown Product")
    customer_name = customer_lookup.get(customer_id, "Unknown Customer")

    # Generate receipt file
    filename = print_receipt(
        product_name, quantity, unit_price, total_price, sale_date,
        cash_received, remaining_amount, customer_name, sales_id
    )

    flash(f"🖨️ Receipt saved as {filename}", "success")
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True)

