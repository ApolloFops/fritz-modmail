import sqlite3

from .config import DATABASE_PATH


class ModmailQueries:
	create_config_table = """
CREATE TABLE IF NOT EXISTS modmail_config (
	guild_id TEXT PRIMARY KEY,
	channel_id TEXT NOT NULL
)
"""

	upsert_channel = """
INSERT INTO modmail_config (guild_id, channel_id)
VALUES (?, ?)
ON CONFLICT(guild_id)
DO UPDATE SET channel_id = excluded.channel_id;
"""

	get_channel = """
SELECT channel_id
FROM modmail_config
WHERE guild_id = ?;
"""

	remove_channel = """
DELETE FROM modmail_config
WHERE guild_id = ?;
"""


class ModmailDatabase:
	def __init__(self):
		with self.connect_db() as db:
			db.cursor().execute(ModmailQueries.create_config_table)
			db.commit()

	def connect_db(self):
		return sqlite3.connect(DATABASE_PATH)

	def set_channel(self, guild_id, channel_id):
		with self.connect_db() as db:
			db.cursor().execute(
				ModmailQueries.upsert_channel,
				(str(guild_id), str(channel_id))
			)
			db.commit()

	def get_channel(self, guild_id):
		with self.connect_db() as db:
			result = db.cursor().execute(
				ModmailQueries.get_channel,
				(str(guild_id),)
			).fetchone()

		return result[0] if result else None

	def remove_channel(self, guild_id):
		with self.connect_db() as db:
			db.cursor().execute(
				ModmailQueries.remove_channel,
				(str(guild_id),)
			)
			db.commit()
