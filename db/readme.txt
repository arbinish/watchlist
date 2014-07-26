session = Session()
session.query(Movie).all()
session.query(Movie).filter(Movie.name.in_(['Lucy', 'Non-Stop'])).all()
session.query(Movie).filter(Movie.year < 2014)

session.add(Movie(name='name', year=2014, lang='English', watched=False))
session.add(Movie(name='name2', year=2014))
session.commit()

# Further read
# http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html
