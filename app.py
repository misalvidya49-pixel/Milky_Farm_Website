from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

# Session secret key
app.secret_key = "milky-farm-secret-key"


# =========================
# DATABASE CREATION
# =========================
def create_database():

    conn = sqlite3.connect("milky_farm.db")
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # ORDERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            product TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            address TEXT NOT NULL
        )
    """)

    # Add status column if it doesn't exist
    try:
        cursor.execute("""
            ALTER TABLE orders
            ADD COLUMN status TEXT NOT NULL DEFAULT 'Pending'
        """)
    except sqlite3.OperationalError:
        pass

    # Add user_id column if it doesn't exist
    try:
        cursor.execute("""
            ALTER TABLE orders
            ADD COLUMN user_id INTEGER
        """)
    except sqlite3.OperationalError:
        pass

    # CONTACTS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            mobile TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================
# HOME PAGE
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# PRODUCTS PAGE
# =========================
@app.route("/products")
def products():
    return render_template("products.html")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("milky_farm.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM users
            WHERE email = ? AND password = ?
        """, (email, password))

        user = cursor.fetchone()

        conn.close()

        if user:

            session["user_id"] = user[0]
            session["user_name"] = user[1]
            session["user_email"] = user[2]

            return redirect("/dashboard")

        else:

            return """
            <div style="
                text-align:center;
                margin-top:100px;
                font-family:Arial;
            ">

                <h2>Invalid Email or Password ❌</h2>

                <br>

                <a href="/login">
                    Try Again
                </a>

            </div>
            """

    return render_template("login.html")


# =========================
# REGISTER
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("milky_farm.db")
        cursor = conn.cursor()

        try:

            cursor.execute("""
                INSERT INTO users
                (name, email, password)
                VALUES (?, ?, ?)
            """, (name, email, password))

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:

            conn.close()

            return """
            <div style="
                text-align:center;
                margin-top:100px;
                font-family:Arial;
            ">

                <h2>Email already registered! ❌</h2>

                <br>

                <a href="/register">
                    Try Again
                </a>

            </div>
            """

    return render_template("register.html")


# =========================
# USER DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("milky_farm.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            product,
            price,
            quantity,
            address,
            status
        FROM orders
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],))

    orders = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        name=session["user_name"],
        email=session["user_email"],
        orders=orders
    )


# =========================
# USER LOGOUT
# =========================
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================
# ORDER PAGE
# =========================
@app.route("/order")
def order():

    if "user_id" not in session:
        return redirect("/login")

    product = request.args.get("product")
    price = request.args.get("price")

    return render_template(
        "order.html",
        product=product,
        price=price
    )


# =========================
# PLACE ORDER
# =========================
@app.route("/place-order", methods=["POST"])
def place_order():

    if "user_id" not in session:
        return redirect("/login")

    customer_name = request.form["customer_name"]
    mobile = request.form["mobile"]
    product = request.form["product"]
    price = float(request.form["price"])
    quantity = int(request.form["quantity"])
    address = request.form["address"]

    user_id = session["user_id"]

    conn = sqlite3.connect("milky_farm.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO orders
        (
            customer_name,
            mobile,
            product,
            price,
            quantity,
            address,
            status,
            user_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        customer_name,
        mobile,
        product,
        price,
        quantity,
        address,
        "Pending",
        user_id
    ))

    conn.commit()
    conn.close()

    total = price * quantity

    return f"""
    <div style="
        text-align:center;
        margin-top:100px;
        font-family:Arial;
    ">

        <h1 style="color:#188038;">
            Order Placed Successfully! 🎉
        </h1>

        <h2>
            Thank You, {customer_name} ❤️
        </h2>

        <p>
            <b>Product:</b> {product}
        </p>

        <p>
            <b>Quantity:</b> {quantity}
        </p>

        <p>
            <b>Price:</b> ₹{price}
        </p>

        <p>
            <b>Total Amount:</b> ₹{total}
        </p>

        <p style="color:#188038;">
            <b>Order Status:</b> Pending 🟡
        </p>

        <br>

        <a href="/dashboard"
           style="
                background:#188038;
                color:white;
                padding:12px 25px;
                border-radius:25px;
                text-decoration:none;
           ">
            My Orders
        </a>

        &nbsp;&nbsp;

        <a href="/products"
           style="
                background:#555;
                color:white;
                padding:12px 25px;
                border-radius:25px;
                text-decoration:none;
           ">
            Products
        </a>

        &nbsp;&nbsp;

        <a href="/"
           style="
                background:#777;
                color:white;
                padding:12px 25px;
                border-radius:25px;
                text-decoration:none;
           ">
            Home
        </a>

    </div>
    """


# =========================
# CONTACT
# =========================
@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        message = request.form["message"]

        conn = sqlite3.connect("milky_farm.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO contacts
            (name, email, mobile, message)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            mobile,
            message
        ))

        conn.commit()
        conn.close()

        return """
        <div style="
            text-align:center;
            margin-top:100px;
            font-family:Arial;
        ">

            <h1 style="color:#188038;">
                Message Sent Successfully! ✅
            </h1>

            <p>
                Thank you for contacting MILKY FARM.
            </p>

            <br>

            <a href="/"
               style="
                    background:#188038;
                    color:white;
                    padding:12px 25px;
                    border-radius:25px;
                    text-decoration:none;
               ">
                Back to Home
            </a>

        </div>
        """

    return render_template("contact.html")


# =========================
# ADMIN LOGIN
# =========================
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        if (
            email == "admin@milkyfarm.com"
            and password == "admin123"
        ):

            session["admin_logged_in"] = True

            return redirect("/admin")

        else:

            return """
            <div style="
                text-align:center;
                margin-top:100px;
                font-family:Arial;
            ">

                <h2>
                    Invalid Admin Email or Password ❌
                </h2>

                <br>

                <a href="/admin-login">
                    Try Again
                </a>

            </div>
            """

    return render_template("admin_login.html")


# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin")
def admin():

    if "admin_logged_in" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect("milky_farm.db")
    cursor = conn.cursor()

    # ORDERS
    cursor.execute("""
        SELECT
            id,
            customer_name,
            mobile,
            product,
            price,
            quantity,
            address,
            status
        FROM orders
        ORDER BY id DESC
    """)

    orders_data = cursor.fetchall()

    orders = []

    for order in orders_data:

        (
            order_id,
            customer_name,
            mobile,
            product,
            price,
            quantity,
            address,
            status
        ) = order

        total = price * quantity

        orders.append((
            order_id,
            customer_name,
            mobile,
            product,
            price,
            quantity,
            total,
            address,
            status
        ))

    # CONTACT MESSAGES
    cursor.execute("""
        SELECT
            id,
            name,
            email,
            mobile,
            message
        FROM contacts
        ORDER BY id DESC
    """)

    contacts = cursor.fetchall()

    # CUSTOMERS
    cursor.execute("""
        SELECT
            users.id,
            users.name,
            users.email,
            COUNT(orders.id) AS total_orders
        FROM users
        LEFT JOIN orders
        ON users.id = orders.user_id
        GROUP BY users.id
        ORDER BY users.id DESC
    """)

    customers = cursor.fetchall()

    # TOTAL USERS
    cursor.execute("""
        SELECT COUNT(*)
        FROM users
    """)

    total_users = cursor.fetchone()[0]

    # TOTAL ORDERS
    cursor.execute("""
        SELECT COUNT(*)
        FROM orders
    """)

    total_orders = cursor.fetchone()[0]

    # TOTAL CONTACTS
    cursor.execute("""
        SELECT COUNT(*)
        FROM contacts
    """)

    total_contacts = cursor.fetchone()[0]

    # TOTAL SALES
    total_sales = sum(
        order[6]
        for order in orders
    )

    conn.close()

    return render_template(
        "admin.html",
        orders=orders,
        contacts=contacts,
        customers=customers,
        total_users=total_users,
        total_orders=total_orders,
        total_contacts=total_contacts,
        total_sales=total_sales
    )


# =========================
# UPDATE ORDER STATUS
# =========================
@app.route("/update-order-status", methods=["POST"])
def update_order_status():

    if "admin_logged_in" not in session:
        return redirect("/admin-login")

    order_id = request.form["order_id"]
    status = request.form["status"]

    conn = sqlite3.connect("milky_farm.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders
        SET status = ?
        WHERE id = ?
    """, (
        status,
        order_id
    ))

    conn.commit()
    conn.close()

    return redirect("/admin")


# =========================
# DELETE ORDER
# =========================
@app.route("/delete-order/<int:order_id>", methods=["POST"])
def delete_order(order_id):

    if "admin_logged_in" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect("milky_farm.db")
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM orders
        WHERE id = ?
    """, (order_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


# =========================
# DELETE CONTACT
# =========================
@app.route("/delete-contact/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):

    if "admin_logged_in" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect("milky_farm.db")
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM contacts
        WHERE id = ?
    """, (contact_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


# =========================
# DELETE USER
# =========================
@app.route("/delete-user/<int:user_id>", methods=["POST"])
def delete_user(user_id):

    if "admin_logged_in" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect("milky_farm.db")
    cursor = conn.cursor()

    # Delete user's orders first
    cursor.execute("""
        DELETE FROM orders
        WHERE user_id = ?
    """, (user_id,))

    # Delete user
    cursor.execute("""
        DELETE FROM users
        WHERE id = ?
    """, (user_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


# =========================
# ADMIN LOGOUT
# =========================
@app.route("/admin-logout")
def admin_logout():

    session.pop("admin_logged_in", None)

    return redirect("/admin-login")


# =========================
# CREATE DATABASE
# =========================
create_database()


# =========================
# RUN FLASK APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)