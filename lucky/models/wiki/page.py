from sqlalchemy import Table, Column, Integer, Binary, TIMESTAMP, MetaData, join, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property

metadata = MetaData()

page_table = Table(
  'page', metadata,
  Column('page_id', Integer, primary_key=True),
  Column('page_namespace', Integer),
  Column('page_title', Binary(255)))

category_links_table = Table(
  'categorylinks', metadata,
  Column('cl_from', Integer, ForeignKey('page.page_id')),
  Column('cl_to', Binary(255)),
  Column('cl_timestamp', TIMESTAMP))

page_category_join = join(page_table, category_links_table)

_Base = declarative_base()

class Page(_Base):
  __table__ = page_category_join

  id = column_property(page_table.c.page_id,
                              category_links_table.c.cl_from)
  title = page_table.c.page_title
  namespace = page_table.c.page_namespace
  category = category_links_table.c.cl_to
  timestamp = category_links_table.c.cl_timestamp

  def __repr__(self):
    return "<Page(page_id=%r, page_title=%r, page_namespace=%r)>" % (
      self.page_id, self.page_title, self.page_namespace)
