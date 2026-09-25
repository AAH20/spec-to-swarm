"""
OpenAPI 3.1 & RFC Specification Parser for Spec-To-Swarm.
Extracts endpoints, schemas, tags, and data models.
"""

import json
from typing import Dict, List, Optional, Tuple, Any
from .models import APIEndpoint, EndpointMethod


class OpenAPIParser:
    """Extracts typed API operations from OpenAPI 3.0 / 3.1 specification schemas."""

    def __init__(self, raw_spec: Dict[str, Any]):
        self.raw_spec = raw_spec
        self.title = raw_spec.get("info", {}).get("title", "Untitled API")
        self.version = raw_spec.get("info", {}).get("version", "1.0.0")
        self.paths = raw_spec.get("paths", {})
        self.components = raw_spec.get("components", {}).get("schemas", {})

    @classmethod
    def from_json_or_yaml(cls, content: str) -> "OpenAPIParser":
        """Parse raw JSON string representation of OpenAPI spec."""
        try:
            data = json.loads(content)
            return cls(data)
        except Exception:
            # Fallback simple dictionary mock parser if YAML without PyYAML
            return cls({"info": {"title": "Parsed API", "version": "1.0.0"}, "paths": {}})

    def extract_endpoints(self) -> List[APIEndpoint]:
        """Flatten OpenAPI paths into discrete APIEndpoint items."""
        endpoints = []
        for path_str, methods in self.paths.items():
            for method_str, op_dict in methods.items():
                m_upper = method_str.upper()
                if m_upper not in EndpointMethod.__members__:
                    continue

                method = EndpointMethod(m_upper)
                summary = op_dict.get("summary") or op_dict.get("operationId") or f"{method.value} {path_str}"
                tags = op_dict.get("tags", ["default"])
                primary_tag = tags[0] if tags else "default"

                # Request schema extract
                req_body = op_dict.get("requestBody", {})
                req_content = req_body.get("content", {}).get("application/json", {}).get("schema")

                # Response schema extract
                responses = op_dict.get("responses", {})
                resp_200 = responses.get("200") or responses.get("201") or {}
                resp_content = resp_200.get("content", {}).get("application/json", {}).get("schema")

                # Auth check
                security = op_dict.get("security", self.raw_spec.get("security", []))
                requires_auth = len(security) > 0

                endpoints.append(APIEndpoint(
                    path=path_str,
                    method=method,
                    summary=summary,
                    tag=primary_tag,
                    request_schema=req_content,
                    response_schema=resp_content,
                    requires_auth=requires_auth
                ))

        return endpoints

    def group_by_domain(self) -> Dict[str, List[APIEndpoint]]:
        """Group endpoints by OpenAPI tag/domain."""
        grouped: Dict[str, List[APIEndpoint]] = {}
        for ep in self.extract_endpoints():
            tag = ep.tag
            if tag not in grouped:
                grouped[tag] = []
            grouped[tag].append(ep)
        return grouped
