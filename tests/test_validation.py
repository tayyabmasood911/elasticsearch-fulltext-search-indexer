import os
import json
import unittest
import yaml

class TestElasticsearchIndexerConfig(unittest.TestCase):
    def test_core_files_exist(self):
        required_files = [
            "README.md",
            "Makefile",
            "SECURITY.md",
            ".gitattributes",
            ".github/workflows/ci.yml",
            "scripts/healthcheck.sh",
            "config/production.env.example",
            "mapping.json",
            "index_template.json",
            "indexer.py",
            "docker-compose.yml",
            "docs/architecture.svg"
        ]
        for file_path in required_files:
            self.assertTrue(os.path.exists(file_path), f"Missing required file: {file_path}")

    def test_mapping_definition_and_analyzers(self):
        with open("mapping.json", "r", encoding="utf-8") as f:
            mapping = json.load(f)
        
        self.assertIn("settings", mapping)
        self.assertIn("mappings", mapping)
        
        # Verify custom analyzers & filters
        analysis = mapping["settings"]["analysis"]
        self.assertIn("analyzer", analysis)
        self.assertIn("filter", analysis)
        self.assertIn("autocomplete_analyzer", analysis["analyzer"])
        self.assertIn("content_analyzer", analysis["analyzer"])
        self.assertIn("autocomplete_filter", analysis["filter"])
        self.assertIn("synonym_filter", analysis["filter"])

        # Verify properties
        props = mapping["mappings"]["properties"]
        self.assertIn("title", props)
        self.assertIn("description", props)
        self.assertIn("category", props)
        self.assertIn("price", props)

    def test_index_template_structure(self):
        with open("index_template.json", "r", encoding="utf-8") as f:
            template = json.load(f)
        self.assertIn("index_patterns", template)
        self.assertIn("template", template)

    def test_docker_compose_validity(self):
        with open("docker-compose.yml", "r", encoding="utf-8") as f:
            compose = yaml.safe_load(f)
        self.assertIn("services", compose)
        self.assertIn("elasticsearch", compose["services"])
        self.assertIn("kibana", compose["services"])

    def test_architecture_diagram_white_theme(self):
        with open("docs/architecture.svg", "r", encoding="utf-8") as f:
            svg = f.read()
        self.assertIn('fill="#ffffff"', svg, "Must have pure white background")
        self.assertIn("Elasticsearch", svg)

if __name__ == "__main__":
    unittest.main()
