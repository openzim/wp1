CREATE TABLE `page` (
  `page_id` int(8) unsigned NOT NULL,
  `page_namespace` int(11) NOT NULL,
  `page_title` varbinary(255) NOT NULL
);

CREATE TABLE `categorylinks` (
  `cl_from` int(8) unsigned NOT NULL DEFAULT 0,
  `cl_to` varbinary(255) NOT NULL DEFAULT '',
  `cl_sortkey` varbinary(230) NOT NULL DEFAULT '',
  `cl_timestamp` timestamp
);
