-- tables.sql
-- Contains table schema for the wikipedia assessments bot
-- Part of WP 1.0 bot
-- See the files README, LICENSE, and AUTHORS for additional information

-- The project table stores a list of participating wikiprojects

create table if not exists projects ( 

    p_project         varchar(63) not null,
        -- project name

    p_timestamp       binary(14) not null,
        -- last time project data was updated

    p_wikipage        varchar(255),
        -- homepage on the wiki for this project

    p_parent          varchar(63),
        -- parent project (for task forces)

    p_shortname       varchar(255),
        -- display name in headers 

    p_count           int unsigned default 0,
        -- how many pages are assessed in project 

    p_qcount          int unsigned default 0,
        -- how many pages have quality assessments in the project

    p_icount          int unsigned default 0,
        -- how many pages have importance assessments in the project 

    p_scope    int unsigned not null default 0,
        -- the project's "scope points", used to compute selection scores
   
    primary key (p_project)

) default character set 'utf8' collate 'utf8_bin'
  engine = InnoDB;


-- The ratings table stores the ratings data. Each article will
-- be listed once per project that assessed it. 

create table if not exists ratings ( 

    r_project               varchar(63)  not null,
        -- project name

    r_namespace             int unsigned not null,
        -- article namespace

    r_article               varchar(255) not null,
        -- article title

    r_quality               varchar(63),
        -- quality rating

    r_quality_timestamp     binary(20),
        -- time when quality rating was assigned
        --   NOTE: a revid can be obtained from timestamp via API
        --  a wiki-format timestamp

    r_importance            varchar(63),
        -- importance rating

    r_importance_timestamp  binary(20),
        -- time when importance rating was assigned
        -- a wiki-style timestamp


    r_score int(8) unsigned not null default 0,
        -- the selection score for this rating of this article

    primary key (r_project, r_namespace, r_article)
) default character set 'utf8' collate 'utf8_bin'
  engine = InnoDB;


-- The categories table stores a list of all ratings 
-- assigned by a particular project

create table if not exists categories ( 

    c_project         varchar(63)  not null,
        -- project name

    c_type        varchar(16)  not null,
        -- what type of rating - 'quality' or 'importance'

    c_rating          varchar(63)  not null,
        -- name of the rating (e.g. B-Class)

    c_replacement          varchar(63)  not null,
        -- replacement name of the rating
        -- a standard replacement for nonstandard ratings
        -- e.g. for c_rating = B+-Class, set c_replacement=B-class
  
    c_category        varchar(255) not null,
        -- category used to get pages that are assigned this rating

    c_ranking           int unsigned not null,
        -- sortkey, used when creating tables 

    primary key (c_project, c_type, c_rating)
) default character set 'utf8' collate 'utf8_bin'
  engine = InnoDB;



-- The logging table has one log entry for each change of an article. 
-- Changing both quality and importance will create two log entries. 

create table if not exists logging ( 
    l_project        varchar(63)  not null,   
       -- project name

    l_namespace      int unsigned not null,
      -- article namespace

    l_article        varchar(255) not null,
       -- article name

    l_action         varchar(20) character set ascii not null,
       -- type of log entry (e.g. 'quality')

       -- NOTE: this is ASCII because of maximum index key
       -- length constraints interacting with utf-8 fields in  
       -- mysql. The primary key for this table is just under the limit. 
 
    l_timestamp      binary(14)  not null,
       -- timestamp when log entry was added

    l_old            varchar(63),
       -- old value (e.g. B-Class)

    l_new            varchar(63),
       -- new value (e.g. GA-Class)

    l_revision_timestamp  binary(20)  not null,
       -- timestamp when page was edited
       -- a wiki-format timestamp

    primary key (l_project, l_namespace, l_article, l_action, l_timestamp),
    key (l_article, l_namespace)
) default charset 'utf8' collate 'utf8_bin'
  engine = InnoDB;


-- The review table stores the data for community-wide reviews:
-- Featured and Good Articles. Each article will be included at 
-- most once, marked either GA or FA. 

-- This table implicitly has rev_namespace = 0

create table if not exists reviews ( 

    rev_value               varchar(10)  not null,
        -- whether an article is FA or GA

    rev_article             varchar(255) not null,
        -- article title

    rev_timestamp     binary(20),
        -- time when review was completed and the article was tagged 
  -- with the proper talk page banner
        --   NOTE: a revid can be obtained from timestamp via API
        --  a wiki-format timestamp

    primary key (rev_article),
    key (rev_value)

) default character set 'utf8' collate 'utf8_bin'
  engine = InnoDB;


-- The global_articles table stores the higest quality and 
-- highest importance assigned to each article. It is used to 
-- generate global statistics 

-- This table implicitly has a_namespace = 0

create table if not exists global_articles ( 

    a_article             varchar(255) not null,
        -- article title

    a_quality             varchar(63) not null,
        -- the article's highest quality rating

    a_importance          varchar(63) not null,
        -- The article's highest importance rating

    a_score           int(8) unsigned not null,
        -- The article's highest selection score

    primary key (a_article)

) default character set 'utf8' collate 'utf8_bin'
  engine = InnoDB;


-- the release table stores data about released versions
-- (currently limited to WP 0.5)

-- This table implicitly has rel_namespace = 0

create table if not exists releases ( 

    rel_article             varchar(255) not null,
        -- article title

    rel_0p5_category        varchar(63) not null,
        -- The Wikipedia 0.5 category (Arts, Language, etc.)

    rel_0p5_timestamp       binary(20),
        -- time when article was added to a 0.5 release category
        -- NOTE: a revid can be obtained from timestamp via API
        -- a wiki-format timestamp
  
    primary key (rel_article),
    key         (rel_0p5_category)

) default character set 'utf8' collate 'utf8_bin'
  engine = InnoDB;


-- the moves table keeps track of previous names of 
-- assessed articles

create table if not exists moves (
    m_timestamp      binary(20),
      -- when the move was made

    m_old_namespace      int unsigned not null,
      -- article namespace before move

    m_old_article        varchar(255) not null,
       -- article name before move

    m_new_namespace      int unsigned not null,
      -- article namespace after move

    m_new_article        varchar(255) not null,
       -- article name after move

   primary key (m_old_namespace, m_old_article, m_timestamp),
   key (m_new_namespace, m_new_article)
) default character set 'utf8' collate 'utf8_bin'
  engine = InnoDB;

-- the global_rankings table determines which
-- quality and importance ratings appear in the
-- global table
 

create table if not exists global_rankings (

    gr_type            varchar(16)  not null,
        -- what type of rating - 'quality' or 'importance'

    gr_rating          varchar(63)  not null,
        -- name of the rating (e.g. B-Class)

    gr_ranking        int unsigned  not null,
        -- integer sortkey for the rating

   primary key (gr_type,gr_rating),
   key (gr_type, gr_ranking)
) default character set 'utf8' collate 'utf8_bin'
  engine = InnoDB;

-- default contents of the global_rankings table

replace into global_rankings values 
   ('quality',    'FA-Class',       500),
   ('quality',    'FL-Class',       480), 
   ('quality',    'A-Class',        425), 
   ('quality',    'GA-Class',       400), 
   ('quality',    'B-Class',        300), 
   ('quality',    'C-Class',        225), 
   ('quality',    'Start-Class',    150),
   ('quality',    'Stub-Class',     100), 
   ('quality',    'List-Class',      80),              
   ('quality',    'Assessed-Class',  20),
   ('quality',    'Unassessed-Class' ,0),
   ('importance', 'Top-Class',      400),
   ('importance', 'High-Class',     300),                
   ('importance', 'Mid-Class',      200), 
   ('importance', 'Low-Class',      100),
   ('importance', 'NA-Class',        50),
   ('importance', 'Unknown-Class',    0);



create table if not exists selection_data (
  sd_article varchar(255) not null,

  sd_langlinks int unsigned not null default 0,
 
  sd_pagelinks int unsigned not null default 0,

  sd_hitcount int unsigned not null default 0,

  sd_external int unsigned not null default 0,

  primary key (sd_article)
) default character set 'utf8' collate 'utf8_bin'
  engine = InnoDB;


create table if not exists manualselection (
  
  ms_article varchar(255) not null,

  ms_type enum('release', 'norelease') not null,

  ms_timestamp       binary(14) not null,

  primary key(ms_article),

  key (ms_type)

) default character set 'utf8' collate 'utf8_bin'
  engine = InnoDB;


create table if not exists manualselectionlog ( 

  msl_article varchar(255) not null,

  msl_type enum('release', 'norelease') not null,

  msl_timestamp       binary(14) not null,

  msl_action varchar(16) not null,

  msl_user varchar(255) not null,

  msl_reason varchar(255) not null,

  primary key (msl_article, msl_timestamp),
  key (msl_user)

) default character set 'utf8' collate 'utf8_bin'
  engine = InnoDB;

-- Used to cache content for the web interface

create table if not exists cache ( 

  c_key varchar(255) not null,

  c_expiry binary(12) not null,

  c_content blob,

  primary key (c_key),

  key (c_expiry)

) default character set 'utf8' collate 'utf8_bin'
  engine = InnoDB;



-- Passwords for manually-maintained data

create table if not exists passwd ( 

  pw_user varchar(255) not null,

  pw_password binary(32) not null,

  primary key (pw_user)

) default character set 'utf8' collate 'utf8_bin'
  engine = InnoDB;

