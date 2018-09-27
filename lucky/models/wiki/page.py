from sqlalchemy import Table, Column, TIMESTAMP, MetaData, join, ForeignKey
from sqlalchemy.dialects.mysql import BINARY, INTEGER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property

from conf import get_conf

config = get_conf()
ARTICLES_LABEL_STR = config['ARTICLES_LABEL']
BY_QUALITY_STR = config['BY_QUALITY']

metadata = MetaData()

page_table = Table(
  'page', metadata,
  Column('page_id', INTEGER(8, unsigned=True), primary_key=True),
  Column('page_namespace', INTEGER(11)),
  Column('page_title', BINARY(255)))

category_links_table = Table(
  'categorylinks', metadata,
  Column('cl_from', INTEGER(8, unsigned=True), ForeignKey('page.page_id')),
  Column('cl_sortkey', BINARY(230)),
  Column('cl_to', BINARY(255)),
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
  sortkey = category_links_table.c.cl_sortkey

  def __repr__(self):
    return "<Page(page_id=%r, page_title=%r, page_namespace=%r)>" % (
      self.id, self.title, self.namespace)

  @property
  def base_title(self):
    bytes_to_replace = ('_%s_%s' %
                        (ARTICLES_LABEL_STR, BY_QUALITY_STR)).encode('utf-8')
    return self.title.replace(bytes_to_replace, b'')
