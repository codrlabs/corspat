CREATE TABLE "users" (
  "id" SERIAL PRIMARY KEY,
  "email" varchar,
  "hash" varchar,
  "first_name" varchar,
  "last_name" varchar,
  "is_checked" bit,
  "created_at" timestamp
);

CREATE TABLE "path" (
  "user_id" int,
  "course_uuid" varchar,
  "course_domain" varchar,
  "course_url" varchar,
  "course_title" varchar,
  "course_desc" varchar,
  "course_img" varchar,
  "finished" bit,
  "created_at" timestamp
);

CREATE TABLE "timetracker" (
  "user_id" int,
  "course_uuid" varchar,
  "course_domain" varchar,
  "course_title" varchar,
  "started_at" timestamp,
  "finished_at" timestamp,
  "duration" timestamp,
  "track_uuid" varchar
);

CREATE TABLE "alerts" (
  "alert_id" SERIAL PRIMARY KEY,
  "alert_msg" varchar,
  "alert_urgency" int,
  "alert_link" varchar,
  "created_at" timestamp
);

ALTER TABLE "path" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "timetracker" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");
