#!/usr/bin/env python3

import os
import json
import uuid
import requests
from datetime import datetime, timezone

class InfobloxSession:
    def __init__(self):
        self.base_url = "https://csp.infoblox.com"
        self.email = os.getenv("INFOBLOX_EMAIL")
        self.password = os.getenv("INFOBLOX_PASSWORD")
        self.jwt = None
        self.session = requests.Session()
        self.headers = {"Content-Type": "application/json"}

    def login(self):
        payload = {"email": self.email, "password": self.password}
        resp = self.session.post(f"{self.base_url}/v2/session/users/sign_in", headers=self.headers, json=payload)
        resp.raise_for_status()
        self.jwt = resp.json()["jwt"]
        print("✅ Logged in.")

    def switch_account(self):
        sandbox_id = self._read_file("sandbox_id.txt")
        payload = {"id": f"identity/accounts/{sandbox_id}"}
        resp = self.session.post(f"{self.base_url}/v2/session/account_switch",
                                 headers=self._auth_headers(), json=payload)
        resp.raise_for_status()
        self.jwt = resp.json()["jwt"]
        print(f"✅ Switched account to sandbox ID: {sandbox_id}")

    def get_pool_id(self):
        url = f"{self.base_url}/api/infra/v1/detail_hosts"
        resp = self.session.get(url, headers=self._auth_headers())
        resp.raise_for_status()
        data = resp.json()
        host = data["results"][0]
        pool_id = host["pool"]["pool_id"]
        print(f"📥 Extracted pool_id: {pool_id}")
        return pool_id

    def enable_dns_service(self, pool_id, dns_name="infolab.com"):
        url = f"{self.base_url}/api/infra/v1/services"
        headers = self._auth_headers()
        now = datetime.now(timezone.utc).isoformat()

        # 👇 Convert raw pool_id to resource URI format
        full_pool_id = f"infra/pool/{pool_id}"

        payload = {
            "name": dns_name,
            "service_type": "dns",
            "pool_id": full_pool_id,
            "desired_state": "start",
            "created_at": now,
            "updated_at": now,
            "tags": {}
        }

        print(f"🚀 Enabling DNS service '{dns_name}' with payload:")
        print(json.dumps(payload, indent=2))

        resp = self.session.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            print(f"❌ Failed to enable DNS. Status: {resp.status_code}")
            print(resp.text)
            resp.raise_for_status()

        print("✅ DNS service enabled.")

    def _auth_headers(self):
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self.jwt}"}

    def _read_file(self, filename):
        with open(filename, "r") as f:
            return f.read().strip()

if __name__ == "__main__":
    session = InfobloxSession()
    session.login()
    session.switch_account()
    pool_id = session.get_pool_id()
    session.enable_dns_service(pool_id=pool_id, dns_name="infolab.com")
