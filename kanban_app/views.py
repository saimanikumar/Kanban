from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .database import db
from .model import Todo_list, Card
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
 

views = Blueprint('views', __name__)


@views.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('views.board', user=current_user))
    return render_template("index.html", logged_in=current_user.is_authenticated)


@views.route('/board', methods=["GET", "POST"])
@login_required
def board():
    user_lists = current_user.lists
    user_cards = []
    for i in user_lists:
        user_cards.append(i.cards)
    return render_template("board.html", user=current_user, logged_in=current_user.is_authenticated, 
    user_lists=user_lists, user_cards=user_cards)


#######################################################

@views.route('/list/create', methods=['GET', 'POST'])
def createList():
    if request.method == "POST":
        title = request.form.get("name")
        description = request.form.get("description")

        new_list = Todo_list(
            list_name=title,
            description=description,
            user_id=current_user.id
        )

        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for('views.board', user=current_user))
    return render_template("newList.html", user=current_user)


@views.route('/list/<int:id>/update', methods=['GET', 'POST'])
def updateList(id):
    if request.method == "POST":
        title = request.form.get("name")
        description = request.form.get("description")
        f = Todo_list.query.filter_by(list_id=id).first()
        f.list_name = title
        f.description = description

        db.session.commit()
        return redirect(url_for('views.board', user=current_user))

    z = Todo_list.query.filter_by(list_id=id).first()
    return render_template("editList.html", user=current_user, curr_id=id, curr_list=z)


@views.route('/list/<int:id>/delete', methods=['GET', 'POST'])
def deleteList(id):

    l = Todo_list.query.filter_by(list_id=id).first()
    db.session.delete(l)
    db.session.commit()
    return redirect(url_for('views.board', user=current_user))


############################################################

@views.route('/card/<int:li_id>/create', methods=['GET', 'POST'])
def createCard(li_id):
    if request.method == "POST":

        up_list_id = request.form.get('list-card')

        name = request.form.get('name')
        content = request.form.get('content')
        format = '%Y-%m-%d'
        e_date = request.form.get('deadline')
        new_date = datetime.strptime(e_date, format)

        percent = request.form.get('completed_percent')


        deadline = new_date
        t_date = datetime.today().strftime(format)

        last_updated_date = datetime.strptime(t_date, format)

        todo_list = Todo_list.query.filter_by(list_id=li_id).first()
        todo_list.tasks_remaining += 1
        if percent == '100':
            todo_list.tasks_completed += 1
            todo_list.tasks_remaining -= 1

        new_card = Card(
            card_title=name,
            content=content,
            deadline=deadline,
            li=up_list_id,
            is_complete=percent,
            task_updated_date=last_updated_date
        )

        db.session.add(new_card)
        db.session.commit()
        return redirect(url_for('views.board', user=current_user, t_date=t_date))

    t_date = datetime.today().strftime('%Y-%m-%d')
    return render_template("newCard.html", user=current_user, li_id=li_id, t_date=t_date)


@views.route('/card/<int:c_id>/update', methods=['GET', 'POST'])
def updateCard(c_id):
    if request.method == "POST":

        up_list_id = request.form.get('list-card')
        name = request.form.get('name')
        content = request.form.get('content')
        format = '%Y-%m-%d'
        e_date = request.form.get('deadline')
        new_date = datetime.strptime(e_date, format)
        deadline = new_date
        t_date = datetime.today().strftime('%Y-%m-%d')
        
        last_updated_date = datetime.strptime(t_date, format)
        percent = request.form.get('completed_percent')

        c1 = Card.query.filter_by(card_id=c_id).first()

        c1.deadline = deadline
        c1.content = content
        c1.is_complete = percent
        c1.li = up_list_id
        c1.card_title = name
        c1.task_updated_date = last_updated_date

        todo_list = Todo_list.query.filter_by(list_id=c1.li).first()        
        if percent == '100': 
            todo_list.tasks_completed += 1
            todo_list.tasks_remaining -= 1
        db.session.commit()

        return redirect(url_for('views.board', user=current_user, t_date=t_date))

    c = Card.query.filter_by(card_id=c_id).first()
    li_id = c.li
    t_date = datetime.today().strftime('%Y-%m-%d')
    return render_template("editCard.html", user=current_user, c_id=c_id, li_id=li_id, c=c, t_date=t_date)


@views.route('/card/<int:c_id>/delete', methods=['GET', 'POST'])
def deleteCard(c_id):
    l = Card.query.filter_by(card_id=c_id).first()
    
    todo_list = Todo_list.query.filter_by(list_id=l.li).first()        
    if l.is_complete == 100:
        todo_list.tasks_completed += 1
    else:
        todo_list.tasks_remaining -= 1

    db.session.delete(l)
    db.session.commit()

    return redirect(url_for('views.board'))


############################################################

@views.route('/board/summary', methods=["GET", "POST"])
@login_required
def summary():
    sns.set()
    user_lists = current_user.lists
    for i in user_lists:
        plt.clf()
        titles = []

        for j in range(len(i.cards)):
            b = None
            if i.cards[j].task_updated_date != None:
                b = i.cards[j].task_updated_date.strftime('%d-%m-%Y')
            if b != None:
                titles.append(i.cards[j].card_title + f"_{j+1}\n" + b)
            else:
                titles.append(i.cards[j].card_title + f"_{j+1}\n")

        y = [j.is_complete for j in i.cards]
        plt.ylim([0, 100])
        plt.bar(titles, y)

        if titles == []:
            continue
        plt.savefig(f"kanban_app\static\graphs\list_{i.list_id}")


    t_date = datetime.today()
    return render_template("summary.html", user=current_user, logged_in=current_user.is_authenticated, user_lists=user_lists,t_date=t_date )


