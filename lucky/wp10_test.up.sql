CREATE TABLE `lucky_ratings` (
  `r_project` varbinary(63) NOT NULL,
  `r_namespace` int(10) unsigned NOT NULL,
  `r_article` varbinary(255) NOT NULL,
  `r_quality` varbinary(63) DEFAULT NULL,
  `r_quality_timestamp` binary(20) DEFAULT NULL,
  `r_importance` varbinary(63) DEFAULT NULL,
  `r_importance_timestamp` binary(20) DEFAULT NULL,
  `r_score` int(8) unsigned  NOT NULL DEFAULT '0',
  PRIMARY KEY (`r_project`,`r_namespace`,`r_article`)
);

CREATE TABLE `lucky_logging` (
  `l_project` varbinary(63) NOT NULL,
  `l_namespace` int(10) unsigned NOT NULL,
  `l_article` varbinary(255) NOT NULL,
  `l_action` varbinary(20) NOT NULL,
  `l_timestamp` binary(14) NOT NULL,
  `l_old` varbinary(63) DEFAULT NULL,
  `l_new` varbinary(63) DEFAULT NULL,
  `l_revision_timestamp` binary(20) NOT NULL,
  PRIMARY KEY (`l_project`,`l_namespace`,`l_article`,`l_action`,`l_timestamp`)
);

CREATE TABLE `lucky_categories` (
  `c_project` varbinary(63) NOT NULL,
  `c_type` varbinary(16) NOT NULL,
  `c_rating` varbinary(63) NOT NULL,
  `c_replacement` varbinary(63) NOT NULL,
  `c_category` varbinary(255) NOT NULL,
  `c_ranking` int(10) unsigned NOT NULL,
  PRIMARY KEY (`c_project`,`c_type`,`c_rating`)
);

CREATE TABLE `lucky_moves` (
  `m_timestamp` binary(20) NOT NULL DEFAULT '\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',
  `m_old_namespace` int(10) unsigned NOT NULL,
  `m_old_article` varbinary(255) NOT NULL,
  `m_new_namespace` int(10) unsigned NOT NULL,
  `m_new_article` varbinary(255) NOT NULL,
  PRIMARY KEY (`m_old_namespace`,`m_old_article`,`m_timestamp`)
);

CREATE TABLE `namespacename` (
  `dbname` varbinary(32) NOT NULL,
  `domain` varbinary(48) NOT NULL,
  `ns_id` int(8) NOT NULL,
  `ns_name` varbinary(255) NOT NULL,
  `ns_type` enum('primary','canonical','alias') NOT NULL,
  `ns_is_favorite` int(1) DEFAULT '0',
  PRIMARY KEY (`domain`,`ns_name`,`ns_type`)
);

INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org', -2, 'Media'                 , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org', -1, 'Special'               , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',  0, ''                      , 'primary' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',  1, 'Talk'                  , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',  2, 'User'                  , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',  3, 'User talk'             , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',  4, 'Wikipedia'             , 'primary' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',  4, 'Project'               , 'canonical' , 0);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',  4, 'WP'                    , 'alias' , 0);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',  5, 'Wikipedia talk'        , 'primary' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',  5, 'Project talk'          , 'canonical' , 0);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',  5, 'WT'                    , 'alias' , 0);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',  6, 'File'                  , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',  6, 'Image'                 , 'alias' , 0);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',  7, 'File talk'             , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',  7, 'Image talk'            , 'alias' , 0);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',  8, 'MediaWiki'             , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',  9, 'MediaWiki talk'        , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org', 10, 'Template'              , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org', 11, 'Template talk'         , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org', 12, 'Help'                  , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org', 13, 'Help talk'             , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org', 14, 'Category'              , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org', 15, 'Category talk'         , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',100, 'Portal'                , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',101, 'Portal talk'           , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',108, 'Book'                  , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',109, 'Book talk'             , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',118, 'Draft'                 , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',119, 'Draft talk'            , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',446, 'Education Program'     , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',447, 'Education Program talk', 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',710, 'TimedText'             , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',711, 'TimedText talk'        , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',828, 'Module'                , 'canonical' , 1);
INSERT INTO `namespacename` (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite) VALUES ('enwiki_p', 'en.wikipedia.org',829, 'Module talk'           , 'canonical' , 1);

