"""
Test cases for error handlers y log handlers para aumentar cobertura
"""
import unittest
from flask import Flask
from service.common import error_handlers, log_handlers

class TestErrorHandlers(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    def test_bad_request_handler(self):
        with self.app.test_request_context():
            resp = error_handlers.bad_request('bad')
            self.assertEqual(resp[1], 400)
            self.assertIn('Bad Request', resp[0].json['error'])

    def test_not_found_handler(self):
        with self.app.test_request_context():
            resp = error_handlers.not_found('not found')
            self.assertEqual(resp[1], 404)
            self.assertIn('Not Found', resp[0].json['error'])

    def test_method_not_supported_handler(self):
        with self.app.test_request_context():
            resp = error_handlers.method_not_supported('no method')
            self.assertEqual(resp[1], 405)
            self.assertIn('Method not Allowed', resp[0].json['error'])

    def test_mediatype_not_supported_handler(self):
        with self.app.test_request_context():
            resp = error_handlers.mediatype_not_supported('no media')
            self.assertEqual(resp[1], 415)
            self.assertIn('Unsupported media type', resp[0].json['error'])

    def test_internal_server_error_handler(self):
        with self.app.test_request_context():
            resp = error_handlers.internal_server_error(Exception('fail'))
            self.assertEqual(resp[1], 500)
            self.assertIn('Internal Server Error', resp[0].json['error'])

class TestLogHandlers(unittest.TestCase):
    def test_init_logging(self):
        app = Flask(__name__)
        # Llama a init_logging con un logger existente
        log_handlers.init_logging(app, 'werkzeug')
        app.logger.info('test log')

if __name__ == "__main__":
    unittest.main()
