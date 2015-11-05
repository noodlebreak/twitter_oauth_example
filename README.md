This is a simple demo app.
Twitter tweet lister, using OAuth authentication.

Currently not very generic, so can't really be used
for any other OAuth provider.

* Installation:
	* Make a Python 3 based virtualenv:
		> mkvirtualenv -p /path/to/python3 tweet_lister
	* Install Python dependencies:
		> pip install -r requirements/demo.txt

* Create a twitter app, and then
  export your app's consumer key and consumer secret
  as `API_KEY` and `API_SECRET` respectively, in your
  shell environment.:
  > export API_KEY=your_app_api_key
  > export API_SECRET=your_app_api_secret

* Run the app:
	> python app.py

NOT included:
	* a basic nginx conf to serve on port 80
	* supervisor conf for gunicorn, etc
	* pagination of tweets - you'll only see the most recent 10

