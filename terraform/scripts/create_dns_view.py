#!/usr/bin/env python3

import os
import json
import requests

from datetime import datetime


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
        resp = self.session.post(f"{self.base_url}/v2/session/users/sign_in",
                                 headers=self.headers, json=payload)
        resp.raise_for_status()
        self.jwt = resp.json()["jwt"]
        print("✅ Logged in.")

    def switch_account(self):
        sandbox_id = self._read_file("sandbox_id.txt")
        payload = {"id": f"identity/accounts/{sandbox_id}"}
        headers = self._auth_headers()
        resp = self.session.post(f"{self.base_url}/v2/session/account_switch",
                                 headers=headers, json=payload)
        resp.raise_for_status()
        self.jwt = resp.json()["jwt"]
        print(f"✅ Switched account to sandbox ID: {sandbox_id}")

    def create_dns_view(self, view_name="demo"):
        url = f"{self.base_url}/api/ddi/v1/dns/view"
        headers = self._auth_headers()

        payload = {
            "inheritance_sources": {
                "gss_tsig_enabled": {"action": "inherit"},
                "sort_list": {"action": "inherit"},
                "dtc_config": {"default_ttl": {"action": "inherit"}},
                "minimal_responses": {"action": "inherit"},
                "synthesize_address_records_from_https": {"action": "inherit"},
                "query_acl": {"action": "inherit"},
                "edns_udp_size": {"action": "inherit"},
                "max_udp_size": {"action": "inherit"},
                "filter_aaaa_on_v4": {"action": "inherit"},
                "filter_aaaa_acl": {"action": "inherit"},
                "transfer_acl": {"action": "inherit"},
                "update_acl": {"action": "inherit"},
                "recursion_enabled": {"action": "inherit"},
                "match_recursive_only": {"action": "inherit"},
                "lame_ttl": {"action": "inherit"},
                "max_cache_ttl": {"action": "inherit"},
                "max_negative_ttl": {"action": "inherit"},
                "recursion_acl": {"action": "inherit"},
                "custom_root_ns_block": {"action": "inherit"},
                "forwarders_block": {"action": "inherit"},
                "add_edns_option_in_outgoing_query": {"action": "inherit"},
                "dnssec_validation_block": {"action": "inherit"},
                "ecs_block": {"action": "inherit"},
                "zone_authority": {
                    "refresh": {"action": "inherit"},
                    "retry": {"action": "inherit"},
                    "expire": {"action": "inherit"},
                    "default_ttl": {"action": "inherit"},
                    "negative_ttl": {"action": "inherit"},
                    "rname": {"action": "inherit"},
                    "mname_block": {"action": "inherit", "value": {}}
                },
                "use_forwarders_for_subzones": {"action": "inherit"}
            },
            "name": view_name,
            "dtc_config": {"default_ttl": 300},
            "compartment_id": None,
            "match_clients_acl": [{"element": "any", "access": "allow"}],
            "match_destinations_acl": [{"element": "any", "access": "allow"}],
            "ip_spaces": []
        }

        print(f"🚀 Creating DNS view '{view_name}'...")
        resp = self.session.post(url, headers=headers, json=payload)

        if resp.status_code != 200:
            print(f"❌ Failed to create DNS view. Status: {resp.status_code}")
            print(resp.text)
            resp.raise_for_status()

        print("✅ DNS view created successfully.")

    def _auth_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.jwt}"
        }

    def _read_file(self, filename):
        with open(filename, "r") as f:
            return f.read().strip()


if __name__ == "__main__":
    session = InfobloxSession()
    session.login()
    session.switch_account()
    session.create_dns_view(view_name="demo")
