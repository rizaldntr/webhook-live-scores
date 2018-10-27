class Config(object):
	"""
	Configuration base, for all environments.
	"""
	CURRENT_URL = "https://world-cup-json.herokuapp.com/matches/current"
    LIVE_BLOG_URL = "https://livebloggingdistributionapi.fifa.com/api/v1/blogs/{}/events?since={}Z"
    LIST_ALL_BLOGS_URL = "https://livebloggingdistributionapi.fifa.com/api/v1/FIFA%20FORGE/en-GB/blogs?tag.IdSeason=254645&$limit=64"
    AUTH_KEY = "LiveBlogging key=1FBA2B07-6619-4BF3-9DE7-F93FFBDE076C"
	WEBHOOK_URL = "https://wc-flask.herokuapp.com/webhook"

class ProductionConfig(Config):
	ENV = "production"

class DevelopmentConfig(Config):
	ENV = "development"