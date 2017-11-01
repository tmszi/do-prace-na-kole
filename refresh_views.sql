
drop table  dpnk_gpxfile_anonymized;
CREATE TABLE dpnk_gpxfile_anonymized as select * from (select a.id, a.campaign_id, ST_LineSubstring(a.track, 100/st_length(a.track::geography), 1 - 100/st_length(a.track::geography)) as the_geom from (SELECT dpnk_gpxfile.id, dpnk_userattendance.campaign_id, (ST_Dump(dpnk_gpxfile.track::geometry)).geom AS track from dpnk_gpxfile join dpnk_userattendance on (dpnk_gpxfile.user_attendance_id = dpnk_userattendance.id)) as a where a.track is not null and st_numpoints(a.track::geometry) > 15 and st_length(a.track::geography)<100000 and st_length(a.track::geography)>200) as b where st_numpoints(b.the_geom)>15;
GRANT ALL PRIVILEGES ON TABLE dpnk_gpxfile_anonymized TO dpnk;
CREATE INDEX dpnk_gpxfile_anonymized_idx ON dpnk_gpxfile_anonymized USING GIST (the_geom);

drop table dpnk_track_anonymized;
create table dpnk_track_anonymized as select * from (select id, campaign_id, st_numpoints((st_dump(track::geometry)).geom) as numpoints, ST_LineSubstring(track::geometry, 100/st_length(track), 1 - 100/st_length(track)) as the_geom from dpnk_userattendance where track is not null and st_length(track)<100000 and st_length(track)>200) as a where numpoints>15;
GRANT ALL PRIVILEGES ON TABLE dpnk_track_anonymized TO dpnk;
CREATE INDEX dpnk_track_anonymized_idx ON dpnk_track_anonymized USING GIST (the_geom);
