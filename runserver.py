import pygraz_website
import settings

app = pygraz_website.create_app(config_object=settings)


if __name__ == '__main__':
    app.run()
