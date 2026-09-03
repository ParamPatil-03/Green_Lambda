import os
import sys
import unittest
import json

# Add backend to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))

from app import app, DEMO_MODE_KEY

class SecurityTestSuite(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_endpoint(self):
        res = self.client.get('/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'healthy')

    def test_security_headers_present(self):
        res = self.client.get('/scatter-data')
        self.assertIn('X-Content-Type-Options', res.headers)
        self.assertEqual(res.headers['X-Content-Type-Options'], 'nosniff')
        self.assertIn('X-Frame-Options', res.headers)
        self.assertEqual(res.headers['X-Frame-Options'], 'DENY')
        self.assertIn('X-XSS-Protection', res.headers)
        self.assertIn('Cache-Control', res.headers)

    def test_connect_aws_missing_fields(self):
        res = self.client.post('/connect-aws', json={"accessKeyId": "foo"})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'error')
        self.assertIn('Missing required fields', data.get('message', ''))

    def test_connect_aws_malformed_json(self):
        res = self.client.post('/connect-aws', data="not json", content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_connect_aws_non_json_content_type(self):
        res = self.client.post('/connect-aws', data="accessKeyId=foo", content_type="application/x-www-form-urlencoded")
        self.assertEqual(res.status_code, 400)

    def test_connect_aws_demo_mode(self):
        res = self.client.post('/connect-aws', json={
            "accessKeyId": DEMO_MODE_KEY,
            "secretAccessKey": "demo-secret",
            "region": "ap-south-1"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("functions", data)
        self.assertTrue(len(data["functions"]) > 0)

    def test_analyze_function_missing_name(self):
        res = self.client.post('/analyze-function', json={"baselineRph": 5000})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'error')

    def test_analyze_function_valid_and_invalid_types(self):
        # Valid call with invalid baselineRph string to test safe_float conversion
        res = self.client.post('/analyze-function', json={
            "functionName": "bubble-sort",
            "baselineRph": "invalid_number_string",
            "model": "xgboost"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("energyWhPerInvocation", data)
        self.assertIn("monthlyCarbonKg", data)

    def test_predict_spike_validation(self):
        # Missing functionName
        res = self.client.post('/predict-spike', json={"multiplier": 10})
        self.assertEqual(res.status_code, 400)

        # Valid call with malicious multiplier injection / bad types
        res = self.client.post('/predict-spike', json={
            "functionName": "fibonacci",
            "multiplier": "invalid",
            "durationHours": "invalid"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("totals", data)
        self.assertIn("hourly", data)

    def test_error_response_hides_traceback(self):
        # Non-existent function with invalid model
        res = self.client.post('/analyze-function', json={
            "functionName": "non_existent_fn_with_forbidden_chars_<script>",
            "model": "xgboost"
        })
        # Should be caught cleanly and sanitized without exposing internal Python stack trace
        self.assertNotIn("Traceback (most recent call last)", res.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
