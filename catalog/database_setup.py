from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from config import DB_STRING, DB_ECHO

Base = declarative_base()

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    def __repr__(self):
        return "<Item(id='%s', name='%s', description='%s')>" % ( 
            self.id, self.name, self.description)

# Re-build the database
if __name__ == "__main__":
    engine = create_engine(DB_STRING, echo=DB_ECHO)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
