"""Entry point to Zoyra."""
import gunicorn.app.base
from flask import Flask, redirect

from zorya.client.blueprints.api import api


app = Flask(
    __name__,
    static_folder="static",
    static_url_path="",
)
app.register_blueprint(api)


@app.route("/index.html")
def index():
    """
    Redirect index.html
    """
    return redirect("/")


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return app.send_static_file("index.html")


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    application = app

    def __init__(self, options=None):
        self.options = options or {}
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict(
            [
                (key, value)
                for key, value in self.options.items()
                if key in self.cfg.settings and value is not None
            ]
        )
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="8080")
