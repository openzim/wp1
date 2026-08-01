import time
from unittest.mock import patch

from rq import Queue
from rq.registry import StartedJobRegistry
from rq.suspension import is_suspended

from wp1 import maintenance
from wp1.base_db_test import BaseWpOneDbTest
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

    @patch("wp1.maintenance.ENV", Environment.PRODUCTION)
    def test_enqueue_global_production(self):
        with patch("wp1.maintenance.redis_connect", return_value=self.redis):
            maintenance.enqueue_global()

        # Global table upload plus global project count.
        self.assertEqual(2, Queue("upload", connection=self.redis).count)

    @patch("wp1.maintenance.ENV", Environment.DEVELOPMENT)
    def test_enqueue_global_development(self):
        with patch("wp1.maintenance.redis_connect", return_value=self.redis):
            maintenance.enqueue_global()

        # Only the global project count; the table upload is production-only.
        self.assertEqual(1, Queue("upload", connection=self.redis).count)

    @patch("wp1.maintenance.rebuild_global_articles")
    @patch("wp1.maintenance.redis_connect")
    def test_update_global_articles_suspends_workers_during_rebuild(
        self, mock_redis_connect, mock_rebuild
    ):
        mock_redis_connect.return_value = self.redis
        suspended_during_rebuild = []
        mock_rebuild.side_effect = lambda: suspended_during_rebuild.append(
            is_suspended(self.redis)
        )

        maintenance.update_global_articles()

        self.assertEqual([True], suspended_during_rebuild)
        self.assertFalse(is_suspended(self.redis))

    @patch("wp1.maintenance.rebuild_global_articles")
    @patch("wp1.maintenance.redis_connect")
    def test_update_global_articles_resumes_after_failure(
        self, mock_redis_connect, mock_rebuild
    ):
        mock_redis_connect.return_value = self.redis
        mock_rebuild.side_effect = RuntimeError("rebuild blew up")

        with self.assertRaises(RuntimeError):
            maintenance.update_global_articles()

        self.assertFalse(is_suspended(self.redis))

    @patch("wp1.maintenance.rebuild_global_articles")
    @patch("wp1.maintenance.redis_connect")
    def test_update_global_articles_times_out_when_update_jobs_stuck(
        self, mock_redis_connect, mock_rebuild
    ):
        mock_redis_connect.return_value = self.redis
        # Simulate an in-flight update job that never finishes.
        registry = StartedJobRegistry(queue=Queue("update", connection=self.redis))
        self.redis.zadd(registry.key, {"in-flight-job:execution": time.time() + 3600})

        with (
            patch.object(maintenance, "DRAIN_POLL_SECONDS", 0.01),
            patch.object(maintenance, "DRAIN_TIMEOUT_SECONDS", 0.05),
        ):
            with self.assertRaises(TimeoutError):
                maintenance.update_global_articles()

        mock_rebuild.assert_not_called()
        self.assertFalse(is_suspended(self.redis))

    @patch("wp1.maintenance.rebuild_global_articles")
    @patch("wp1.maintenance.redis_connect")
    def test_update_global_articles_proceeds_once_update_jobs_finish(
        self, mock_redis_connect, mock_rebuild
    ):
        mock_redis_connect.return_value = self.redis
        # An in-flight job whose registry entry has already expired is cleaned
        # up by the drain check rather than blocking it.
        registry = StartedJobRegistry(queue=Queue("update", connection=self.redis))
        self.redis.zadd(registry.key, {"finished-job:execution": time.time() - 10})

        maintenance.update_global_articles()

        mock_rebuild.assert_called_once_with()
        self.assertFalse(is_suspended(self.redis))
