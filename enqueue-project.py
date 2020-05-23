import logging
import sys

from wp1 import queues


def main():
  logging.basicConfig(level=logging.INFO)

  # Job methods expect project names as bytes.
  project_names = [n.encode('utf-8') for n in sys.argv[1:]]
  logger.debug(project_names)

  queues.enqueue_multiple_projects(project_names)


if __name__ == '__main__':
  main()
