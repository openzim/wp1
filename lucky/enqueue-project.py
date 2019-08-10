import sys

from redis import Redis
from rq import Queue

import lucky.logic.project as logic_project


def main():
  q = Queue(connection=Redis())

  project_names = sys.argv[1:]
  print(project_names)

  for project_name in project_names:
    print('Enqueuing %s' % project_name)
    q.enqueue(logic_project.update_project_by_name, project_name)


if __name__ == '__main__':
  main()
