CREATE TABLE `automatedselection` (
  `as_article` varbinary(255) NOT NULL,
  `as_revid` int(8) unsigned DEFAULT NULL,
  PRIMARY KEY (`as_article`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `categories` (
  `c_project` varbinary(63) NOT NULL,
  `c_type` varbinary(16) NOT NULL,
  `c_rating` varbinary(63) NOT NULL,
  `c_replacement` varbinary(63) NOT NULL,
  `c_category` varbinary(255) NOT NULL,
  `c_ranking` int(10) unsigned NOT NULL,
  PRIMARY KEY (`c_project`,`c_type`,`c_rating`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `global_articles` (
  `a_article` varbinary(255) NOT NULL,
  `a_quality` varbinary(63) NOT NULL,
  `a_importance` varbinary(63) NOT NULL,
  `a_score` int(8) unsigned NOT NULL,
  PRIMARY KEY (`a_article`),
  KEY `score` (`a_score`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `global_rankings` (
  `gr_type` varbinary(16) NOT NULL,
  `gr_rating` varbinary(63) NOT NULL,
  `gr_ranking` int(10) unsigned NOT NULL,
  PRIMARY KEY (`gr_type`,`gr_rating`),
  KEY `gr_type` (`gr_type`,`gr_ranking`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `logging` (
  `l_project` varbinary(63) NOT NULL,
  `l_namespace` int(10) unsigned NOT NULL,
  `l_article` varbinary(255) NOT NULL,
  `l_action` varbinary(20) NOT NULL,
  `l_timestamp` binary(14) NOT NULL,
  `l_old` varbinary(63) DEFAULT NULL,
  `l_new` varbinary(63) DEFAULT NULL,
  `l_revision_timestamp` binary(20) NOT NULL,
  PRIMARY KEY (`l_project`,`l_namespace`,`l_article`,`l_action`,`l_timestamp`),
  KEY `l_article` (`l_article`,`l_namespace`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `moves` (
  `m_timestamp` binary(20) NOT NULL DEFAULT '\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',
  `m_old_namespace` int(10) unsigned NOT NULL,
  `m_old_article` varbinary(255) NOT NULL,
  `m_new_namespace` int(10) unsigned NOT NULL,
  `m_new_article` varbinary(255) NOT NULL,
  PRIMARY KEY (`m_old_namespace`,`m_old_article`,`m_timestamp`),
  KEY `m_new_namespace` (`m_new_namespace`,`m_new_article`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `namespacename` (
  `dbname` varbinary(32) NOT NULL,
  `domain` varbinary(48) NOT NULL,
  `ns_id` int(8) NOT NULL,
  `ns_name` varbinary(255) NOT NULL,
  `ns_type` enum('primary','canonical','alias') NOT NULL,
  `ns_is_favorite` int(1) DEFAULT '0',
  PRIMARY KEY (`domain`,`ns_name`,`ns_type`),
  KEY `domain` (`domain`,`ns_id`,`ns_type`),
  KEY `dbname` (`dbname`,`ns_id`,`ns_type`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `ratings` (
  `r_project` varbinary(63) NOT NULL,
  `r_namespace` int(10) unsigned NOT NULL,
  `r_article` varbinary(255) NOT NULL,
  `r_quality` varbinary(63) DEFAULT NULL,
  `r_quality_timestamp` binary(20) DEFAULT NULL,
  `r_importance` varbinary(63) DEFAULT NULL,
  `r_importance_timestamp` binary(20) DEFAULT NULL,
  `r_score` int(8) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`r_project`,`r_namespace`,`r_article`),
  KEY `nstitle` (`r_namespace`,`r_article`(50))
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `selection_data` (
  `sd_article` varbinary(255) NOT NULL,
  `sd_langlinks` int(10) unsigned NOT NULL DEFAULT '0',
  `sd_pagelinks` int(10) unsigned NOT NULL DEFAULT '0',
  `sd_hitcount` int(10) unsigned NOT NULL DEFAULT '0',
  `sd_external` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`sd_article`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `workingselection` (
  `ws_article` varbinary(255) NOT NULL,
  `ws_revid` int(8) unsigned DEFAULT NULL,
  PRIMARY KEY (`ws_article`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- The following tables are used by various part of the previous version of this
-- tool, which was written in Perl. The current code in this repository neither
-- reads from nor updates these tables. They are kept here for archival reasons.

/**
--- Only used by old Perl bot.
CREATE TABLE `cache` (
  `c_key` varchar(255) COLLATE utf8_bin NOT NULL,
  `c_expiry` binary(12) NOT NULL,
  `c_content` blob,
  PRIMARY KEY (`c_key`),
  KEY `c_expiry` (`c_expiry`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- Only used by old Perl bot.
CREATE TABLE `manualselection` (
  `ms_article` varbinary(255) NOT NULL,
  `ms_type` enum('release','norelease') NOT NULL,
  `ms_timestamp` binary(14) NOT NULL,
  `ms_revid` int(8) unsigned DEFAULT NULL,
  PRIMARY KEY (`ms_article`),
  KEY `ms_type` (`ms_type`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Only used by old Perl bot.
CREATE TABLE `manualselectionlog` (
  `msl_article` varbinary(255) NOT NULL,
  `msl_type` enum('release','norelease') NOT NULL,
  `msl_timestamp` binary(14) NOT NULL,
  `msl_action` varbinary(16) NOT NULL,
  `msl_user` varbinary(255) NOT NULL,
  `msl_reason` varbinary(255) NOT NULL,
  PRIMARY KEY (`msl_article`,`msl_timestamp`),
  KEY `msl_user` (`msl_user`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Only used by old Perl bot.
DROP TABLE IF EXISTS `passwd`;
CREATE TABLE `passwd` (
  `pw_user` varchar(255) COLLATE utf8_bin NOT NULL,
  `pw_password` binary(32) NOT NULL,
  PRIMARY KEY (`pw_user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- Only used by old Perl bot.
DROP TABLE IF EXISTS `releases`;
CREATE TABLE `releases` (
  `rel_article` varbinary(255) NOT NULL,
  `rel_0p5_category` varbinary(63) NOT NULL,
  `rel_0p5_timestamp` binary(20) DEFAULT NULL,
  PRIMARY KEY (`rel_article`),
  KEY `rel_0p5_category` (`rel_0p5_category`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Only used by old Perl bot.
CREATE TABLE `reviews` (
  `rev_value` varbinary(10) NOT NULL,
  `rev_article` varbinary(255) NOT NULL,
  `rev_timestamp` binary(20) DEFAULT NULL,
  PRIMARY KEY (`rev_article`),
  KEY `rev_value` (`rev_value`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

**/
