from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Cuisine, Base, Recipe, User

engine = create_engine('postgresql://catalog:catalog@localhost/recipecatalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Add all the cuisines
cuisine1 = Cuisine(name="American")
session.add(cuisine1)
session.commit()

cuisine1 = Cuisine(name="Chinese")
session.add(cuisine1)
session.commit()

cuisine1 = Cuisine(name="English")
session.add(cuisine1)
session.commit()

cuisine1 = Cuisine(name="French")
session.add(cuisine1)
session.commit()

cuisine1 = Cuisine(name="Italian")
session.add(cuisine1)
session.commit()

cuisine1 = Cuisine(name="Japanese")
session.add(cuisine1)
session.commit()

cuisine1 = Cuisine(name="Malaysian")
session.add(cuisine1)
session.commit()

cuisine1 = Cuisine(name="Middle Eastern")
session.add(cuisine1)
session.commit()

cuisine1 = Cuisine(name="South Asian")
session.add(cuisine1)
session.commit()

cuisine1 = Cuisine(name="Vegan")
session.add(cuisine1)
session.commit()

print "added Cuisines!"
