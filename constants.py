DROP_VOCAB_TABLE = 'drop table if exists temp_vocab'

CREATE_VOCAB_TABLE = """
CREATE TABLE temp_vocab (
  id int(10) unsigned NOT NULL,
  name varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (id),
  KEY name (name),
  KEY idName (id, name)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 COLLATE=utf8_unicode_ci;
"""

INSERT_VOCAB_ROW = 'insert into temp_vocab (id, name) values (%s, %s)'

LOAD_VOCAB = """
LOAD DATA LOCAL INFILE %s INTO TABLE temp_vocab
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\r\n';
"""

SELECT_USER_QUERIES = """
select sl.phrase from user_has_search_log uhl, search_log sl
where uhl.userId = %s and uhl.searchLogId = sl.id
order by uhl.id desc limit %s
"""

VECTOR_LIMIT = 100