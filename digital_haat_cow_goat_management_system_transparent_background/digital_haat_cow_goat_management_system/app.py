from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config["SECRET_KEY"] = "digital-haat-secret-key-change-this"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///digital_haat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_number = db.Column(db.String(50), nullable=False, unique=True)
    animal_type = db.Column(db.String(20), nullable=False)  # Cow or Goat
    name = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    age_months = db.Column(db.Integer, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Available")
    location = db.Column(db.String(150), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    health_records = db.relationship("HealthRecord", backref="animal", lazy=True, cascade="all, delete-orphan")
    feeding_records = db.relationship("FeedingRecord", backref="animal", lazy=True, cascade="all, delete-orphan")
    sale_records = db.relationship("SaleRecord", backref="animal", lazy=True, cascade="all, delete-orphan")


class HealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey("animal.id"), nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    record_type = db.Column(db.String(50), nullable=False) 
    doctor_name = db.Column(db.String(100), nullable=False)
    medicine = db.Column(db.String(150), nullable=True)
    cost = db.Column(db.Float, nullable=False, default=0)
    notes = db.Column(db.Text, nullable=True)


class FeedingRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey("animal.id"), nullable=False)
    feeding_date = db.Column(db.Date, nullable=False)
    feed_name = db.Column(db.String(100), nullable=False)
    quantity_kg = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=False, default=0)
    notes = db.Column(db.Text, nullable=True)


class ExpenseRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)


class SaleRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey("animal.id"), nullable=False)
    buyer_name = db.Column(db.String(100), nullable=False)
    buyer_phone = db.Column(db.String(50), nullable=False)
    sale_date = db.Column(db.Date, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)

def convert_text_to_date(date_text):
    """Convert form date text into Python date object."""
    return datetime.strptime(date_text, "%Y-%m-%d").date()


def get_total_purchase_value(animals):
    total = 0
    for animal in animals:
        total = total + animal.purchase_price
    return total


def get_total_health_cost():
    records = HealthRecord.query.all()
    total = 0
    for record in records:
        total = total + record.cost
    return total


def get_total_feeding_cost():
    records = FeedingRecord.query.all()
    total = 0
    for record in records:
        total = total + record.cost
    return total


def get_total_expense_cost():
    records = ExpenseRecord.query.all()
    total = 0
    for record in records:
        total = total + record.amount
    return total


def get_total_sales_value():
    records = SaleRecord.query.all()
    total = 0
    for record in records:
        total = total + record.sale_price
    return total

@app.route("/")
def index():
    total_animals = Animal.query.count()
    available_animals = Animal.query.filter_by(status="Available").count()
    sold_animals = Animal.query.filter_by(status="Sold").count()
    latest_animals = Animal.query.order_by(Animal.created_at.desc()).limit(3).all()

    return render_template(
        "index.html",
        total_animals=total_animals,
        available_animals=available_animals,
        sold_animals=sold_animals,
        latest_animals=latest_animals
    )


@app.route("/dashboard")
def dashboard():
    animals = Animal.query.all()
    total_animals = Animal.query.count()
    total_cows = Animal.query.filter_by(animal_type="Cow").count()
    total_goats = Animal.query.filter_by(animal_type="Goat").count()
    available_animals = Animal.query.filter_by(status="Available").count()
    sold_animals = Animal.query.filter_by(status="Sold").count()

    purchase_value = get_total_purchase_value(animals)
    health_cost = get_total_health_cost()
    feeding_cost = get_total_feeding_cost()
    expense_cost = get_total_expense_cost()
    sales_value = get_total_sales_value()
    estimated_profit = sales_value - purchase_value - health_cost - feeding_cost - expense_cost

    recent_animals = Animal.query.order_by(Animal.created_at.desc()).limit(5).all()
    recent_health = HealthRecord.query.order_by(HealthRecord.record_date.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        total_animals=total_animals,
        total_cows=total_cows,
        total_goats=total_goats,
        available_animals=available_animals,
        sold_animals=sold_animals,
        purchase_value=purchase_value,
        health_cost=health_cost,
        feeding_cost=feeding_cost,
        expense_cost=expense_cost,
        sales_value=sales_value,
        estimated_profit=estimated_profit,
        recent_animals=recent_animals,
        recent_health=recent_health
    )


@app.route("/animals")
def animals():
    search_text = request.args.get("search", "")
    animal_type = request.args.get("animal_type", "")
    status = request.args.get("status", "")

    animal_query = Animal.query

    if search_text != "":
        animal_query = animal_query.filter(
            (Animal.name.contains(search_text)) |
            (Animal.tag_number.contains(search_text)) |
            (Animal.breed.contains(search_text))
        )

    if animal_type != "":
        animal_query = animal_query.filter_by(animal_type=animal_type)

    if status != "":
        animal_query = animal_query.filter_by(status=status)

    all_animals = animal_query.order_by(Animal.created_at.desc()).all()

    return render_template(
        "animals.html",
        animals=all_animals,
        search_text=search_text,
        selected_type=animal_type,
        selected_status=status
    )


@app.route("/animals/add", methods=["GET", "POST"])
def add_animal():
    if request.method == "POST":
        tag_number = request.form.get("tag_number")
        existing_animal = Animal.query.filter_by(tag_number=tag_number).first()

        if existing_animal is not None:
            flash("This tag number already exists. Please use a unique tag number.", "error")
            return redirect(url_for("add_animal"))

        new_animal = Animal(
            tag_number=tag_number,
            animal_type=request.form.get("animal_type"),
            name=request.form.get("name"),
            breed=request.form.get("breed"),
            gender=request.form.get("gender"),
            age_months=int(request.form.get("age_months")),
            weight_kg=float(request.form.get("weight_kg")),
            purchase_price=float(request.form.get("purchase_price")),
            purchase_date=convert_text_to_date(request.form.get("purchase_date")),
            status=request.form.get("status"),
            location=request.form.get("location"),
            notes=request.form.get("notes")
        )

        db.session.add(new_animal)
        db.session.commit()
        flash("Animal profile added successfully.", "success")
        return redirect(url_for("animals"))

    today_date = date.today().strftime("%Y-%m-%d")
    return render_template("add_animal.html", today_date=today_date)


@app.route("/animals/<int:animal_id>")
def animal_detail(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    health_records = HealthRecord.query.filter_by(animal_id=animal_id).order_by(HealthRecord.record_date.desc()).all()
    feeding_records = FeedingRecord.query.filter_by(animal_id=animal_id).order_by(FeedingRecord.feeding_date.desc()).all()
    sale_records = SaleRecord.query.filter_by(animal_id=animal_id).order_by(SaleRecord.sale_date.desc()).all()

    total_health_cost = 0
    for record in health_records:
        total_health_cost = total_health_cost + record.cost

    total_feeding_cost = 0
    for record in feeding_records:
        total_feeding_cost = total_feeding_cost + record.cost

    return render_template(
        "animal_detail.html",
        animal=animal,
        health_records=health_records,
        feeding_records=feeding_records,
        sale_records=sale_records,
        total_health_cost=total_health_cost,
        total_feeding_cost=total_feeding_cost
    )


@app.route("/animals/<int:animal_id>/edit", methods=["GET", "POST"])
def edit_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)

    if request.method == "POST":
        animal.tag_number = request.form.get("tag_number")
        animal.animal_type = request.form.get("animal_type")
        animal.name = request.form.get("name")
        animal.breed = request.form.get("breed")
        animal.gender = request.form.get("gender")
        animal.age_months = int(request.form.get("age_months"))
        animal.weight_kg = float(request.form.get("weight_kg"))
        animal.purchase_price = float(request.form.get("purchase_price"))
        animal.purchase_date = convert_text_to_date(request.form.get("purchase_date"))
        animal.status = request.form.get("status")
        animal.location = request.form.get("location")
        animal.notes = request.form.get("notes")

        db.session.commit()
        flash("Animal profile updated successfully.", "success")
        return redirect(url_for("animal_detail", animal_id=animal.id))

    return render_template("edit_animal.html", animal=animal)


@app.route("/animals/<int:animal_id>/delete", methods=["POST"])
def delete_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    db.session.delete(animal)
    db.session.commit()
    flash("Animal profile deleted successfully.", "success")
    return redirect(url_for("animals"))


@app.route("/health", methods=["GET", "POST"])
def health_records():
    if request.method == "POST":
        new_record = HealthRecord(
            animal_id=int(request.form.get("animal_id")),
            record_date=convert_text_to_date(request.form.get("record_date")),
            record_type=request.form.get("record_type"),
            doctor_name=request.form.get("doctor_name"),
            medicine=request.form.get("medicine"),
            cost=float(request.form.get("cost")),
            notes=request.form.get("notes")
        )

        db.session.add(new_record)
        db.session.commit()
        flash("Health record added successfully.", "success")
        return redirect(url_for("health_records"))

    all_animals = Animal.query.order_by(Animal.name.asc()).all()
    records = HealthRecord.query.order_by(HealthRecord.record_date.desc()).all()
    today_date = date.today().strftime("%Y-%m-%d")

    return render_template(
        "health.html",
        animals=all_animals,
        records=records,
        today_date=today_date
    )


@app.route("/feeding", methods=["GET", "POST"])
def feeding_records():
    if request.method == "POST":
        new_record = FeedingRecord(
            animal_id=int(request.form.get("animal_id")),
            feeding_date=convert_text_to_date(request.form.get("feeding_date")),
            feed_name=request.form.get("feed_name"),
            quantity_kg=float(request.form.get("quantity_kg")),
            cost=float(request.form.get("cost")),
            notes=request.form.get("notes")
        )

        db.session.add(new_record)
        db.session.commit()
        flash("Feeding record added successfully.", "success")
        return redirect(url_for("feeding_records"))

    all_animals = Animal.query.order_by(Animal.name.asc()).all()
    records = FeedingRecord.query.order_by(FeedingRecord.feeding_date.desc()).all()
    today_date = date.today().strftime("%Y-%m-%d")

    return render_template(
        "feeding.html",
        animals=all_animals,
        records=records,
        today_date=today_date
    )


@app.route("/expenses", methods=["GET", "POST"])
def expenses():
    if request.method == "POST":
        new_expense = ExpenseRecord(
            expense_date=convert_text_to_date(request.form.get("expense_date")),
            category=request.form.get("category"),
            amount=float(request.form.get("amount")),
            description=request.form.get("description")
        )

        db.session.add(new_expense)
        db.session.commit()
        flash("Expense record added successfully.", "success")
        return redirect(url_for("expenses"))

    records = ExpenseRecord.query.order_by(ExpenseRecord.expense_date.desc()).all()
    today_date = date.today().strftime("%Y-%m-%d")
    total_expenses = get_total_expense_cost()

    return render_template(
        "expenses.html",
        records=records,
        today_date=today_date,
        total_expenses=total_expenses
    )


@app.route("/sales", methods=["GET", "POST"])
def sales():
    if request.method == "POST":
        animal_id = int(request.form.get("animal_id"))
        animal = Animal.query.get_or_404(animal_id)

        new_sale = SaleRecord(
            animal_id=animal_id,
            buyer_name=request.form.get("buyer_name"),
            buyer_phone=request.form.get("buyer_phone"),
            sale_date=convert_text_to_date(request.form.get("sale_date")),
            sale_price=float(request.form.get("sale_price")),
            payment_status=request.form.get("payment_status"),
            notes=request.form.get("notes")
        )

        animal.status = "Sold"
        db.session.add(new_sale)
        db.session.commit()
        flash("Sale record added and animal marked as sold.", "success")
        return redirect(url_for("sales"))

    available_animals = Animal.query.filter_by(status="Available").order_by(Animal.name.asc()).all()
    records = SaleRecord.query.order_by(SaleRecord.sale_date.desc()).all()
    today_date = date.today().strftime("%Y-%m-%d")
    total_sales = get_total_sales_value()

    return render_template(
        "sales.html",
        animals=available_animals,
        records=records,
        today_date=today_date,
        total_sales=total_sales
    )


@app.route("/reports")
def reports():
    animals = Animal.query.all()
    purchase_value = get_total_purchase_value(animals)
    health_cost = get_total_health_cost()
    feeding_cost = get_total_feeding_cost()
    expense_cost = get_total_expense_cost()
    sales_value = get_total_sales_value()
    total_cost = purchase_value + health_cost + feeding_cost + expense_cost
    net_result = sales_value - total_cost

    total_cows = Animal.query.filter_by(animal_type="Cow").count()
    total_goats = Animal.query.filter_by(animal_type="Goat").count()
    available_animals = Animal.query.filter_by(status="Available").count()
    sold_animals = Animal.query.filter_by(status="Sold").count()

    return render_template(
        "reports.html",
        purchase_value=purchase_value,
        health_cost=health_cost,
        feeding_cost=feeding_cost,
        expense_cost=expense_cost,
        sales_value=sales_value,
        total_cost=total_cost,
        net_result=net_result,
        total_cows=total_cows,
        total_goats=total_goats,
        available_animals=available_animals,
        sold_animals=sold_animals
    )
def create_sample_data():
    animal_count = Animal.query.count()

    if animal_count == 0:
        cow_one = Animal(
            tag_number="COW-1001",
            animal_type="Cow",
            name="Brahman King",
            breed="American Brahman",
            gender="Male",
            age_months=36,
            weight_kg=620,
            purchase_price=250000,
            purchase_date=date(2025, 8, 10),
            status="Available",
            location="Main Cattle Shed",
            notes="Healthy large Brahman bull, suitable for breeding and premium haat sales."
        )

        cow_two = Animal(
            tag_number="COW-1002",
            animal_type="Cow",
            name="Red Sultan",
            breed="Red Brahman",
            gender="Male",
            age_months=30,
            weight_kg=540,
            purchase_price=210000,
            purchase_date=date(2025, 9, 2),
            status="Available",
            location="Premium Shed",
            notes="Beautiful red color cattle with strong body structure."
        )

        goat_one = Animal(
            tag_number="GOAT-2001",
            animal_type="Goat",
            name="Black Diamond",
            breed="Black Bengal",
            gender="Female",
            age_months=18,
            weight_kg=28,
            purchase_price=18000,
            purchase_date=date(2025, 10, 5),
            status="Available",
            location="Goat Unit A",
            notes="Healthy local goat, good for breeding and small livestock trade."
        )

        db.session.add(cow_one)
        db.session.add(cow_two)
        db.session.add(goat_one)
        db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_sample_data()

    app.run(debug=True)
