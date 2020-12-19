from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import time, datetime, timedelta
import requests

db_path = "./ProjectDesign/db.sqlite3"  # this will need to be changed
engine = create_engine(f'sqlite:///{db_path}')
Base = declarative_base(engine)


class Plantgroup(Base):  # needed
    """"""
    __tablename__ = 'Plantgroup'
    __table_args__ = {'autoload': True}


class Transpiration(Base):  # needed
    """"""
    __tablename__ = 'Transpiration'
    __table_args__ = {'autoload': True}


def loadSession():
    """"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


session = loadSession()

irrigation_times = [(i.water_t1, i.location)
                    for i in session.query(Plantgroup).all()]
irrigation_times = [(i[0].hour * 60 + i[0].minute, i[1])
                    for i in irrigation_times]
now = datetime.now()
now = now.hour * 60 + now.minute


baseurl = "http://localhost:8000"
# check waterlevel
print("checking waterlevel")
requests.get(baseurl + "/check")

# creating new evap object if it's between 4.55 and 5.00
newlevel_min = 4 * 60 + 55
newlevel_max = 5 * 60
if now > newlevel_min and now < newlevel_max:
    print("creating new waterlevel entry")
    requests.get(baseurl+"/create_evap/")

# watering
print("checking if we need to water anything")
for i in irrigation_times:
    if i[0] - now <= 5:
        print(f"watering group {i[1]}")
        requests.get(baseurl + "/water_plantgroup/" + str(i[1]))
