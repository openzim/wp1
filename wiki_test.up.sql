CREATE TABLE `page` (
  `page_id` int(8) unsigned NOT NULL,
  `page_namespace` int(11) NOT NULL,
  `page_title` varbinary(255) NOT NULL,
  `page_touched` varbinary(14) NOT NULL DEFAULT ''
);

CREATE TABLE `categorylinks` (
  `cl_from` int(8) unsigned NOT NULL DEFAULT 0,
  `cl_to` varbinary(255) NOT NULL DEFAULT '',
  `cl_sortkey` varbinary(230) NOT NULL DEFAULT '',
  `cl_timestamp` timestamp
);

CREATE TABLE `redirect` (
  `rd_from` int(8) unsigned NOT NULL DEFAULT 0,
  `rd_namespace` int(11) NOT NULL DEFAULT 0,
  `rd_title` varbinary(255) NOT NULL DEFAULT '',
  `rd_interwiki` varbinarY(32) DEFAULT NULL,
  `rd_fragment` varbinary(255) DEFAULT NULL
);

CREATE TABLE `revision` (
  `rev_id` int(8) unsigned NOT NULL DEFAULT 0,
  `rev_page` int(8) unsigned NOT NULL DEFAULT 0,
  `rev_text_id` bigint(10) unsigned DEFAULT NULL,
  `rev_comment_id` decimal(20,0) DEFAULT NULL,
  `rev_actor` decimal(20,0) DEFAULT NULL,
  `rev_timestamp` varbinary(14) NOT NULL DEFAULT '',
  `rev_minor_edit` tinyint(1) unsigned NOT NULL DEFAULT 0,
  `rev_deleted` tinyint(1) unsigned NOT NULL DEFAULT 0,
  `rev_len` int(8) unsigned DEFAULT NULL,
  `rev_parent_id` int(8) unsigned DEFAULT NULL,
  `rev_sha1` varbinary(32) DEFAULT NULL,
  `rev_content_model`  varbinary(32) DEFAULT NULL,
  `rev_content_format` varbinary(64) DEFAULT NULL
);
