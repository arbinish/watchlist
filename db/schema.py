from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    create_engine
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os


Base = declarative_base()
DB = 'movies.db'


class Movie(Base):
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    year = Column(Integer)
    lang = Column(Integer, default=u'English')
    watched = Column(Boolean, default=False)

    def __repr__(self):
        return u"Movie <{0}:{1}>".format(self.name, self.year)


base_dir = os.path.dirname(os.path.abspath(__file__))
engine = create_engine(
    'sqlite:///{0}/{1}'.format(base_dir, DB), echo=False)
Session = sessionmaker(bind=engine)


def main():
    """
    Main routines
    """
    if not os.path.exists('{0}/{1}'.format(base_dir, DB)):
        Base.metadata.create_all(engine)


if __name__ == '__main__':
    main()
