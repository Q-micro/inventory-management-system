from flaskwebgui import FlaskUI
from app import app


if __name__ == "__main__":
    FlaskUI(
        app=app,
        server="flask",
        width=1280,
        height=850
    ).run()