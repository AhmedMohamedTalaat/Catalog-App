from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Categories, Items

engine = create_engine("sqlite:///catalogApp.db")
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()


def save(obj):
    try:
        session.add(obj)
        session.commit()
        return True
    except:
        print("error while saving")


user1 = User(name="ahmed", email='bb@bb.com', )
save(user1)

cate1 = Categories(user_id=1, name="Food", )
save(cate1)

item1 = Items(cate_id=1, name="Tuna", description="sea food")
save(item1)
item2 = Items(cate_id=1, name="salamon", description="salamon fish")
save(item2)
item3 = Items(cate_id=1, name="shrimpo", description="shrimpo jampo")
save(item3)

cate2 = Categories(user_id=1, name="Games")
save(cate2)
item4 = Items(cate_id=2, name="BF1", description="shooting")
save(item4)
item5 = Items(cate_id=2, name="NFS", description="racing car")
save(item5)
item6 = Items(cate_id=2, name="MH", description="war")
save(item6)

cate3 = Categories(user_id=1, name="Football")
save(cate3)
item7 = Items(cate_id=3, name="T-shrit", description="soccer t-shirt")
save(item7)
item8 = Items(cate_id=3, name="Football", description="football")
save(item8)
item8 = Items(cate_id=3, name="short", description="short")
save(item8)

user2 = User(name="ali", email='bb@bb.com', )
save(user2)
cate2 = Categories(user_id=2, name="Entertainment", )
save(cate2)
item9 = Items(cate_id=2, name="PS4", description="console")
save(item9)

print("saved into database")
