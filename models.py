#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import datetime
from sqlalchemy import Column, Integer, \
    String, DateTime, Sequence
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Address(Base):
    __tablename__ = "address"

    id = Column(Integer(), Sequence("address_id_seq"), primary_key=True)
    egid = Column(String(250))
    street = Column(String(250))
    nr = Column(String(250))
    zip_code = Column(String(250))
    plz = Column(String(250))
    location = Column(String(250))
    city = Column(String(250))
    bfs_number = Column(String(250))
    created_on = Column(DateTime(), default=datetime.datetime.now)
