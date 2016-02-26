## Udacity FSND Project 3 Item Catalog

### Pre-requisites

This project has been developed in a Linux environment and requires
the following programs to build from scratch:

 - one of postgresql or sqlite
 - sqlalchemy
 - flask

Now you can download, build
and view the website as follows:

```
$ git clone https://github.com/alcarruth/fullstack-p3-item-catalog.git
$ cd fullstack-p3-item-catalog
```

Edit the options.py to suit your situation.  In particular, the variable
`engine-type` should be set to the db backend of your choice.  The code
has been tested and seems to work well with postgresql 9.3.11 and with
whatever sqlite I've got. (what is it?)  Once this is done, rebuild the
database usint the script `reset_db.sh`.  With the default dummy data
table sizes, this takes a few seconds and produces something like the 
following terminal output:

```
$ ./reset_db.sh 
DROP DATABASE
CREATE DATABASE
removed ‘tickets.db’
loading 10 conferences
loading 128 teams
schecduling 77 games
schecduling 66 games
schecduling 77 games
schecduling 66 games
schecduling 77 games
schecduling 71 games
schecduling 71 games
schecduling 66 games
schecduling 66 games
schecduling 66 games
creating 1000 users
creating 5000 ticket lots
0
1000
2000
3000
4000
created 13793 tickets
```

Now the db has been initialized and you can run the ticket app server:

```
$ ./web_server.py 
 * Running on http://0.0.0.0:5000/
 * Restarting with reloader
```

Point your browser to `http://localhost:5000` to view the Tickets'R'Us 
web app.


### Project Overview

The original nanodegree project has been extensively refactored.
First, the project has been split into two, **Pizza App** and **Mobile Portfolio**.
Each of these has its own subdirectory containing `src` and `dist` subdirectories, and 
a `gulpfile.js`.  Each project can be built separately by changing to its root directory
and issuing the `gulp` command.

However, the two projects share a single `node_modules` directory and `package.json` file
in the root directory of this repository.

### Mobile Portfolio

The mobile portfolio site was optimized and tested with 
[PageSpeed Insights](https://developers.google.com/speed/pagespeed/insights/).
The following optimizations were made:

Stylesheets:
 - webfonts - Open_Sans was downloaded and inlined
 - style.css - minified with gulp-cleancss and inlined
 - print.css - minified with gulp-cleancss and inlined

Scripts:
 - google_analytics.js: `async` property added
 - perfmatters.js:  minified and inlined
 - google_analitics_profile.js: minified and inlined

images:
 - profilepic.jpg: compressed
 - mobilewebdev.jpg: compressed
 - cam_be_like.jpg: compressed


### Pizza App

The Pizza App site has been completely overhauled.  The main.js file was
split into six files:

 - animation_loop.js
 - pizza_app.js
 - pizza_designer.js
 - pizza_menu.js
 - sliding_pizzas.js
 - timer.js

![alt text](fullstack-p3-item-catalog/images/jpg/tickets_step1.jpg, "main page")



Extensive documentation can be found in the comments in these files, but here
is an overview.

#### pizza_app.js
pizza_app.js is the main entry point into the code. It defines, instantiates
and initializes a PizzaApp object.

```
window.pizzaApp = PizzaApp();
```

#### pizza_designer.js

pizza_designer.js contains the code for generating the pizzas for the menu.
A big change is that it only generates what I'm calling _semantic pizzas_, that is
JavaScript objects containing no HTML.  These are later combined with a _view_
template to create the actual HTML for the page.

So pizza_designer.js includes the lists of nouns, adjectives and
ingredients from the original.  The random generator code has been
cleaned up and modularized in an attempt to make it more cohesive,
comprehensible and "easy on the eyes".  And the two default pizzas,
_The Udacity Special_, and _The Cameron Special_, which were
previously a part of index.html, are now semantic _secialty pizzas_ in
the pizza designer.

#### pizza_menu.js
pizza_menu.js contains the code that generates the menu pizzas, using PizzaDesigner
and Mustache to fill the menu items portion of the page.  It also contains
the code to update the pizza sizes when the slider is changed.

#### sliding_pizzas.js
sliding_pizzas.js contains the code for the crazy sliding pizzas page background.
It contains two class definitions, SlidingPizza, and SlidingPizzasBackground.
Again, this code has been tidied up considerably, moving non central functionality
like timing and animation to separate files.  This results in code that allows
one to focus on the core functionality with minimal obfuscation.

#### timer.js
The timing code in the original is very cool as Cameron has testified, but 
I felt like it cluttered things up considerably.  It was/is used in three places
1. generating pizzas, 2. resizing pizzas and 3. scrolling updates, and each of 
these had essentially the same timer code.  I tried to abstract the similar
timing code and ended up with a function `timerWrap()` which could wrap
another function and do the timing.  This generalization resulted in
much cleaner code for the functions that were being timed.

#### animation_loop.js
animation_loop.js is probably the most interesting of the bunch.  In trying
to get my head around `requestAnimationFrame()` I realized that I had
to use the tail-recursive calls as in all the examples, but I didn't want
the loop to run forever, only when scrolling.  So I needed to be able
to exit the loop when we were no longer scrolling and start it again
when a `scroll` event happened.

After wrestling with it _in situ_, I decided to pull it out into a separate
function so that `updatePositions()` could focus on updating positions and
not have to worry about the bigger picture.

Eventually I realized that there was an inherent mis-match here between
`scroll` _events_ and a scrolling _condition_, the former being ephemeral
or instantaneous, and the latter having some longer duration.  I wanted
the animation to start when a `scroll` event was received continue until
we were no longer scrolling, which meant that we had not received a
`scroll` event in some period of time.

So, anyway, separating the animation management from the position
updating allowed me to focus on one at a time, without being concerned
with the other.  And it seems that the resulting code `animationLoop()`
says something fundamental about the relationship between events
and conditions that might be re-used elsewhere, certainly in animation
but possibly beyond that.

### Status

I'm still playing with it. 
Most of the optimization targets were met by just refactoring the 
for loops, moving unnecessary code out of inner loops and maintaining
in memory a list of pizza elements so that there was no need to
query the document each time around.

All of the timing tests seem to pass with flying colors except for the
60 frames per second.  In DevTools, the CPU time required for each
frame is usually around 10 ms, but the rest of the frame is hollow
with nothing in it.

I've tried a number of things to improve the timing

 - I reduced the number of sliding pizzas to 8 columns by 5 rows.
   Definitely a win.
 - I tried to reduce the size of the DOM.  The original code
   had a lot of `<div>`s to handle the bootstrap formatting.
   I got rid of bootstrap and relied on flex-box instead.
   Not sure what to make of this, but I do prefer the flex-box way.
 - putting all the sliding pizzas on a sliding_pizzas layer.
   I did this by changing the CSS.  The sliding pizzas had
   z-index: inerit and their container had z-index: 1.
 - putting them on one of 5 layers according to their 'phase'.
   This way the whole layer could be shifted by dx, instead
   of shifting each pizza individually.  This actually worked
   and I thought it was pretty cool but the painter and compositor
   did not care much for it. 
 - putting them each on their own layer.  This is the current
   best approach.
 - I tried using opaque sliding pizza images with a black background
   thinking it might take some of the pressure off of the compositor.
   This seemed not to work.
 - I resized the pizza images (both sliding and menu) to their
   eventual display size.  This helped a bit.

I also tried:

 - two different OS's: OSX and Linux
 - four or five different versions of google-chrome/chromium
 - changing chrome:flags like GPU blacklist
 - installing the nVida proprietary binary drivers (on Linux)
 - taking a week off to just play JankInvaders.  I got pretty
   good at it.

### License

Probably GNU or MIT or BSD ... I don't know.
