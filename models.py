from sqlalchemy import Column, Integer, String, Numeric, CheckConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from string import ascii_letters, digits, punctuation

from settings import DB_URI

Base = declarative_base()

class Log(Base):
	__tablename__ = "tb_log"
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
	tickno = Column(Integer, nullable=True)


class Game(Base):
	__tablename__ = "tb_game"	
	g_name = Column(String, primary_key=True)


class Counter(Base):
	__tablename__ = "tb_counter"
	c_name = Column(String, primary_key=True)
	c_value = Column(Integer, nullable=False)


class User(Base):
	__tablename__ = "tb_user"
	u_id = Column(Integer, primary_key=True)
	u_name = Column(String, unique=True)
	u_email = Column(String(254), unique=True)  # RFC 3696
	u_password = Column(String(64))  # SHA256

	# re.match("^[A-Za-z0-9!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{4,}$", u_name)
	CheckConstraint("len(u_name) > 4 and all(map(lambda l: l in ascii_letters or l in digits or l in punctuation, u_name))")


class Score(Base):
	__tablename__ = "tb_score"
	g_name = Column(String, ForeignKey("tb_game.g_name", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
	u_id = Column(Integer, ForeignKey("tb_user.u_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
	score = Column(Integer, nullable=False)

	CheckConstraint("score >= 0")


engine = create_engine(DB_URI)
Session = sessionmaker(bind=engine)