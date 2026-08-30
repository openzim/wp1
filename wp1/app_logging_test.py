import logging

from wp1.app_logging import configure_logging
from wp1.config import override_settings


class AppLoggingTest:
    """This is a pytest test class, because we want to use the `caplog` fixture."""

    @override_settings(
        LOGGING={
            "*": {
                "level": "DEBUG",
                "format": "%(levelname)s:test:%(message)s",
            },
            "wp1.component": {"level": "INFO"},
        }
    )
    def test_configure_logging(self, caplog):
        configure_logging()

        root = logging.getLogger()
        root.debug("root debug message")
        root.warning("root warning message")

        component_logger = logging.getLogger("wp1.component")
        component_logger.debug("component debug message")
        component_logger.error("component error message")

        assert caplog.record_tuples == [
            ("root", logging.DEBUG, "root debug message"),
            ("root", logging.WARNING, "root warning message"),
            ("wp1.component", logging.ERROR, "component error message"),
        ]
