DROP TABLE if exists readings;

CREATE TABLE readings (
					id integer primary key,
					created text not null,
					temperature real not null,
					humidity real not null
				);
CREATE INDEX readings_index on readings(created);
