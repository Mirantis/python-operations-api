from operations_api import app as application

if __name__ == '__main__':
    """
        WGSI module to run application using Gunicorn server.
        Main module from Operations RestAPI
    """
    application.run()
