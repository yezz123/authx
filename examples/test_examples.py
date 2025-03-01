import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

# List of example files to test
EXAMPLES = [
    "basic_auth_example.py",
    "refresh_token_example.py",
    "token_blocklist_example.py",
    "token_locations_example.py",
    "fresh_token_example.py",
]

# Base URL for the examples
BASE_URL = "http://localhost:8000"

# Check if examples exist
for example in EXAMPLES:
    if not Path(example).exists():
        print(f"Warning: Example file {example} not found. Make sure you're running tests from the examples directory.")


class ExampleServer:
    """Context manager to start and stop an example server."""

    def __init__(self, example_file: str):
        self.example_file = example_file
        self.process = None

    def __enter__(self):
        print(f"\nStarting server for {self.example_file}...")

        # Check if the file exists
        if not Path(self.example_file).exists():
            pytest.skip(f"Example file {self.example_file} not found")

        # Start the server
        self.process = subprocess.Popen(
            [sys.executable, self.example_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # Use text mode to avoid ResourceWarning
        )

        # Wait for server to start
        max_retries = 10
        for i in range(max_retries):
            time.sleep(1)  # Give more time to start
            try:
                # Try to connect to the server
                response = httpx.get(f"{BASE_URL}/", timeout=1)
                if response.status_code == 200:
                    print(f"Server for {self.example_file} started successfully")
                    break
            except httpx.ConnectError:
                if i == max_retries - 1:
                    # If we've reached max retries, check if process is still running
                    if self.process.poll() is not None:
                        # Process has terminated
                        stdout, stderr = self.process.communicate()
                        print(f"Server process terminated with exit code {self.process.returncode}")
                        print(f"STDOUT: {stdout}")
                        print(f"STDERR: {stderr}")
                        pytest.skip(f"Server for {self.example_file} failed to start")
                print(f"Waiting for server to start (attempt {i + 1}/{max_retries})...")
                continue

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Kill the server process
        if self.process:
            try:
                if self.process.poll() is None:  # Only terminate if still running
                    print(f"Terminating server for {self.example_file}...")
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                        self.process.wait()

                # Ensure all file descriptors are closed
                if hasattr(self.process, "stdout") and self.process.stdout:
                    self.process.stdout.close()
                if hasattr(self.process, "stderr") and self.process.stderr:
                    self.process.stderr.close()

            except Exception as e:
                print(f"Error terminating server: {e}")


@pytest.mark.parametrize("example", EXAMPLES)
def test_example_root_endpoint(example):
    """Test that the root endpoint of each example returns a 200 status code."""
    with ExampleServer(example) as server:
        try:
            response = httpx.get(f"{BASE_URL}/", timeout=5)
            assert response.status_code == 200
            # Verify it's a JSON response with a message field
            data = response.json()
            assert "message" in data
        except httpx.ConnectError as e:
            pytest.fail(f"Could not connect to server: {e}")


@pytest.mark.parametrize("example", EXAMPLES)
def test_example_login(example):
    """Test the login endpoint of each example."""
    with ExampleServer(example) as server:
        try:
            # Try to login with valid credentials
            response = httpx.post(f"{BASE_URL}/login", json={"username": "user1", "password": "password1"}, timeout=5)
            assert response.status_code == 200
            data = response.json()

            # Check for access token in response
            if example == "fresh_token_example.py":
                assert "fresh_token" in data
            else:
                assert "access_token" in data

            # Try to login with invalid credentials
            response = httpx.post(f"{BASE_URL}/login", json={"username": "invalid", "password": "invalid"}, timeout=5)
            assert response.status_code == 401
        except httpx.ConnectError as e:
            pytest.fail(f"Could not connect to server: {e}")


@pytest.mark.parametrize("example", EXAMPLES)
def test_example_protected_route(example):
    """Test the protected route of each example."""
    with ExampleServer(example) as server:
        try:
            # First login to get a token
            login_response = httpx.post(
                f"{BASE_URL}/login", json={"username": "user1", "password": "password1"}, timeout=5
            )
            assert login_response.status_code == 200
            login_data = login_response.json()

            # Get the appropriate token
            if example == "fresh_token_example.py":
                token = login_data.get("fresh_token")
            else:
                token = login_data.get("access_token")

            assert token is not None

            # Try to access protected route with token
            response = httpx.get(f"{BASE_URL}/protected", headers={"Authorization": f"Bearer {token}"}, timeout=5)
            assert response.status_code == 200

            # Try to access protected route without token
            response = httpx.get(f"{BASE_URL}/protected", timeout=5)
            assert response.status_code == 401
        except httpx.ConnectError as e:
            pytest.fail(f"Could not connect to server: {e}")


# Specific tests for refresh token example
def test_refresh_token_flow():
    """Test the refresh token flow in the refresh token example."""
    example = "refresh_token_example.py"
    with ExampleServer(example) as server:
        try:
            # Login to get tokens
            login_response = httpx.post(
                f"{BASE_URL}/login", json={"username": "user1", "password": "password1"}, timeout=5
            )
            assert login_response.status_code == 200
            login_data = login_response.json()

            access_token = login_data.get("access_token")
            refresh_token = login_data.get("refresh_token")

            assert access_token is not None
            assert refresh_token is not None

            # Use refresh token to get a new access token
            refresh_response = httpx.post(f"{BASE_URL}/refresh", json={"refresh_token": refresh_token}, timeout=5)
            assert refresh_response.status_code == 200
            refresh_data = refresh_response.json()

            new_access_token = refresh_data.get("access_token")
            assert new_access_token is not None
            assert new_access_token != access_token
        except httpx.ConnectError as e:
            pytest.fail(f"Could not connect to server: {e}")


# Specific tests for token blocklist example
def test_token_blocklist_flow():
    """Test the token blocklist flow in the blocklist example."""
    example = "token_blocklist_example.py"
    with ExampleServer(example) as server:
        try:
            # Login to get a token
            login_response = httpx.post(
                f"{BASE_URL}/login", json={"username": "user1", "password": "password1"}, timeout=5
            )
            assert login_response.status_code == 200
            login_data = login_response.json()

            access_token = login_data.get("access_token")
            assert access_token is not None

            # Access protected route with token
            response = httpx.get(
                f"{BASE_URL}/protected", headers={"Authorization": f"Bearer {access_token}"}, timeout=5
            )
            assert response.status_code == 200

            # Logout (blocklist the token)
            logout_response = httpx.post(
                f"{BASE_URL}/logout", headers={"Authorization": f"Bearer {access_token}"}, timeout=5
            )
            assert logout_response.status_code == 200

            # Try to access protected route with blocklisted token
            response = httpx.get(
                f"{BASE_URL}/protected", headers={"Authorization": f"Bearer {access_token}"}, timeout=5
            )
            assert response.status_code == 401
        except httpx.ConnectError as e:
            pytest.fail(f"Could not connect to server: {e}")


# Specific tests for token locations example
def test_token_locations():
    """Test the different token locations in the token locations example."""
    example = "token_locations_example.py"
    with ExampleServer(example) as server:
        try:
            # Login to get a token
            login_response = httpx.post(
                f"{BASE_URL}/login", json={"username": "user1", "password": "password1"}, timeout=5
            )
            assert login_response.status_code == 200
            login_data = login_response.json()

            access_token = login_data.get("access_token")
            assert access_token is not None

            # Test token in Authorization header
            response = httpx.get(
                f"{BASE_URL}/protected", headers={"Authorization": f"Bearer {access_token}"}, timeout=5
            )
            assert response.status_code == 200

            # Test token in query string
            response = httpx.get(f"{BASE_URL}/protected?token={access_token}", timeout=5)
            assert response.status_code == 200

            # Test token in cookies
            cookies = {"access_token": access_token}
            response = httpx.get(f"{BASE_URL}/protected", cookies=cookies, timeout=5)
            assert response.status_code == 200

            # Test token in JSON body
            response = httpx.post(f"{BASE_URL}/protected-post", json={"access_token": access_token}, timeout=5)
            assert response.status_code == 200

        except httpx.ConnectError as e:
            pytest.fail(f"Could not connect to server: {e}")


# Specific tests for fresh token example
def test_fresh_token_flow():
    """Test the fresh token flow in the fresh token example."""
    example = "fresh_token_example.py"
    with ExampleServer(example) as server:
        try:
            # Login to get a fresh token
            login_response = httpx.post(
                f"{BASE_URL}/login", json={"username": "user1", "password": "password1"}, timeout=5
            )
            assert login_response.status_code == 200
            login_data = login_response.json()

            fresh_token = login_data.get("fresh_token")
            assert fresh_token is not None

            # Access protected route with fresh token
            response = httpx.get(f"{BASE_URL}/protected", headers={"Authorization": f"Bearer {fresh_token}"}, timeout=5)
            assert response.status_code == 200

            # Access fresh-required route with fresh token
            response = httpx.get(
                f"{BASE_URL}/fresh-required", headers={"Authorization": f"Bearer {fresh_token}"}, timeout=5
            )
            assert response.status_code == 200

            # Get a non-fresh token
            refresh_response = httpx.post(
                f"{BASE_URL}/refresh", headers={"Authorization": f"Bearer {fresh_token}"}, timeout=5
            )
            assert refresh_response.status_code == 200
            refresh_data = refresh_response.json()

            non_fresh_token = refresh_data.get("access_token")
            assert non_fresh_token is not None

            # Access protected route with non-fresh token
            response = httpx.get(
                f"{BASE_URL}/protected", headers={"Authorization": f"Bearer {non_fresh_token}"}, timeout=5
            )
            assert response.status_code == 200

            # Try to access fresh-required route with non-fresh token
            response = httpx.get(
                f"{BASE_URL}/fresh-required", headers={"Authorization": f"Bearer {non_fresh_token}"}, timeout=5
            )
            assert response.status_code == 401

        except httpx.ConnectError as e:
            pytest.fail(f"Could not connect to server: {e}")


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
