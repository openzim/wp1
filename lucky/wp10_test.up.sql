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
