from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_STRING, DB_ECHO
from database_setup import Item, Category

engine = create_engine(DB_STRING, echo=DB_ECHO)
Session = sessionmaker()
Session.configure(bind=engine)

s = Session()

plushie_category = Category(name="Plushies")
plushie_category.items.append(
    Item(name="Yeti Plushie", description="Very white."))
plushie_category.items.append(
    Item(name="Yeti Plushie", description="Very white."))
plushie_category.items.append(
    Item(name="Orc Plushie", description="Do not clean."))
plushie_category.items.append(
    Item(name="Moose Plushie", description="They're actually quite dangerous."))
plushie_category.items.append(
    Item(name="Elf Plushie", description="Careful! The ears are sharp."))
plushie_category.items.append(
    Item(name="Beholder Plushie", description="Comes with a free contact lense!"))
plushie_category.items.append(
    Item(name="Gremlin Plushie", description="Keep away from electronics."))

s.add(plushie_category)

gaming_category = Category(name="Gaming")
gaming_category.items.append(
    Item(name="d6 Pack", description="A pack of random six-sided die!"))
gaming_category.items.append(
    Item(name="Wizard Miniature", description="1 inch base. Pointy hat. Garlic breath."))

s.add(gaming_category)

s.commit()
s.close()
