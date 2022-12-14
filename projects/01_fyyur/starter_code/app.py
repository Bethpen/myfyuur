#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from datetime import date
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from collections import defaultdict
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
## DONE
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

Shows = db.Table('shows',
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
    db.Column('start_time', db.DateTime),
    db.Column('venue_name', db.String()),
    db.Column('artist_name', db.String()),
    db.Column('artist_image_link', db.String(500)),
)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(200))
    s_talent = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(200))
    s_venue = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(500))
    venues = db.relationship('Venue', secondary=Shows, backref=db.backref('artists', lazy=True))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # return render_template('venues.html', area=)
  all_venue = Venue.query.all()
  venue_list = []

  for i in all_venue:
    venue_list.append({
      "city": i.city,
      "state":i.state,
      "venues":[{
        "id":i.id,
        "name":i.name,
        # "num_upcoming_shows":i.upcoming_shows_count
      }]
    })
  
  return render_template('pages/venues.html', areas=venue_list)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }

  search_key = request.form.get('search_term', '')
  venues = []
  venues.append(Venue.query.filter(Venue.name.ilike(f'%{search_key}')).first())
  venues.append(Venue.query.filter(Venue.name.ilike(f'%{search_key}%')).first())
  venues.append(Venue.query.filter(Venue.name.ilike(f'{search_key}%')).first())

  for i in venues:
    if i== None:
      venues.remove(i)

  venues_result={
    "count":len(venues),
    "data": venues
  }

  print(venues_result['data'][0])

  return render_template('pages/search_venues.html', results=venues_result, search_term=search_key)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    data= Venue.query.get(venue_id)

    if data.genres[0] == '{':
      data.genres = data.genres.split('{')[1].split('}')[0].split(',')
    else:
      data.genres=data.genres.split(',')

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error= False
  try:
    venue_new = Venue(
      name = request.form.get('name'),
      city= request.form.get('city'),
      state= request.form.get('state'),
      phone= request.form.get('phone'),
      address= request.form.get('address'),
      genres= request.form.getlist('genres'),
      image_link= request.form.get('image_link'),
      facebook_link= request.form.get('facebook_link'),
      s_talent= request.form.get('seeking_talent'),
      description= request.form.get('seeking_description'),
      website_link= request.form.get('website_link')
    )
    try:
      if (request.form.get('seeking_talent')):
        venue_new.s_talent =True
    except:
      venue_new.s_talent =False

    print(venue_new)
    db.session.add(venue_new)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # on unsuccessful db insert, flash an error instead.
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist = Artist.query.all()
  return render_template('pages/artists.html', artists=artist)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }

  search_key = request.form.get('search_term', '')
  artists = []
  artists.append(Venue.query.filter(Venue.name.ilike(f'%{search_key}')).first())
  artists.append(Venue.query.filter(Venue.name.ilike(f'%{search_key}%')).first())
  artists.append(Venue.query.filter(Venue.name.ilike(f'{search_key}%')).first())

  for i in artists:
    if i== None:
      artists.remove(i)

  artists_result={
    "count":len(artists),
    "data": artists
  }

  print(artists_result['data'][0])

  return render_template('pages/search_artists.html', results=artists_result, search_term=search_key)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist= Artist.query.get(artist_id)

  if artist.genres[0] == '{':
    artist.genres = artist.genres.split('{')[1].split('}')[0].split(',')
  else:
    artist.genres=artist.genres.split(',')

  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  new_artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=new_artist)

  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_artist": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=new_artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

 
  artist = Artist.query.get(artist_id)
  artist.name = request.form.get('name','')
  artist.city = request.form.get('city','')
  artist.state = request.form.get('state','')
  artist.phone = request.form.get('phone','')
  artist.address = request.form.get('address','')
  artist.genres = request.form.get('genres','')
  artist.facebook_link = request.form.get('facebook_link','')
  artist.image_link = request.form.get('image_link','')
  artist.website_link = request.form.get('website_link','')
  if request.form.get('looking_for_artists','') == '':
    artist.looking_for_talent = False
  else:
    artist.looking_for_talent = True
  artist.seeking_description = request.form.get('seeking_description','')

  try:
    db.session.commit()
    flash('artist ' + artist.name + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('artist ' + artist.name + ' could not be updated!')
  finally:
    db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  new_venue = Venue.query.get(venue_id)
  form = VenueForm(obj=new_venue)
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=new_venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name','')
    venue.city = request.form.get('city','')
    venue.state = request.form.get('state','')
    venue.phone = request.form.get('phone','')
    venue.address = request.form.get('address','')
    venue.genres = request.form.get('genres','')
    venue.facebook_link = request.form.get('facebook_link','')
    venue.image_link = request.form.get('image_link','')
    venue.website_link = request.form.get('website_link','')
    if request.form.get('looking_for_venues','') == '':
      venue.looking_for_talent = False
    else:
      venue.looking_for_talent = True
    venue.seeking_description = request.form.get('seeking_description','')

    db.session.commit()
    flash('venue ' + venue.name + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('venue ' + venue.name + ' could not be updated!')
  finally:
    db.session.close()


  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error= False
  try:
    artist_new = Artist(
      name = request.form.get('name'),
      city= request.form.get('city'),
      state= request.form.get('state'),
      phone= request.form.get('phone'),
      genres= request.form.getlist('genres'),
      image_link= request.form.get('image_link'),
      facebook_link= request.form.get('facebook_link'),
      s_venue= request.form.get('seeking_venue'),
      description= request.form.get('seeking_description'),
      website_link= request.form.get('website_link')
    )
    try:
      if (request.form.get('seeking_venue')):
        artist_new.s_venue =True
    except:
      artist_new.s_venue =False

    print(artist_new)
    db.session.add(artist_new)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # on unsuccessful db insert, flash an error instead.
  else:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = shows.query.all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error= False
  artist_id = request.form.get('artist_id')
  venue_id= request.form.get('venue_id')
  artist = Artist.query.get(artist_id)
  venue = Venue.query.get(venue_id)
  try:
    new_show = Shows.insert().values(
      artist_id = artist_id, 
      venue_id= venue_id, 
      artist_name =artist.name,
      venue_name =venue.name,
      artist_image_link = artist.image_link,
      start_time= request.form.get('start_time')
      )
    db.session.execute(new_show)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  else:
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
