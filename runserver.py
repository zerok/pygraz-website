import pygraz_website

app = pygraz_website.create_app('FLASK_SETTINGS')
pygraz_website.load_db(app)
app.run()
