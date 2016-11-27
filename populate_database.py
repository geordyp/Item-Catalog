from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a 'staging zone' for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# The category objects below MUST be added
category1 = Category(name='Games')
session.add(category1)
session.commit()

category2 = Category(name='Movies')
session.add(category2)
session.commit()

category3 = Category(name='Music')
session.add(category3)
session.commit()

category4 = Category(name='Books')
session.add(category4)
session.commit()

category5 = Category(name='Podcasts')
session.add(category5)
session.commit()

category6 = Category(name='TV Shows')
session.add(category6)
session.commit()

# Anything below this point is just filler data, safe to remove or comment out
user1 = User(name='Paul', email='paul@gmail.com')
session.add(user1)
session.commit()

item1 = Item(title='The Last of Us',
             description='The Last of Us is an action-adventure survival horror video game developed by Naughty Dog and published by Sony Computer Entertainment. It was released for the PlayStation 3 in June 2013.',
             category_id=category1.id,
             user_id=user1.id)
session.add(item1)
session.commit()

item2 = Item(title='Ex Machina',
             description='Caleb Smith (Domhnall Gleeson) a programmer at a huge Internet company, wins a contest that enables him to spend a week at the private estate of Nathan Bateman (Oscar Isaac), his firm's brilliant CEO. When he arrives, Caleb learns that he has been chosen to be the human component in a Turing test to determine the capabilities and consciousness of Ava (Alicia Vikander), a beautiful robot. However, it soon becomes evident that Ava is far more self-aware and deceptive than either man imagined.',
             category_id=category2.id,
             user_id=user1.id)
session.add(item2)
session.commit()

item3 = Item(title='XCOM 2',
             description='XCOM 2 is a turn-based tactics video game developed by Firaxis Games and published by 2K Games. It was released for Microsoft Windows, OS X, and Linux in February 2016, and for PlayStation 4 and Xbox One in September 2016.',
             category_id=category1.id,
             user_id=user1.id)
session.add(item3)
session.commit()

item4 = Item(title='Between the World and Me',
             description='Between the World and Me is a 2015 book written by Ta-Nehisi Coates and published by Spiegel & Grau.',
             category_id=category4.id,
             user_id=user1.id)
session.add(item4)
session.commit()

item5 = Item(title='Starboy',
             description='Starboy is the third studio album by Canadian singer and songwriter The Weeknd. It was released on November 25, 2016 by XO and Republic Records.',
             category_id=category3.id,
             user_id=user1.id)
session.add(item5)
session.commit()

item6 = Item(title='The Great Gatsby',
             description='The Great Gatsby is a 1925 novel written by American author F. Scott Fitzgerald that follows a cast of characters living in the fictional town of West Egg on prosperous Long Island in the summer of 1922.',
             category_id=category4.id,
             user_id=user1.id)
session.add(item6)
session.commit()

item7 = Item(title='Thriller',
             description='Thriller 25 is the 25th anniversary edition reissue of American recording artist Michael Jackson's sixth studio album Thriller. The original album sold between 51 and 65 million copies worldwide, making it the world's best selling album of all time.',
             category_id=category3.id,
             user_id=user1.id)
session.add(item7)
session.commit()

item8 = Item(title='This American Life',
             description='This American Life (TAL) is an American weekly hour-long radio program produced by WBEZ and hosted by Ira Glass. It is broadcast on numerous public radio stations in the United States and internationally, and is also available as a free weekly podcast.',
             category_id=category5.id,
             user_id=user1.id)
session.add(item8)
session.commit()

item9 = Item(title='Radiolab',
             description='Radiolab is a radio program produced by WNYC, a public radio station in New York City, and broadcast on public radio stations in the United States.',
             category_id=category5.id,
             user_id=user1.id)
session.add(item9)
session.commit()

item10 = Item(title='Breaking Bad',
             description='Mild-mannered high school chemistry teacher Walter White thinks his life can't get much worse. His salary barely makes ends meet, a situation not likely to improve once his pregnant wife gives birth, and their teenage son is battling cerebral palsy. But Walter is dumbstruck when he learns he has terminal cancer. Realizing that his illness probably will ruin his family financially, Walter makes a desperate bid to earn as much money as he can in the time he has left by turning an old RV into a meth lab on wheels.',
             category_id=category6.id,
             user_id=user1.id)
session.add(item10)
session.commit()

print 'populated the database!'
