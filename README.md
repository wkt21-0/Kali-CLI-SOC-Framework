# Kali SOC Compliance Framework

<img width="1024" height="1024" alt="Kali SOC Framework" src="https://github.com/user-attachments/assets/4e7a06ab-f531-4df6-8744-8dd0d97ffb58" />

A comprehensive, modular Bash + Python framework for SOC automation, MITRE ATT&CK simulations, log generation, and security operations lab exercises.

## 📋 Overview

The Kali SOC Compliance Framework provides an extensible toolkit for security operations professionals and students. It integrates with industry-standard tools (SIEM, ELK, Sigma rules) and supports hands-on lab exercises mapped to a structured SOC Analyst roadmap.

**Key Use Cases:**
- MITRE ATT&CK technique simulation and validation
- Realistic log generation for SIEM/ELK training
- Automated security lab environments
- Detection rule testing and tuning
- Security operations workflow practice

## ✨ Features

- **MITRE ATT&CK Integration** — Simulate and document techniques with roadmap-aligned lab sections
- **Log Generation & Analysis** — Produce realistic execution, network, and authentication events for training
- **Lab Automation** — Bootstrap complete environments with configurable complexity levels
- **Rich Reporting** — Track progression from Core Skills through Advanced Blue Team competencies
- **Secure Ingestion** — TLS and mutual TLS (mTLS) support for endpoint data collection
- **Extensible Architecture** — Add custom modules and plugins via simple manifest format
- **Compliance Mapping** — Track against compliance frameworks (CIS, NIST, PCI-DSS)

## 📦 Installation

### Prerequisites

- Python 3.8+
- Bash 4.0+
- Git
- OpenSSL (for certificate generation)
- Docker & Docker Compose (optional, for containerized deployment)

### Local Setup (Development/Lab)

```bash
# Clone the repository
git clone https://github.com/wkt21-0/Kali-CLI-SOC-Framework.git
cd Kali-CLI-SOC-Framework

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Make scripts executable
chmod +x scripts/*.sh
```

### Running the Ingest Server (Local Lab)

```bash
# Generate self-signed certificates for lab environment
./scripts/generate_mtls_certs.sh --domain localhost --outdir ./certs --client-name lab-agent

# Set environment variables
export INGEST_API_KEY="lab-secret"
export REQUIRE_MTLS="false"  # Set to "true" to enforce client certificates

# Start the FastAPI server
uvicorn ops.ingest.server:app \
  --host 0.0.0.0 \
  --port 5514 \
  --ssl-certfile ./certs/server.crt \
  --ssl-keyfile ./certs/server.key
```

The server will be accessible at `https://localhost:5514/ingest`

## 🚀 Quick Start

### CLI Usage Examples

```bash
# View help and available commands
soc --help

# Simulate a specific ATT&CK technique
soc attack simulate T1059  # Command & Scripting Interpreter

# Generate execution logs
soc logs generate execution --count 100

# Generate network traffic logs
soc logs generate network --duration 3600

# Generate authentication events
soc logs generate auth --users 50

# Create a comprehensive report
soc report generate soc-operations --output report.html

# Check engine status
python -m core.engine status
```

### Testing Ingest with curl

```bash
# Test without mTLS (requires API key only)
curl --insecure \
  -H "X-API-Key: lab-secret" \
  -H "Content-Type: application/json" \
  -d '{"type":"test","timestamp":"2025-01-01T00:00:00Z","msg":"Hello SOC"}' \
  https://localhost:5514/ingest

# Test with mTLS (client certificate required)
curl --insecure \
  --cert ./certs/lab-agent.crt \
  --key ./certs/lab-agent.key \
  -H "X-API-Key: lab-secret" \
  -H "Content-Type: application/json" \
  -d '{"type":"proc","name":"powershell.exe","args":"Get-Process"}' \
  https://localhost:5514/ingest
```

## 📁 Project Structure

```
.
├── bin/                          # Main CLI entry points
├── core/
│   ├── engine.py                 # CLI router and module loader
│   ├── modules/                  # Feature modules (mitre, loggen, sigma, etc.)
│   └── security/
│       └── rbac.py               # Role-based access control
├── ops/                          # Operational services
│   ├── ingest/
│   │   └── server.py             # FastAPI ingestion service
│   ├── threatintel/              # Threat intelligence integration
│   ├── detection/                # Detection rule engine
│   ├── alerts/                   # Alert processing
│   └── dashboard/                # Web UI/dashboard
├── agent/
│   ├── collector/                # Endpoint event collection
│   └── transport/                # Secure transport (TLS/mTLS)
├── config/
│   ├── soc.yaml                  # Main configuration
│   ├── rbac.yaml                 # Role definitions
│   └── compliance.yaml           # Compliance mappings
├── scripts/
│   ├── generate_mtls_certs.sh    # Certificate generation
│   ├── rotate_certs.sh            # Certificate rotation
│   ├── run_mtls_e2e.sh            # End-to-end testing
│   └── ci_run.sh                  # CI pipeline script
├── deployment/
│   ├── nginx/                    # Nginx reverse proxy config
│   ├── docker/                   # Docker & docker-compose files
│   └── certbot/                  # Let's Encrypt setup guide
├── system/
│   └── systemd/                  # Systemd service units
├── tests/                        # Test suite (pytest)
└── data/                         # Runtime logs and artifacts (gitignored)
```

## 🔐 Security & Authentication

### API Key Authentication

All requests to the ingest server require the `X-API-Key` header:

```bash
-H "X-API-Key: $(echo $INGEST_API_KEY)"
```

**Important:** Never commit API keys or secrets to version control. Use environment variables or secure secret management.

### Mutual TLS (mTLS)

For production deployments, enable mutual TLS to verify both client and server:

```bash
# Generate certificates with CA
./scripts/generate_mtls_certs.sh --domain soc.example.com --outdir ./certs

# Enable mTLS in server
export REQUIRE_MTLS=true

# Clients must provide certificate and key
curl --cert client.crt --key client.key https://soc.example.com:5514/ingest
```

### Certificate Rotation

Certificates should be rotated periodically:

```bash
./scripts/rotate_certs.sh --outdir ./certs --clients agent-01,agent-02 --days 365
```

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
# Generate certificates
./scripts/generate_mtls_certs.sh --domain soc.local --outdir ./certs

# Start services
docker-compose -f deployment/docker/docker-compose.mtls.yml up -d

# Run tests
./scripts/run_mtls_e2e.sh --domain soc.local --client agent-01

# Stop services
docker-compose -f deployment/docker/docker-compose.mtls.yml down
```

## 🌐 Production Deployment (Nginx + Certbot)

See [deployment/certbot/README.md](deployment/certbot/README.md) for complete production setup instructions with Let's Encrypt SSL certificates.

**Quick summary:**
```bash
# Install dependencies
sudo apt update && sudo apt install -y nginx python3-certbot-nginx

# Obtain Let's Encrypt certificate
sudo certbot --nginx -d soc.example.com --agree-tos --email admin@example.com

# Start the service
sudo systemctl enable --now soc-ingest.service
```

## 📊 Roadmap Alignment

Every command and module is aligned with a progressive SOC analyst learning roadmap:

1. **Core Skills** — Basic detection, log analysis, alert handling
2. **Intermediate** — Rule tuning, threat intelligence correlation, incident response
3. **Advanced** — Threat hunting, purple team exercises, compliance validation

See the framework's integrated help for roadmap mappings:
```bash
soc --roadmap              # List all aligned lab sections
soc attack --techniques    # Show MITRE ATT&CK simulations
```

## 🧪 Testing

### Unit Tests

```bash
# Run pytest suite
pytest -v

# Run specific test file
pytest tests/ingest/test_ingest.py -v

# Run with coverage
pytest --cov=core --cov=ops
```

### Integration Tests

```bash
# Run mTLS end-to-end tests (requires Docker)
./scripts/run_mtls_e2e.sh --domain soc.test --client agent-01
```

### CI/CD Pipeline

GitHub Actions workflows automatically run tests on push and pull requests:

- `.github/workflows/tests.yml` — Python unit tests
- `.github/workflows/docker-e2e.yml` — Docker integration tests

## 📝 Configuration

### Main Configuration (config/soc.yaml)

```yaml
engine:
  mode: "lab"          # "lab" or "production"
  log_level: "INFO"    # DEBUG, INFO, WARNING, ERROR

paths:
  logs: "data/logs"
  reports: "data/reports"
  plugins: "core/plugins"

ingest:
  host: "0.0.0.0"
  port: 5514
  workers: 4
  timeout: 30
```

### RBAC Configuration (config/rbac.yaml)

```yaml
roles:
  analyst:
    allowed: ["logs:read", "reports:read", "alerts:ack"]
  senior:
    allowed: ["all"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit changes (`git commit -am 'Add my feature'`)
4. Push to branch (`git push origin feature/my-feature`)
5. Open a Pull Request

Please ensure:
- Code follows PEP 8 style guide
- Tests pass (`pytest`)
- Secrets are never committed
- Documentation is updated

## ⚠️ Important Security Notes

### Do NOT Commit

- ❌ Private keys or certificates (`*.key`, `*.pem`)
- ❌ API keys or authentication tokens
- ❌ Credential files or `.env` files with secrets

### Best Practices

✅ Use `scripts/generate_mtls_certs.sh` to create certificates securely  
✅ Store API keys in environment variables or secret management systems  
✅ Rotate certificates regularly using `scripts/rotate_certs.sh`  
✅ Keep Nginx and system packages updated  
✅ Use strong passphrases for certificate private keys  
✅ Restrict file permissions: `chmod 600 /etc/default/soc-ingest`  

## 📚 Documentation

- [Ingest Server API](ops/ingest/README.md)
- [Agent Transport](agent/transport/README.md)
- [Deployment Guide](deployment/certbot/README.md)
- [Configuration Reference](config/README.md)
- [Roadmap Mappings](docs/roadmap.md)

## 🐛 Troubleshooting

### Server won't start

```bash
# Check port availability
lsof -i :5514

# View logs
export INGEST_API_KEY="lab-secret"
uvicorn ops.ingest.server:app --log-level debug

# Verify certificates
openssl x509 -in ./certs/server.crt -text -noout
```

### mTLS client certificate rejected

```bash
# Verify client certificate is valid
openssl x509 -in ./certs/agent.crt -text -noout

# Check certificate chain
openssl verify -CAfile ./certs/ca.crt ./certs/agent.crt

# Test connectivity
curl --cacert ./certs/ca.crt --cert ./certs/agent.crt --key ./certs/agent.key \
  -v https://localhost:5514/ingest
```

### Permission denied errors

```bash
# Fix script permissions
chmod +x scripts/*.sh

# Fix certificate permissions
chmod 600 ./certs/*.key
chmod 644 ./certs/*.crt
```

## 📄 License

This project is provided for educational and authorized testing purposes. Ensure compliance with applicable laws and organizational policies.

## 👨‍💼 Support & Contribution

For questions, issues, or contributions:

- 🐛 [Report Issues](https://github.com/wkt21-0/Kali-CLI-SOC-Framework/issues)
- 💬 [Start Discussion](https://github.com/wkt21-0/Kali-CLI-SOC-Framework/discussions)
- 📧 Contact: [Your Contact Info]

---

**Last Updated:** January 2025  
**Framework Version:** 0.3.0  
**Status:** Active Development
