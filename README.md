# ⚠️ **CRITICAL WARNING - READ BEFORE PROCEEDING** ⚠️

> ## 🚨 PRE-ALPHA SOFTWARE - NOT FUNCTIONAL 🚨
> 
> **THIS PROJECT IS CURRENTLY IN PRE-ALPHA DEVELOPMENT AND IS NOT YET FUNCTIONAL.**
> 
> ### ❌ DO NOT USE FOR:
> - Production environments
> - Business-critical data
> - Live financial systems
> - Any mission-critical applications
> 
> ### ⚠️ IMPORTANT DISCLAIMERS:
> - **DATA LOSS RISK**: This software may corrupt, lose, or mishandle your data
> - **NO RELIABILITY GUARANTEE**: Features may not work as expected or at all
> - **BREAKING CHANGES**: API and functionality will change without notice
> - **NO SUPPORT**: Limited or no support available during pre-alpha phase
> 
> ### 🔬 INTENDED FOR:
> - Development and testing purposes only
> - Contributors and early adopters willing to accept risks
> - Non-critical experimentation environments
> 
> **By using this software, you acknowledge and accept full responsibility for any potential data loss, system issues, or other consequences.**

---


# BigCapitalPy

**A complete Python rewrite of BigCapital accounting software using Flask, HTML, CSS, and vanilla JavaScript.**

<p align="center">
  <a href="https://github.com/bigcapitalhq/bigcapital" target="_blank">
    <img src="https://raw.githubusercontent.com/abouolia/blog/main/public/bigcapital.svg" alt="BigCapitalPy" width="280" height="75">
  </a>
</p>

<p align="center">
  <strong>BigCapitalPy - Python-based accounting software with HTML, CSS, and vanilla JavaScript frontend.</strong>
</p>

<p align="center">
  <em>A complete rewrite of BigCapital using Flask, SQLAlchemy, and modern web technologies.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+"/>
  <img src="https://img.shields.io/badge/flask-2.3+-green.svg" alt="Flask 2.3+"/>
  <img src="https://img.shields.io/badge/postgresql-15-blue.svg" alt="PostgreSQL 15"/>
  <img src="https://img.shields.io/badge/docker-ready-blue.svg" alt="Docker Ready"/>
 <img src="https://img.shields.io/badge/license-AGPL-blue.svg" alt="AGPL License"/>
</p>

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Docker & Docker Compose (for containerized setup)

### Option 1: Quick Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/bigcapitalhq/bigcapital.git bigcapitalpy
   cd bigcapitalpy
   ```

2. **Run the quick start script**
   ```bash
   python run_bigcapitalpy.py
   ```

3. **Access the application**
   - Open your browser: `http://localhost:5000`
   - Login credentials:
     - **Email:** `admin@bigcapitalpy.com`
     - **Password:** `admin123`

### Option 2: Docker Setup

1. **Clone and start with Docker**
   ```bash
   git clone https://github.com/bigcapitalhq/bigcapital.git bigcapitalpy
   cd bigcapitalpy
   make quick-start-docker
   ```

2. **Access services**
   - **Application:** http://localhost:5000
   - **pgAdmin:** http://localhost:8080
   - **Nginx Proxy:** http://localhost

### Option 3: Makefile Commands

```bash
# View all available commands
make help

# Local development setup
make setup
make run

# Docker development
make up-build
make logs

# Database operations
make db-upgrade
make db-migrate MSG="Your migration message"
```

## 🏗️ Architecture

BigCapitalPy follows a modern, modular architecture:

### Backend Stack
- **Flask** - Web framework with Blueprint organization
- **SQLAlchemy** - Database ORM with PostgreSQL
- **Flask-Login** - User authentication and session management
- **Flask-WTF** - Form handling and CSRF protection
- **Flask-Migrate** - Database migrations and versioning
- **Redis** - Caching and session storage
- **Celery** - Background task processing (planned)

### Frontend Stack
- **Bootstrap 5** - Responsive UI framework
- **Vanilla JavaScript** - No heavy frontend frameworks
- **Chart.js** - Interactive data visualization
- **Bootstrap Icons** - Icon library
- **Jinja2** - Server-side templating

### Infrastructure
- **PostgreSQL** - Primary database
- **Docker** - Containerization
- **Nginx** - Reverse proxy and static file serving
- **Gotenberg** - PDF generation service

### Project Structure
```
bigcapitalpy/
├── packages/
│   ├── server/src/           # Backend Python code
│   │   ├── database/         # Database configuration
│   │   └── models/           # SQLAlchemy models
│   └── webapp/src/           # Frontend code
│       ├── routes/           # Flask routes/blueprints
│       ├── templates/        # Jinja2 HTML templates
│       └── static/           # CSS, JS, images
├── docker/                   # Docker configuration files
├── app.py                    # Main Flask application
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # Development services
├── Makefile                 # Build and deployment automation
└── requirements-python.txt  # Python dependencies
```

## ✨ Features

### 🧾 Core Accounting Features
- [x] **Dashboard** - Overview of key metrics and recent activity
- [x] **Customer Management** - Complete customer lifecycle management
- [x] **User Authentication** - Secure multi-user login system
- [x] **Multi-tenancy** - Support for multiple organizations
- [x] **Invoicing** - Create, send, and track invoices
- [x] **Vendor Management** - Track vendors and expenses
- [x] **Item/Inventory Management** - Product catalog and stock tracking
- [ ] **Chart of Accounts** - Customizable accounting structure
- [ ] **Financial Reports** - P&L, Balance Sheet, Cash Flow
- [ ] **Payment Tracking** - Record payments and receipts
- [ ] **Journal Entries** - Manual accounting entries
- [ ] **Bank Reconciliation** - Match transactions with bank statements
- [ ] **Tax Management** - Sales tax and VAT calculations- Australian GST

### 🔧 Technical Features
- [x] **Responsive Design** - Works on desktop, tablet, and mobile
- [x] **CSRF Protection** - Security against cross-site attacks
- [x] **Database Migrations** - Schema versioning with Flask-Migrate
- [x] **Docker Support** - Full containerization with docker-compose
- [x] **Health Checks** - Service monitoring and status endpoints
- [x] **Nginx Integration** - Production-ready reverse proxy setup
- [ ] **RESTful API** - Complete API for integrations
- [ ] **PDF Generation** - Export invoices and reports
- [ ] **Excel Export** - Data export capabilities
- [ ] **Email Integration** - Send invoices and notifications
- [ ] **Backup & Restore** - Automated database backups
- [ ] **Audit Trail** - Track all changes and user actions

### 🚀 Developer Experience
- [x] **Comprehensive Makefile** - 40+ automation commands
- [x] **Hot Reloading** - Automatic server restart during development
- [x] **Code Formatting** - Black and isort integration
- [x] **Testing Framework** - pytest with coverage reporting
- [x] **Development Tools** - Debugging and profiling support
- [x] **Documentation** - Inline documentation and examples

## 🛠️ Development

### Manual Setup (Alternative to quick start)

1. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements-python.txt
   pip install -r requirements-dev.txt  # For development tools
   ```

3. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   export FLASK_APP=app.py
   export FLASK_ENV=development
   ```

4. **Initialize database**
   ```bash
   flask db upgrade
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

### Database Management

BigCapitalPy uses PostgreSQL for production and SQLite for development. Database migrations are handled by Flask-Migrate:

```bash
# Initialize migrations (first time only)
make db-init

# Create a new migration
make db-migrate MSG="Add new table"

# Apply migrations
make db-upgrade

# Reset database (destroys all data)
make db-reset
```

### Docker Development

The Docker setup includes all necessary services:

```bash
# Start all services
make up

# Build and start services
make up-build

# View logs
make logs

# Stop services
make down

# Access database shell
make shell-db

# Backup database
make backup-db
```

### Testing

```bash
# Run tests
make test

# Run tests with coverage
make test-coverage

# Run linting
make lint

# Format code
make format
```

## 🎨 Frontend Development

The frontend uses vanilla JavaScript with a modular approach for better maintainability:

### File Structure
- **CSS**: `packages/webapp/src/static/css/main.css`
- **JavaScript**: `packages/webapp/src/static/js/main.js`
- **Templates**: `packages/webapp/src/templates/`
- **Images**: `packages/webapp/src/static/images/`

### Adding New Features

1. **Backend Route**:
   ```python
   # packages/webapp/src/routes/your_module.py
   from flask import Blueprint, render_template
   
   your_bp = Blueprint('your_module', __name__)
   
   @your_bp.route('/')
   def index():
       return render_template('your_module/index.html')
   ```

2. **Database Model**:
   ```python
   # packages/server/src/models/__init__.py
   class YourModel(db.Model):
       __tablename__ = 'your_table'
       id = db.Column(db.Integer, primary_key=True)
       # Add your fields
   ```

3. **HTML Template**:
   ```html
   <!-- packages/webapp/src/templates/your_module/index.html -->
   {% extends "base.html" %}
   {% block content %}
       <!-- Your content -->
   {% endblock %}
   ```

### JavaScript API

BigCapitalPy includes a custom JavaScript framework:

```javascript
// Making API calls
BigCapitalPy.api.get('/api/customers')
    .then(data => console.log(data))
    .catch(error => console.error(error));

// Show notifications
BigCapitalPy.utils.showToast('Success!', 'success');

// Format currency
BigCapitalPy.utils.formatCurrency(1234.56); // Returns "$1,234.56"
```

## ⚙️ Configuration

BigCapitalPy uses environment variables for configuration. Copy `.env.example` to `.env` and modify:

### Core Settings
```bash
# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/bigcapitalpy

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (for sending invoices)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Docker Configuration

The `docker-compose.yml` includes:
- **PostgreSQL** database with persistent storage
- **Redis** for caching and sessions
- **Nginx** reverse proxy for production-like setup
- **pgAdmin** for database management
- **Gotenberg** for PDF generation

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions | `dev-secret-key` |
| `DATABASE_URL` | Database connection string | SQLite for dev |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `FLASK_ENV` | Environment mode | `development` |
| `MAIL_SERVER` | SMTP server for emails | None |

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| bigcapitalpy | 5000 | Main Flask application |
| postgres | 5432 | PostgreSQL database |
| redis | 6379 | Redis cache |
| nginx | 80/443 | Reverse proxy |
| pgadmin | 8080 | Database admin interface |
| gotenberg | 3000 | PDF generation service |

## � Migration from Original BigCapital

### Why Python Instead of React?

This rewrite addresses several limitations of the original React-based BigCapital:

| Aspect | Original BigCapital | BigCapitalPy |
|--------|-------------------|--------------|
| **Complexity** | Heavy Node.js + React stack | Simple Python + HTML |
| **Performance** | Client-side rendering overhead | Fast server-side rendering |
| **SEO** | Poor search engine optimization | Excellent SEO with SSR |
| **Dependencies** | 500+ npm packages | ~20 Python packages |
| **Build Process** | Complex webpack/babel setup | No build process needed |
| **Learning Curve** | Requires React/JS expertise | Standard web development |
| **Deployment** | Complex multi-service setup | Simple Flask deployment |
| **Customization** | Framework constraints | Full control over UI/UX |

### Migration Benefits

1. **🚀 Performance** - Faster initial page loads and better caching
2. **🔧 Simplicity** - Easier to understand, modify, and extend
3. **📈 SEO-Friendly** - Better search engine optimization
4. **🛠️ Maintainability** - Standard Python patterns and practices
5. **💰 Cost-Effective** - Lower hosting requirements
6. **🎯 Flexibility** - Complete control without framework limitations

### Data Migration

BigCapitalPy provides tools to migrate data from the original BigCapital:

```bash
# Export data from original BigCapital
# (Custom migration scripts to be provided)

# Import into BigCapitalPy
python manage.py import_bigcapital_data --file=export.json
```

## � Screenshots

<p align="center">
  <img src="https://raw.githubusercontent.com/abouolia/blog/main/public/screenshot-2.png" width="270" alt="Dashboard">
  <img src="https://raw.githubusercontent.com/abouolia/blog/main/public/screenshot-1.png" width="270" alt="Invoices">
  <img src="https://raw.githubusercontent.com/abouolia/blog/main/public/screenshot-3.png" width="270" alt="Reports">
</p>

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Getting Started
1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/yourusername/bigcapitalpy.git`
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Install** dependencies: `make install-dev`
5. **Make** your changes
6. **Test** your changes: `make test`
7. **Commit** your changes: `git commit -m 'Add amazing feature'`
8. **Push** to your branch: `git push origin feature/amazing-feature`
9. **Submit** a pull request

### Development Guidelines
- Follow PEP 8 coding standards
- Write tests for new features
- Update documentation as needed
- Use meaningful commit messages
- Ensure all tests pass before submitting

### Areas We Need Help
- 🧾 **Invoicing Module** - Invoice creation and management
- 📊 **Financial Reports** - P&L, Balance Sheet, Cash Flow
- 💳 **Payment Processing** - Integration with payment gateways
- 📱 **Mobile Optimization** - Better mobile experience
- 🌐 **Internationalization** - Multi-language support
- 🔌 **API Development** - RESTful API endpoints
- 📚 **Documentation** - User guides and API docs

## 🏗️ Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   cp .env.example .env
   # Configure production settings in .env
   ```

2. **Docker Production**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Traditional Deployment**
   ```bash
   pip install -r requirements-python.txt
   flask db upgrade
   gunicorn --bind 0.0.0.0:5000 app:app
   ```

### Security Considerations
- Change default passwords and secrets
- Use HTTPS in production
- Configure firewall rules
- Regular security updates
- Database backups

## 📖 Documentation

- **[API Reference](docs/api.md)** - REST API documentation
- **[User Guide](docs/user-guide.md)** - How to use BigCapitalPy
- **[Developer Guide](docs/developer-guide.md)** - Technical documentation
- **[Deployment Guide](docs/deployment.md)** - Production deployment
- **[Migration Guide](docs/migration.md)** - Migrating from original BigCapital

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Original BigCapital Team** - For the inspiration and excellent design
- **Flask Community** - For the robust web framework
- **SQLAlchemy Team** - For the powerful ORM
- **Bootstrap Team** - For the responsive UI framework
- **All Contributors** - For making this project better

## 📞 Support & Community

### Get Help
- 📚 **Documentation**: Check our comprehensive docs
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/bigcapitalhq/bigcapital/issues)
- � **Discussions**: [GitHub Discussions](https://github.com/bigcapitalhq/bigcapital/discussions)
- 💻 **Discord**: [Join our community](https://discord.com/invite/c8nPBJafeb)

### Commercial Support
For enterprise support, custom development, or consulting:

<a target="_blank" href="https://cal.com/ahmed-bouhuolia-ekk3ph/30min">
  <img src="https://cal.com/book-with-cal-dark.svg" alt="Book us with Cal.com" width="200"/>
</a>

---

<p align="center">
  <strong>BigCapitalPy</strong> - Simple, smart accounting software built with Python ❤️
</p>

<p align="center">
  <a href="https://my.bigcapital.app">Try BigCapital Cloud</a> •
  <a href="https://docs.bigcapital.app">Documentation</a> •
  <a href="https://github.com/bigcapitalhq/bigcapital/discussions">Community</a>
</p>
