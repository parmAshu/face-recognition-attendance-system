import app

APP = app.create_app()

if __name__ == "__main__":
    APP.run( "localhost", 5000, debug=True )