"""
Shared network helpers for interacting with the Breathesafe Rails app.
"""

from __future__ import annotations

import logging
import os
from typing import Dict

import requests

INTERNAL_EXPORT_TOKEN_HEADER = "X-Breathesafe-Internal-Token"


def build_session(cookie: str | None) -> requests.Session:
  session = requests.Session()
  if cookie:
    session.headers.update({"Cookie": cookie})
  session.headers.update({"Accept": "application/json"})
  return session


def login_with_credentials(
  session: requests.Session, base_url: str, email: str, password: str
) -> None:
  login_url = f"{base_url.rstrip('/')}/users/log_in.json"
  logging.info("Logging in via %s", login_url)
  response = session.post(
    login_url,
    json={"user": {"email": email, "password": password}},
    timeout=30,
  )
  if response.status_code not in (200, 201):
    raise RuntimeError(f"Login failed ({response.status_code}): {response.text}")
  logging.info("Login successful; session cookie established.")


def logout(session: requests.Session, base_url: str) -> None:
  logout_url = f"{base_url.rstrip('/')}/users/log_out.json"
  logging.info("Logging out via %s", logout_url)
  response = session.delete(logout_url, timeout=30)
  if response.status_code != 200:
    logging.warning(
      "Logout returned status %s: %s", response.status_code, response.text
    )
  else:
    logging.info("Logout successful.")


def fetch_json(session: requests.Session, url: str, headers: Dict | None = None) -> Dict:
  logging.info("Fetching %s", url)
  response = session.get(url, headers=headers, timeout=60)
  response.raise_for_status()
  return response.json()


def fetch_facial_measurements_fit_tests(
  base_url='http://localhost:3000',
  session=None,
  include_without_facial_measurements=False,
):
  base = base_url.rstrip('/')
  internal_api_token = os.getenv("MASK_RECOMMENDER_INTERNAL_API_TOKEN")
  params = ""
  if include_without_facial_measurements:
    params = "?include_without_facial_measurements=true"
  if internal_api_token:
    fit_tests_url = f"{base}/internal/facial_measurements_fit_tests.json{params}"
    headers = {INTERNAL_EXPORT_TOKEN_HEADER: internal_api_token}
  else:
    fit_tests_url = f"{base}/facial_measurements_fit_tests.json{params}"
    headers = None
  if session is None:
    session = build_session(None)

  return fetch_json(session, fit_tests_url, headers=headers)[
    "fit_tests_with_facial_measurements"
  ]


def fetch_dashboard_stats(base_url='http://localhost:3000', session=None):
  base = base_url.rstrip('/')
  url = f"{base}/dashboard/stats.json"
  if session is None:
    session = build_session(None)

  return fetch_json(session, url)
