CREATE TABLE `ratings` (
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

CREATE TABLE `categories` (
  `c_project` varbinary(63) NOT NULL,
  `c_type` varbinary(16) NOT NULL,
  `c_rating` varbinary(63) NOT NULL,
  `c_replacement` varbinary(63) NOT NULL,
  `c_category` varbinary(255) NOT NULL,
  `c_ranking` int(10) unsigned NOT NULL,
  PRIMARY KEY (`c_project`,`c_type`,`c_rating`)
);

CREATE TABLE `moves` (
  `m_timestamp` binary(20) NOT NULL DEFAULT '\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',
  `m_old_namespace` int(10) unsigned NOT NULL,
  `m_old_article` varbinary(255) NOT NULL,
  `m_new_namespace` int(10) unsigned NOT NULL,
  `m_new_article` varbinary(255) NOT NULL,
  PRIMARY KEY (`m_old_namespace`,`m_old_article`,`m_timestamp`)
);

CREATE TABLE `projects` (
  `p_project` varbinary(63) NOT NULL,
  `p_timestamp` binary(14) NOT NULL,
  `p_wikipage` varbinary(255) DEFAULT NULL,
  `p_parent` varbinary(63) DEFAULT NULL,
  `p_shortname` varbinary(255) DEFAULT NULL,
  `p_count` int(10) unsigned DEFAULT '0',
  `p_qcount` int(10) unsigned DEFAULT '0',
  `p_icount` int(10) unsigned DEFAULT '0',
  `p_scope` int(10) unsigned NOT NULL DEFAULT '0',
  `p_upload_timestamp` binary(14) DEFAULT NULL,
  PRIMARY KEY (`p_project`)
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

CREATE TABLE `releases` (
  `rel_article` varbinary(255) NOT NULL,
  `rel_0p5_category` varbinary(63) NOT NULL,
  `rel_0p5_timestamp` binary(20) DEFAULT NULL,
  PRIMARY KEY (`rel_article`)
);

CREATE TABLE `global_articles` (
  `a_article` varbinary(255) NOT NULL,
  `a_quality` varbinary(63) NOT NULL,
  `a_importance` varbinary(63) NOT NULL,
  `a_score` int(8) unsigned NOT NULL,
  PRIMARY KEY (`a_article`)
);

CREATE TABLE `global_rankings` (
  `gr_type` varbinary(16) NOT NULL,
  `gr_rating` varbinary(63) NOT NULL,
  `gr_ranking` int(10) unsigned NOT NULL,
  PRIMARY KEY (`gr_type`,`gr_rating`)
);

CREATE TABLE `users` (
  `u_id` VARCHAR(255) NOT NULL,
  `u_username` varchar(255) DEFAULT NULL
);

CREATE TABLE `builders` (
  b_id VARBINARY(255) NOT NULL PRIMARY KEY,
  b_name VARBINARY(255) NOT NULL,
  b_user_id VARCHAR(255) NOT NULL,
  b_project VARBINARY(255) NOT NULL,
  b_model VARBINARY(255) NOT NULL,
  b_current_version int(11) NOT NULL DEFAULT 0,
  b_params BLOB,
  b_created_at BINARY(14),
  b_updated_at BINARY(14),
  b_selection_zim_version int(11) NOT NULL DEFAULT 0
);

CREATE TABLE `selections` (
  s_id VARBINARY(255) NOT NULL PRIMARY KEY,
  s_builder_id VARBINARY(255) NOT NULL,
  s_content_type VARBINARY(255) NOT NULL,
  s_updated_at BINARY(14) NOT NULL,
  s_version int(11) NOT NULL,
  s_object_key VARBINARY(255),
  s_status VARBINARY(255) DEFAULT 'OK',
  s_error_messages BLOB,
  s_article_count int(11)
);

CREATE TABLE custom (
  c_name VARBINARY(255) NOT NULL PRIMARY KEY,
  c_module VARBINARY(255) NOT NULL,
  c_username VARBINARY(255) DEFAULT NULL,
  c_description BLOB,
  c_params MEDIUMBLOB,
  c_created_at BINARY(20),
  c_updated_at BINARY(20),
  c_is_active TINYINT
);

CREATE TABLE zim_files (
  z_id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
  z_selection_id VARBINARY(255) NOT NULL,
  z_status VARBINARY(255) DEFAULT "NOT_REQUESTED",
  z_task_id VARBINARY(255),
  z_requested_at BINARY(14),
  z_updated_at BINARY(14),
  z_long_description blob,
  z_description tinyblob
);

CREATE TABLE `temp_pageviews` (
  `tp_lang` varbinary(255) NOT NULL,
  `tp_page_id` int(11) NOT NULL,
  `tp_article` varbinary(1024) DEFAULT NULL,
  `tp_views` int(11) DEFAULT 0,
  PRIMARY KEY (`tp_lang`,`tp_page_id`),
  KEY `idx_tp_article` (tp_article)
);

CREATE TABLE `page_scores` (
  `ps_lang` varbinary(255) NOT NULL,
  `ps_page_id` int(11) NOT NULL,
  `ps_article` varbinary(1024) DEFAULT NULL,
  `ps_views` int(11) DEFAULT 0,
  `ps_links` int(11) DEFAULT 0,
  `ps_lang_links` int(11) DEFAULT 0,
  `ps_score` int(11) DEFAULT 0,
  PRIMARY KEY (`ps_lang`,`ps_page_id`),
  KEY `lang_article` (`ps_lang`,`ps_article`),
  KEY `idx_ps_article` (ps_article)
);

INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('importance', 'Unknown-Class', 0);
INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('importance', 'NA-Class', 50);
INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('importance', 'Low-Class', 100);
INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('importance', 'Mid-Class', 200);
INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('importance', 'High-Class', 300);
INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('importance', 'Top-Class', 400);
INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('quality', 'Unassessed-Class', 0);
INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('quality', 'Assessed-Class', 20);
INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('quality', 'List-Class', 80);
INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('quality', 'Stub-Class', 100);
INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('quality', 'Start-Class', 150);
INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('quality', 'C-Class', 225);
INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('quality', 'B-Class', 300);
INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('quality', 'GA-Class', 400);
INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('quality', 'A-Class', 425);
INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('quality', 'FL-Class', 480);
INSERT INTO `global_rankings` (gr_type, gr_rating, gr_ranking) VALUES ('quality', 'FA-Class', 500);

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
