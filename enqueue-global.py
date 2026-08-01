from wp1 import app_logging, maintenance


def main():
    app_logging.configure_logging()
    maintenance.enqueue_global()


if __name__ == "__main__":
    main()
