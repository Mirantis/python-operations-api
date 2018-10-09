import os

import tempfile

from operations_api.app import create_app


class FlaskBase:

    def setup(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app = self.app.test_client()


class FlaskTestDBCase(FlaskBase):
    def setup(self):
        self.db_fd, self.app.config['DATABASE'] = tempfile.mkstemp()
        self.app.init_db()

    def teardown(self):
        os.close(self.db_fd)
        os.unlink(self.app.config['DATABASE'])
