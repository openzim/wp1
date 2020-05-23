import logging

from wp1 import queues


def main():
  logging.basicConfig(level=logging.INFO)
  queues.enqueue_all_projects()


if __name__ == '__main__':
  main()
