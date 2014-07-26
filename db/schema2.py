from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, Response
#from misc import cached, refresh_cache
#from threading import Timer
from flask.ext.restless import APIManager
#from sqlalchemy.ext.hybrid import hybrid_property
#import atexit
import json
import os

app = Flask(__name__)

db = SQLAlchemy(app)

DB = 'movies.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{0}'.format(DB)
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False


class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    year = db.Column(db.Integer)
    lang = db.Column(db.Integer, default=u'English')
    watched = db.Column(db.Boolean, default=False)
# since there is only one foreign key, no need to mention the foreign_key
    director_id = db.Column(db.Integer, db.ForeignKey('directors.id'))
    director = db.relationship('Director', lazy='joined', uselist=False)

    _show_fields = ('id', 'name', 'year', 'lang', 'watched')

    def __repr__(self):
        return u"Movie <{0}:{1}>".format(self.name, self.year)

    def to_dict(self):
        _resp = {}
        for m in self._show_fields:
            _resp[m] = getattr(self, m)
        return _resp


class Director(db.Model):
    __tablename__ = 'directors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
#    movies = db.relationship('Movie', lazy='joined', uselist=True)
    movies = db.column_property(
        db.select([Movie.name], whereclause=Movie.director_id == id), deferred=True)

#    @hybrid_property
#    def movies(self):
#        return Movie.query.filter(self.id == Movie.director_id).all()

    def __repr__(self):
        return u"Director <{}>".format(self.name)


base_dir = os.path.dirname(os.path.abspath(__file__))


#@cached()
def get_all_movies():
    _resp = []
    for m in db.session.query(Movie).all():
        _resp.append(m.to_dict())
    return _resp


def get_all_directors():
    _resp = []
    d = db.session.query(Director).all()
    for i in d:
#        _resp.append({i.name: [m.name for m in i.movies]})
        _resp.append({i.name: i.movies})
    return _resp


#@cached()
def get_test(val=None):
    if val:
        return val
    return 100


@app.route('/movies')
def movies():
    return Response(json.dumps(get_all_movies()), mimetype='application/json')


@app.route('/directors')
def directors():
#    return Response(json.dumps(get_all_directors()), mimetype='application/json')
    r = Response(json.dumps(get_all_directors()), mimetype='application/json')
    r.headers['Access-Control-Allow-Origin'] = 'http://fiddle.jshell.net'
    return r


@app.route('/')
def index():
    return Response('<h3>hello world</h3><!-- brathnap-mn1 -->')


def pre_get_many(search_params=None, **kwargs):
    filters = [dict(name='year', op='neq', val=2014)]
    params = dict(filters=filters)
    search_params.update(params)
    print kwargs, 'search_params', search_params


def patch_single(instance_id=None, data=None, **kw):
    print 'instance_id', instance_id
    print 'data', data
    print 'kw', kw


def post_get_single(result=None, **kwargs):
    print 'post_get_single', kwargs
    print 'post_get_single: result', result
    _filter = filter(lambda k: k['year'] == 2014, result['objects'])
    for i in _filter:
        result['objects'].pop(result['objects'].index(i))


def main():
    """
    Main routines
    """
    if not os.path.exists('{0}/{1}'.format(base_dir, DB)):
        db.create_all()
    manager = APIManager(app, flask_sqlalchemy_db=db)
    manager.create_api(Movie,
                       methods=['GET', 'PATCH'],
                       preprocessors={
                           'GET_MANY':  [pre_get_many]
                       },
                       #                   postprocessors= {
                       #                       'PATCH_SINGLE': [patch_single],
                       #                           'GET_MANY': [post_get_single]
                       #                   },
                       include_columns=['name', 'year', 'lang'])
    app.run(debug=True, host='0.0.0.0')

if __name__ == '__main__':
#    t = Timer(35, refresh_cache, ())
#    t.setDaemon(True)
#    atexit.register(t.cancel)
#    t.start()
    main()
