from flask import Flask, render_template, request, redirect
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sales.db")
app = Flask(__name__)


UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    search = request.args.get("search", "").strip()
    filter_condition = request.args.get("condition", "")
    filter_category = request.args.get("category", "")
    instagram_status = request.args.get("instagram_status", "")
    sort_by = request.args.get("sort", "newest")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT *
        FROM items
        WHERE status = 'available'
    """

    params = []

    if search:
        query += """
            AND (
                name LIKE ?
                OR description LIKE ?
                OR item_condition LIKE ?
            )
        """

        like_term = f"%{search}%"
        params.extend([like_term, like_term, like_term])

    if filter_condition:
        query += " AND item_condition = ?"
        params.append(filter_condition)

    if filter_category:
        query += " AND category = ?"
        params.append(filter_category)

    if instagram_status == "posted":
        query += " AND instagram_posted = 1"

    elif instagram_status == "not_posted":
        query += " AND instagram_posted = 0"

    sort_options = {
        "newest": "date_added DESC, id DESC",
        "price_low": "price ASC",
        "price_high": "price DESC"
    }

    query += " ORDER BY " + sort_options.get(sort_by, "date_added DESC, id DESC")

    cursor.execute(query, params)
    items = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*)
        FROM items
        WHERE status = 'available'
    """)
    available_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM items
        WHERE status = 'sold'
    """)
    sold_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT SUM(price)
        FROM items
        WHERE status = 'sold'
    """)
    total_sales = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT DISTINCT item_condition
        FROM items
        WHERE item_condition IS NOT NULL
        ORDER BY item_condition
    """)
    conditions = [row[0] for row in cursor.fetchall()]

    cursor.execute("""
        SELECT DISTINCT category
        FROM items
        WHERE category IS NOT NULL
        AND status = 'available'
        ORDER BY category
    """)
    categories = [row[0] for row in cursor.fetchall()]

    conn.close()

    return render_template(
        "index.html",
        items=items,
        available_count=available_count,
        sold_count=sold_count,
        total_sales=total_sales,
        conditions=conditions,
        categories=categories,
        search=search,
        filter_condition=filter_condition,
        filter_category=filter_category,
        instagram_status=instagram_status,
        sort_by=sort_by
    )


# ADD ITEM

@app.route("/add", methods=["POST"])
def add_item():
    name = request.form["name"]
    price = request.form["price"]
    quantity = request.form["quantity"]
    condition = request.form["condition"]
    description = request.form["description"]

    category = request.form.get("category", "").strip()
    custom_category = request.form.get("custom_category", "").strip()

    if category == "OTHER":
        category = custom_category

    image = request.files.get("image")

    filename = ""

    image_position = request.form.get(
        "image_position",
        "50% 50%"
    )

    if image and image.filename:
        filename = image.filename
        image.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )
    size = request.form.get("size", "")
    custom_size = request.form.get("custom_size", "")

    if size == "OTHER":
        size = custom_size

    date_added = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO items
    (
        name,
        price,
        quantity,
        size,
        category,
        item_condition,
        description,
        image_path,
        image_position,
        date_added
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    name,
    price,
    quantity,
    size,
    category,
    condition,
    description,
    filename,
    image_position,
    date_added
))

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/toggle-instagram/<int:item_id>")
def toggle_instagram(item_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE items
        SET instagram_posted =
            CASE
                WHEN instagram_posted = 1 THEN 0
                ELSE 1
            END
        WHERE id=?
    """, (item_id,))

    conn.commit()
    conn.close()

    return redirect("/")

# SOLD ITEMS PAGE


@app.route("/sold-items")
def sold_items():
    search = request.args.get("search", "").strip()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT *
        FROM items
        WHERE status = 'sold'
    """

    params = []

    if search:
        query += """
            AND (
                name LIKE ?
                OR description LIKE ?
                OR item_condition LIKE ?
                OR category LIKE ?
            )
        """

        like_term = f"%{search}%"
        params.extend([
            like_term,
            like_term,
            like_term,
            like_term
        ])

    query += " ORDER BY date_sold DESC, id DESC"

    cursor.execute(query, params)
    items = cursor.fetchall()

    conn.close()

    return render_template(
        "sold_items.html",
        items=items,
        search=search
    )


# DELETE ITEM


@app.route("/delete/<int:item_id>")
def delete_item(item_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM items
        WHERE id=?
    """, (item_id,))

    conn.commit()
    conn.close()

    return redirect("/")

# Mark Sold
@app.route("/mark-sold/<int:item_id>", methods=["POST"])
def mark_sold(item_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    sold_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE items
        SET status = 'sold',
            date_sold = ?
        WHERE id = ?
    """, (sold_date, item_id))

    conn.commit()
    conn.close()

    return redirect("/")


# EDIT ITEM PAGE
@app.route("/edit/<int:item_id>")
def edit_item(item_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM items
        WHERE id=?
    """, (item_id,))

    item = cursor.fetchone()

    # Get all existing categories
    cursor.execute("""
        SELECT DISTINCT category
        FROM items
        WHERE category IS NOT NULL
        AND category != ''
        ORDER BY category
    """)

    categories = [row["category"] for row in cursor.fetchall()]

    conn.close()

    return render_template(
        "edit_item.html",
        item=item,
        categories=categories
    )

#SAVE EDIT
@app.route("/update/<int:item_id>", methods=["POST"])
def update_item(item_id):
    name = request.form["name"]
    price = float(request.form["price"])
    quantity = int(request.form["quantity"])
    condition = request.form["condition"]
    size = request.form.get("size", "")
    custom_size = request.form.get("custom_size", "")
    description = request.form["description"]
    category = request.form.get("category", "").strip()

    image_position = request.form.get(
        "image_position",
        "50% 50%"
    )

    if size == "OTHER":
        size = custom_size

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT image_path FROM items WHERE id=?",
        (item_id,)
    )

    current_item = cursor.fetchone()

    current_image = current_item[0] if current_item else ""

    image = request.files.get("image")

    filename = current_image

    if image and image.filename:
        filename = image.filename

        image.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

    status = "available"
    date_sold = None

    if quantity <= 0:
        status = "sold"
        date_sold = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        UPDATE items
        SET
            name=?,
            price=?,
            quantity=?,
            size=?,
            category=?,
            item_condition=?,
            description=?,
            image_path=?,
            image_position=?,
            status=?,
            date_sold=?
        WHERE id=?
    """, (
        name,
        price,
        quantity,
        size,
        category,
        condition,
        description,
        filename,
        image_position,
        status,
        date_sold,
        item_id
    ))

    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)