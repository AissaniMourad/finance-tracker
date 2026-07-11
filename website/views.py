from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Transaction
from . import db

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    income = sum(t.amount for t in transactions if t.type == "income")
    expenses = sum(t.amount for t in transactions if t.type == "expense")
    balance = round(income - expenses, 2)

    categories = {}
    for t in transactions:
        if t.type == "expense":
            categories[t.category] = categories.get(t.category, 0) + t.amount

    return render_template("dashboard.html", transactions=transactions, income=income, expenses=expenses, balance=balance, categories=categories, user=current_user)


@views.route('/add-transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        description = request.form.get("description")
        amount = request.form.get("amount")
        type = request.form.get("type")
        category = request.form.get("category")

        new_transaction = Transaction(
            description=description, amount=amount, type=type, category=category, user_id=current_user.id)
        db.session.add(new_transaction)
        db.session.commit()
        flash("Transaction added!", category='success')
        return redirect(url_for('views.dashboard'))
    return render_template("add_transaction.html", user=current_user)


@views.route('/delete-transaction/<int:id>', methods=['POST'])
@login_required
def delete_transaction(id):
    transaction = Transaction.query.get(id)
    if transaction.user_id == current_user.id:
        db.session.delete(transaction)
        db.session.commit()
        flash("Transaction deleted!", category='seccess')
    return redirect(url_for('views.dashboard'))
