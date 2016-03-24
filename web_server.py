#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from catalog import DBSession, Item, Category, User

app = Flask(__name__)

session = DBSession()

#-------------------------------------------------------------------------
# Catalog Main

@app.route('/')
@app.route('/catalog')
def catalog():
    categories = session.query(Category).all()
    return render_template('categories.html', categories=categories)

#-------------------------------------------------------------------------
# Category

@app.route('/catalog/<category_name>')
def category(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(cat_id=category.id).all()
    return render_template('category.html', category=category, items=items)

@app.route('/catalog/<category_name>/JSON')
def category(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    #items = session.query(Items).filter_by(cat_id=category.id).all()
    return jsonify(category.serialize())

#-------------------------------------------------------------------------
# Item

@app.route('/catalog/<category_name>/<item_name>')
def item(category_name, item_name):
    item = session.query(Items).filter_by(name=item_name).one()
    return render_template('item.html', item=item)

@app.route('/catalog/<category_name>/<item_name>/JSON')
def item(category_name, item_name):
    item = session.query(Items).filter_by(name=item_name).one()
    return jsonify(item.serialize())

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

@app.route('/users/<int:user_id>')
def user(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return jsonify(user.serialize())


#-------------------------------------------------------------------------
# add a new item to a category
#
@app.route('/catalog/<str:category_name>/new', methods=['GET', 'POST'])
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


