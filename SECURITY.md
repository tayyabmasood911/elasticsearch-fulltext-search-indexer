# Security Policy

## Supported Versions

The following versions of this project are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0.0 | :x:                |

## Reporting a Vulnerability

We take the security and integrity of our search and indexing infrastructure seriously. If you discover a vulnerability, search injection vector, or denial-of-service flaw, please report it responsibly.

### Disclosure Process

1. **Private Reporting**: Please **DO NOT** file a public GitHub issue. Send your vulnerability report directly via email to **[tayyabmasood911@gmail.com](mailto:tayyabmasood911@gmail.com)** with the subject line `[SECURITY] elasticsearch-fulltext-search-indexer Vulnerability`.
2. **Details to Include**:
   - Description of the vulnerability and attack vector.
   - Minimal reproduction script, index mapping, or search query.
   - Affected analyzer, mapping definition, or indexer component.
   - Proposed mitigation or remediation patch if available.
3. **Response Timelines**:
   - **Initial Acknowledgement**: Within 24 hours.
   - **Triage & Assessment**: Within 72 hours.
   - **Remediation & Advisory Release**: Coordinated fix within 14 business days.

## Security Controls & Best Practices

- **Authentication & RBAC**: Ingestion pipelines authenticate via Elasticsearch API keys or TLS client certificates with least-privilege `create_doc` and `auto_configure_index` roles.
- **Zero Exposed Elastic Port**: Production cluster ports `9200` (HTTP) and `9300` (Transport) must be strictly isolated within private VPC subnets.
- **Payload Sanitization**: Indexing mapping restricts excessive field explosion by disabling dynamic mappings (`dynamic: strict` or `dynamic: false`).

## Safe Harbor

We consider security research conducted in good faith under this policy to be authorized. We will not pursue legal action against researchers who adhere to responsible disclosure principles.
