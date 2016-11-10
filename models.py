from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import DB_URI

Base = declarative_base()

class Log(Base):
	__tablename__ = "log"
	id = Column(Integer, primary_key=True)
	created = Column(Numeric, nullable=False)
	exc_text = Column(String, nullable=True)
	filename = Column(String, nullable=False)
	levelname = Column(String, nullable=False)
	levelno = Column(Integer, nullable=False)
	lineno = Column(Integer, nullable=False)
	module = Column(String, nullable=False)
	message = Column(String, nullable=False)
	pathname = Column(String, nullable=False)
	playerid = Column(Integer, nullable=True)
	gameid = Column(Integer, nullable=True)

	def __repr__(self):
		return "<Log({})>".format(
			", ".join(
				map(
					lambda x: x + "=" + str(getattr(self, x)), 
					(x for x in dir(self) if not x.startswith("__"))
					)
				)
			)


class StoredId(Base):
	__tablename__ = "storedid"
	name = Column(String, primary_key=True)
	storedid = Column(Integer, nullable=False)

engine = create_engine(DB_URI)
session = sessionmaker(bind=engine)()