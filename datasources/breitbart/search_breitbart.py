"""
Breitbart Search via Sphinx
"""
from datasources.fourchan.search_4chan import Search4Chan


class SearchBreitbart(Search4Chan):
	"""
	Search Breitbart corpus

	Defines methods that are used to query the Breitbart data indexed and saved.

	Apart from the prefixes, this works identically to the 4chan searcher, so
	most methods are inherited from there.
	"""
	type = "breitbart-search"
	sphinx_index = "breitbart"
	prefix = "breitbart"

	# Columns to return in csv
	return_cols = ["id", "thread_id", "reply_to", "author", "timestamp", "body", "likes", "dislikes", "subject"]

	def after_search(self, posts):
		"""
		Post-process search results

		Breitbart has some thread-level metadata that is useful to add to the
		result, so this method fetches metadata for all full articles in the
		dataset and adds it to those rows.

		:param list posts:  Posts found for the query
		:return list:  Posts with thread-level metadata added
		"""
		processed_posts = []

		thread_ids = set()
		for post in posts:
			if post["thread_id"] == post["id"] and post["subject"]:
				thread_ids.add(post["thread_id"])

		self.dataset.update_status("Fetching thread metadata for %i threads..." % len(thread_ids))
		thread_metadata = {row["id"]: {"url": row["url"], "section": row["section"], "tags": row["tags"]} for row in
						   self.db.fetchall("SELECT id, url, section, tags FROM threads_breitbart WHERE id IN %s",
											tuple(thread_ids))}

		self.dataset.update_status("Adding metadata to %i articles..." % len(thread_ids))
		while posts:
			post = posts.pop(0)
			if post["subject"] and post["thread_id"] in thread_ids:
				post = {**post, **thread_metadata[post["thread_id"]]}
			else:
				post = {**post, **{"url": "", "section": "", "tags": ""}}

			processed_posts.append(post)

		return processed_posts