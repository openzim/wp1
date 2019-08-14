from redis import Redis
from rq import Queue

from lucky import tables


def main():
  upload_q = Queue('upload', connection=Redis(host='redis'))

  print('Enqueuing global table upload')
  upload_q.enqueue(tables.upload_global_table)


if __name__ == '__main__':
  main()
