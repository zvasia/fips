# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, LargeBinary, ForeignKey, String, Date, Text, DateTime


Base = declarative_base()


class Certificate(Base):
    __tablename__ = 'final_tosn'

    id = Column(Integer, primary_key=True)
    os_id = Column(Integer, nullable=False)
    num = Column('B111', Integer, unique=True)
    full_num = Column('B111_ADD', String(50), nullable=False, default='')
    type = Column('B130', String(5))
    country = Column('B190', String(5), nullable=False)
    application_number = Column('B210', String(15))
    application_number_clean = Column('B210_CLEAN', Integer)
    valid_until = Column('B181', Date)
    application_date = Column('B220', Date)
    registration_date = Column('B151', Date)
    owner = Column('B732', Text)
    owner_translit = Column('B732_translit', Text)
    owner_address = Column('B750', Text)
    b900 = Column('B900', Integer)
    colors = Column('B591', Text)
    publishing_date = Column('B450', Date)
    priority = Column('B221', Date)

    status = Column('PO_Status', String(45))
    status_date = Column('PO_Status_Date', DateTime)

    create_date = Column('Create_Date', DateTime)
    update_date = Column('Update_Date', DateTime)


class ICGS(Base):
    __tablename__ = 'final_ttov'

    id = Column(Integer, primary_key=True)
    cert = Column('os_id', Integer, ForeignKey("final_tosn.os_id"), nullable=False)
    cls = Column('B511A', Integer, nullable=False)
    descr_ru = Column('B511', Text, nullable=False)
    descr_en = Column('B511_en', Text, nullable=True)


class Pics(Base):
    __tablename__ = 'final_tpic'

    id = Column(Integer, primary_key=True)
    image = Column('T12', LargeBinary(length=(2 ** 32) - 1))
    cert = Column('os_id', Integer, ForeignKey("final_tosn.os_id"), nullable=False)
