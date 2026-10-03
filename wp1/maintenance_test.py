import time
from unittest.mock import call, patch

from rq import Queue
from rq.registry import StartedJobRegistry

from wp1 import maintenance
from wp1.base_db_test import BaseWpOneDbTest
from wp1.config import override_settings
from wp1.environment import Environment


class MaintenanceTest(BaseWpOneDbTest):

    @patch("wp1.maintenance._restart_upload_workers")
    @patch("wp1.maintenance.queues.enqueue_all_projects")
    @patch("wp1.maintenance.wp10_connect")
    @patch("wp1.maintenance.redis_connect")
    def test_enqueue_all(
        self, mock_redis_connect, mock_wp10_connect, mock_enqueue_all, mock_restart
    ):
        mock_redis_connect.return_value = self.redis
        mock_wp10_connect.return_value = self.wp10db

        maintenance.enqueue_all()

        mock_restart.assert_called_once_with()
        mock_enqueue_all.assert_called_once_with(self.redis, self.wp10db)

    @override_settings(ENV=Environment.PRODUCTION)
    def test_enqueue_global_production(self):
        with patch("wp1.maintenance.redis_connect", return_value=self.redis):
            maintenance.enqueue_global()

        # Global table upload plus global project count.
        self.assertEqual(2, Queue("upload", connection=self.redis).count)

    @override_settings(ENV=Environment.DEVELOPMENT)
    def test_enqueue_global_development(self):
        with patch("wp1.maintenance.redis_connect", return_value=self.redis):
            maintenance.enqueue_global()

        # Only the global project count; the table upload is production-only.
        self.assertEqual(1, Queue("upload", connection=self.redis).count)

    @patch("wp1.maintenance._supervisorctl")
    @patch("wp1.maintenance.rebuild_global_articles")
    @patch("wp1.maintenance.redis_connect")
    def test_update_global_articles_stops_workers_during_rebuild(
        self, mock_redis_connect, mock_rebuild, mock_supervisorctl
    ):
        mock_redis_connect.return_value = self.redis
        events = []
        mock_supervisorctl.side_effect = lambda *args: events.append(args)
        mock_rebuild.side_effect = lambda: events.append("rebuild")

        maintenance.update_global_articles()

        self.assertEqual(
            [
                ("stop", *maintenance.UPDATE_WORKER_GROUPS),
                "rebuild",
                ("start", *maintenance.UPDATE_WORKER_GROUPS),
            ],
            events,
        )

    @patch("wp1.maintenance._supervisorctl")
    @patch("wp1.maintenance.rebuild_global_articles")
    @patch("wp1.maintenance.redis_connect")
    def test_update_global_articles_restarts_workers_after_failure(
        self, mock_redis_connect, mock_rebuild, mock_supervisorctl
    ):
        mock_redis_connect.return_value = self.redis
        mock_rebuild.side_effect = RuntimeError("rebuild blew up")

        with self.assertRaises(RuntimeError):
            maintenance.update_global_articles()

        mock_supervisorctl.assert_has_calls(
            [call("start", *maintenance.UPDATE_WORKER_GROUPS)]
        )

    @patch("wp1.maintenance._supervisorctl")
    @patch("wp1.maintenance.rebuild_global_articles")
    @patch("wp1.maintenance.redis_connect")
    def test_update_global_articles_aborts_if_workers_cannot_be_stopped(
        self, mock_redis_connect, mock_rebuild, mock_supervisorctl
    ):
        mock_redis_connect.return_value = self.redis
        mock_supervisorctl.side_effect = OSError("no supervisord")

        with self.assertRaises(OSError):
            maintenance.update_global_articles()

        mock_rebuild.assert_not_called()

    @patch("wp1.maintenance.send_stop_job_command")
    @patch("wp1.maintenance._supervisorctl")
    @patch("wp1.maintenance.rebuild_global_articles")
    @patch("wp1.maintenance.redis_connect")
    def test_update_global_articles_stops_inflight_jobs(
        self, mock_redis_connect, mock_rebuild, mock_supervisorctl, mock_send_stop
    ):
        mock_redis_connect.return_value = self.redis
        registry = StartedJobRegistry(queue=Queue("update", connection=self.redis))
        self.redis.zadd(registry.key, {"in-flight-job:execution": time.time() + 3600})

        maintenance.update_global_articles()

        mock_send_stop.assert_called_once_with(self.redis, "in-flight-job")
        mock_rebuild.assert_called_once_with()

    @patch("wp1.maintenance.send_stop_job_command")
    @patch("wp1.maintenance._supervisorctl")
    @patch("wp1.maintenance.rebuild_global_articles")
    @patch("wp1.maintenance.redis_connect")
    def test_update_global_articles_survives_stop_command_failure(
        self, mock_redis_connect, mock_rebuild, mock_supervisorctl, mock_send_stop
    ):
        mock_redis_connect.return_value = self.redis
        registry = StartedJobRegistry(queue=Queue("update", connection=self.redis))
        self.redis.zadd(registry.key, {"finished-job:execution": time.time() + 3600})
        # The job finished between listing and stopping; the rebuild proceeds
        # because the worker processes get stopped regardless.
        mock_send_stop.side_effect = Exception("job not currently executing")

        maintenance.update_global_articles()

        mock_rebuild.assert_called_once_with()
