from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = "Secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///income.sqlite'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Create database for list of income
class IncomeData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(100))
    amount = db.Column(db.Integer)

    def __init__(self, name, type, amount):
        self.name = name
        self.type = type
        self.amount = amount


# Create database for list of expenditure
class ExpenditureData(db.Model):
    exp_id = db.Column(db.Integer, primary_key=True)
    exp_name = db.Column(db.String(100))
    exp_type = db.Column(db.String(100))
    exp_amount = db.Column(db.Integer)

    def __init__(self, exp_name, exp_type, exp_amount):
        self.exp_name = exp_name
        self.exp_type = exp_type
        self.exp_amount = exp_amount


# Create database for savings
class SavingsData(db.Model):
    savings_id = db.Column(db.Integer, primary_key=True)
    savings_amount = db.Column(db.Integer)

    def __init__(self, savings_amount):
        self.savings_amount = savings_amount


# App route to home
@app.route("/")
def home():
    home_income = IncomeData.query.all()
    home_expenditure = ExpenditureData.query.all()
    income_total = sum(inc.amount for inc in home_income)
    expenditure_total = sum(exp.exp_amount for exp in home_expenditure)

    # Saving data of goal amount
    goal = SavingsData.query.order_by(SavingsData.savings_id.desc()).first()
    if goal is not None:
        savings_amount = goal.savings_amount
    else:
        return redirect(url_for("configure_savings"))
    exp_data = ExpenditureData.query.all()
    income_data = IncomeData.query.all()

    # Calculate total income and total expenditures
    income_total = sum(inc.amount for inc in income_data)
    exp_total = sum(exp.exp_amount for exp in exp_data)

    # Calculate difference between total income and total expenditures
    difference = income_total - exp_total

    # Calculate the progress based on exp_total, income_total, and savings goal
    if income_total > exp_total:
        home_progress = (income_total - exp_total) / goal.savings_amount * 100
    else:
        home_progress = 0

    return render_template("index.html",home_progress=home_progress, expenditure_total=expenditure_total, income_total=income_total, difference = difference)


# app route to income page
@app.route("/income")
def income():
    all_data = IncomeData.query.all()
    income_total = sum(inc.amount for inc in all_data)
    return render_template("incomePage.html", incomes=all_data, income_total=income_total)


# app route to insert new income data
@app.route("/insert", methods=["POST"])
def insert():

    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        amount = request.form['amount']

        income_data = IncomeData(name, type, amount)
        db.session.add(income_data)
        db.session.commit()

        flash("Income Inserted Successfully!")
        return redirect(url_for("income"))


# app route to edit income data
@app.route("/update", methods=["GET","POST"])
def update():

    if request.method == "POST":
        income_data = IncomeData.query.get(request.form.get("id"))
        income_data.name = request.form['name']
        income_data.type = request.form['type']
        income_data.amount = request.form['amount']

        db.session.commit()
        flash("Income Updated Successfully!")

        return redirect(url_for("income"))


# app route to delete income data
@app.route("/delete/<id>/", methods=["GET","POST"])
def delete(id):
    income_data = IncomeData.query.get(id)
    db.session.delete(income_data)
    db.session.commit()

    flash("Income Deleted Successfully")

    return redirect(url_for("income"))


# app route to expenditure page
@app.route("/expenditure")
def expense():
    exp_data = ExpenditureData.query.all()
    exp_total = sum(exp.exp_amount for exp in exp_data)
    return render_template("expenseList.html", expenditures=exp_data, exp_total=exp_total)


# app route to insert new expenditure data
@app.route("/exp_insert", methods=["POST"])
def exp_insert():

    if request.method == 'POST':
        exp_name = request.form['exp_name']
        exp_type = request.form['exp_type']
        exp_amount = request.form['exp_amount']

        expenditure_data = ExpenditureData(exp_name, exp_type, exp_amount)
        db.session.add(expenditure_data)
        db.session.commit()

        flash("Expense Inserted Successfully!")
        return redirect(url_for("expense"))


# app route to edit expenditure data
@app.route("/exp_update", methods=["GET","POST"])
def exp_update():

    if request.method == "POST":
        expenditure_data = ExpenditureData.query.get(request.form.get("exp_id"))
        expenditure_data.exp_name = request.form['exp_name']
        expenditure_data.exp_type = request.form['exp_type']
        expenditure_data.exp_amount = request.form['exp_amount']

        db.session.commit()
        flash("Expense Updated Successfully!")

        return redirect(url_for("expense"))


# app route to delete expenditure data
@app.route("/exp_delete/<exp_id>/", methods=["GET","POST"])
def exp_delete(exp_id):
    expenditure_data = ExpenditureData.query.get(exp_id)
    db.session.delete(expenditure_data)
    db.session.commit()

    flash("Expense Deleted Successfully")

    return redirect(url_for("expense"))


# app route to savings goal page
@app.route("/savings", methods=["GET","POST"])
def savings():
    goal = SavingsData.query.order_by(SavingsData.savings_id.desc()).first()
    if goal is not None:
        savings_amount = goal.savings_amount
    else:
        return redirect(url_for("configure_savings"))
    exp_data = ExpenditureData.query.all()
    income_data = IncomeData.query.all()

    # Calculate total income and total expenditures
    income_total = sum(inc.amount for inc in income_data)
    exp_total = sum(exp.exp_amount for exp in exp_data)

    # Calculate the progress based on exp_total, income_total, and savings goal
    if income_total > exp_total:
        progress = (income_total - exp_total) / goal.savings_amount * 100
    else:
        progress = 0

    # Request user to insert new savings goal amount
    if request.method == "POST":
        new_savings_amount = int(request.form["savings_amount"])
        if goal:
            goal.savings_amount = new_savings_amount
        else:
            goal = SavingsData(new_savings_amount)
        db.session.add(goal)
        db.session.commit()

        flash("Savings Goal Updated Successfully!")
        return redirect(url_for("savings"))
    return render_template("savingsGoal.html", goal=goal, exp_total=exp_total, income_total=income_total, progress=progress)


# app route to edit savings goal
@app.route("/configure_savings", methods=["GET", "POST"])
def configure_savings():
    if request.method == "POST":
        new_savings_amount = float(request.form["savings_amount"])

        if new_savings_amount <= 0:
            flash("Savings Goal cannot be zero. Please enter a valid number.")
        else:
            goal = SavingsData.query.order_by(SavingsData.savings_id.desc()).first()

            if goal:
                goal.savings_amount = new_savings_amount
            else:
                goal = SavingsData(savings_amount=new_savings_amount)
                db.session.add(goal)

            db.session.commit()

            flash("Savings Goal Configured Successfully!")
            return redirect(url_for("savings"))

    return render_template("configureSavings.html")


if __name__ == "__main__":
 app.app_context().push()
 db.create_all()
 app.run(debug=True)

