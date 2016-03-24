#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from tickets import DBSession, Conference, Team, Game, Ticket, Ticket_Lot, User

app = Flask(__name__)

session = DBSession()

#-------------------------------------------------------------------------
# Conferences

@app.route('/')
@app.route('/conferences')
def conferences():
    conferences = session.query(Conference).all()
    return render_template('conferences.html', conferences=conferences)

#-------------------------------------------------------------------------
# Conference

@app.route('/conference/<conference>')
def conference(conference):
    conference = session.query(Conference).filter_by(abbrev_name=conference).one()
    return render_template('conference.html', conference=conference)

@app.route('/conference/<conference>/JSON')
def conference_json(conference):
    conference = session.query(Conference).filter_by(abbrev_name=conference).one()
    return jsonify(conference.serialize())

#-------------------------------------------------------------------------
# Team

@app.route('/team/<team_name>')
def team(team_name):
    team = session.query(Team).filter_by(name=team_name).one()
    return render_template('team.html', team=team)

@app.route('/team/<team_name>/JSON')
def team_json(team_name):
    team = session.query(Team).filter_by(name=team_name).one()
    return jsonify(team.serialize())

#-------------------------------------------------------------------------
# Game

@app.route('/game/<game_id>')
def game(game_id):
    game = session.query(Game).filter_by(id=game_id).one()
    game.ticket_lots.sort(key = lambda x: x.price)
    return render_template('game_tickets.html', game=game)

@app.route('/game/<game_id>/JSON')
def game_json(game_id):
    game = session.query(Game).filter_by(id=game_id).one()
    return jsonify(game.serialize())

#-------------------------------------------------------------------------
# Tickets

@app.route('/tickets/<ticket_lot_id>')
def ticket_lot(ticket_lot_id):
    ticket_lot = session.query(Ticket_Lot).filter_by(id=ticket_lot_id).one()
    return render_template('ticket_lot.html', ticket_lot=ticket_lot)

@app.route('/tickets/<ticket_lot_id>/JSON')
def ticket_lot_json(ticket_lot_id):
    ticket_lot = session.query(Ticket_Lot).filter_by(id=ticket_lot_id).one()
    return jsonify(ticket_lot.serialize())

#-------------------------------------------------------------------------
# User

@app.route('/users')
def users():
    users = session.query(User).all()
    return render_template('users.html', users=users)

@app.route('/users/<int:user_id>')
def user(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return render_template('user.html', user=user)

@app.route('/users/<int:user_id>/JSON')
def user(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return jsonify(user.serialize())

#-------------------------------------------------------------------------
# add a new item to a category
#
@app.route('/catalog/<category_name>/new', methods=['GET', 'POST'])
def add_item(category_name):

    if request.method == 'POST':
        session.add( new_item = Item(
            name = request.form['name'],
            price = request.form['price'],
            description = request.form['description'],
            cat_id = request.form['cat_id'],
            user_id = request.form['user_id']))
        session.commit()
        flash('New menu item created: %s.' % new_menu_item.name)
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

    else:
        category = session.query(Category).filter_by(name=category_name).one()
        return render_template('new_menu_item.html', restaurant=restaurant)

# edit menu item
#
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    #print 'edit menu item %d for restaurant %d' % (restaurant_id, menu_id)
    if request.method == 'POST':
        menu_item = session.query(MenuItem).filter_by(id=menu_id).one()
        menu_item.name = request.form['name'],
        menu_item.price = request.form['price'],
        menu_item.description = request.form['description']
        session.commit()
        flash('Menu item edited: %s.' % menu_item.name)
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        menu_item = session.query(MenuItem).filter_by(id=menu_id).one()
        return render_template('edit_menu_item.html', restaurant=restaurant, menu_item=menu_item)


# delete menu item
#
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    if request.method == 'POST':
        menu_item = session.query(MenuItem).filter_by(id=menu_id).one()
        menu_item_name = menu_item.name
        #print 'deleting %s'
        session.delete(menu_item)
        session.commit()
        flash('Menu item deleted: %s.' % menu_item_name)
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        menu_item = session.query(MenuItem).filter_by(id=menu_id).one()
        return render_template('delete_menu_item.html', restaurant=restaurant, menu_item=menu_item)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)


