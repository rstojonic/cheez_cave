DROP TABLE if exists readings;

CREATE TABLE readings (
					id integer primary key,
					created text not null,
					temperature real not null,
					humidity real not null,
                    humidity_mov_avg real
				);
CREATE INDEX readings_index on readings(created);
create index readings_id_index on readings(id);

drop table if exists humidififer;

create table humidifier (
    id integer primary key,
    created text not null,
    mode text not null
);
create index humidifier_id_index on humidifier(id);
create index humidifier_created_index on humidifier(created);

