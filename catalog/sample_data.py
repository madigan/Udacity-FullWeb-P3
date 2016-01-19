from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from prod_config import DB_STRING, DB_ECHO
from database_setup import Item

engine = create_engine(DB_STRING, echo=DB_ECHO)
Session = sessionmaker()
Session.configure(bind=engine)

s = Session()

s.add(Item(name="Yeti Plushie", description="Very white."))
s.add(Item(name="Orc Plushie", description="Do not clean."))
s.add(Item(name="Moose Plushie", description="They're actually quite dangerous."))
s.add(Item(name="Elf Plushie", description="Careful! The ears are sharp."))
s.add(Item(name="Beholder Plushie", description="Comes with a free contact lense!"))
s.add(Item(name="Gremlin Plushie", description="Keep away from electronics."))

s.commit()
s.close()
