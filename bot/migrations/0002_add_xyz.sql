-- 0002_add_xyz.sql
ALTER TABLE guild_settings
ADD COLUMN IF NOT EXISTS qotd_role_id BIGINT;
