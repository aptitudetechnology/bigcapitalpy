<p align="center">
# BigCapitalPy

**A complete Python rewrite of BigCapital accounting software using Flask, HTML, CSS, and vanilla JavaScript.**

<p align="center">
  <p align="center">
    <a href="https://github.com/bigcapitalhq/bigcapital" target="_blank">
      <img src="https://raw.githubusercontent.com/abouolia/blog/main/public/bigcapital.svg" alt="BigCapitalPy" width="280" height="75">
    </a>
  </p>
  <p align="center">
    BigCapitalPy - Python-based accounting software with HTML, CSS, and vanilla JavaScript frontend.
  </p>
  <p align="center">
    A complete rewrite of BigCapital using Flask, SQLAlchemy, and modern web technologies.
  </p>

  <p align="center">
    <img src="https://img.shields.io/badge/python-3.8+-blue.svg" />
    <img src="https://img.shields.io/badge/flask-2.3+-green.svg" />
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" />
  </p>
</p>

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/bigcapitalhq/bigcapital.git bigcapitalpy
   cd bigcapitalpy
   ```

2. **Run the quick start script**
   ```bash
   python run_bigcapitalpy.py
   ```

   This script will:
   - Create a Python virtual environment
   - Install all required dependencies
   - Set up the database with sample data
   - Start the development server

3. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Login with demo credentials:
     - **Email:** `admin@bigcapitalpy.com`
     - **Password:** `admin123`

## 🏗️ Architecture

BigCapitalPy follows a modern, modular architecture:

### Backend (Python/Flask)
- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **Flask-Login** - User authentication
- **Flask-WTF** - Form handling and CSRF protection
- **Flask-Migrate** - Database migrations

### Frontend (HTML/CSS/JS)
- **Bootstrap 5** - UI framework
- **Vanilla JavaScript** - No heavy frontend frameworks
- **Chart.js** - Data visualization
- **Bootstrap Icons** - Icon library

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
├── app.py                    # Main Flask application
├── run_bigcapitalpy.py      # Quick start script
└── requirements-python.txt  # Python dependencies
```

## 🎯 Features

### Core Accounting Features
- [x] **Dashboard** - Overview of key metrics and recent activity
- [x] **Customer Management** - Add, edit, and manage customers
- [x] **User Authentication** - Secure login system
- [ ] **Invoicing** - Create and manage invoices
- [ ] **Vendor Management** - Track vendors and expenses
- [ ] **Item/Inventory Management** - Product catalog
- [ ] **Chart of Accounts** - Customizable accounting structure
- [ ] **Financial Reports** - P&L, Balance Sheet, etc.
- [ ] **Payment Tracking** - Record payments and receipts
- [ ] **Journal Entries** - Manual accounting entries

### Technical Features
- [x] **Multi-tenancy** - Support for multiple organizations
- [x] **Responsive Design** - Works on desktop and mobile
- [x] **CSRF Protection** - Security against cross-site attacks
- [x] **Database Migrations** - Schema versioning
- [ ] **API Endpoints** - RESTful API for integrations
- [ ] **PDF Generation** - Export invoices and reports
- [ ] **Excel Export** - Data export capabilities
- [ ] **Email Integration** - Send invoices via email

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
   ```

3. **Set environment variables**
   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

### Database Management

The application uses SQLite by default for development. Database migrations are handled by Flask-Migrate:

```bash
# Initialize migrations (first time only)
flask db init

# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade
```

## 🎨 Frontend Development

The frontend uses vanilla JavaScript with a modular approach:

- **CSS**: Located in `packages/webapp/src/static/css/`
- **JavaScript**: Located in `packages/webapp/src/static/js/`
- **Templates**: Jinja2 templates in `packages/webapp/src/templates/`

### Adding New Features

1. **Backend**: Add routes in `packages/webapp/src/routes/`
2. **Frontend**: Create templates and add JavaScript functionality
3. **Database**: Update models in `packages/server/src/models/`

## 🔧 Configuration

Key configuration options can be set via environment variables:

- `SECRET_KEY` - Flask secret key for sessions
- `DATABASE_URL` - Database connection string
- `FLASK_ENV` - Environment (development/production)

## 📝 Why Python Instead of React?

This rewrite addresses several limitations of the original React-based BigCapital:

1. **Simplicity** - Easier to understand and modify
2. **Performance** - Server-side rendering for faster initial loads
3. **SEO-Friendly** - Better search engine optimization
4. **Lower Complexity** - No complex build processes or npm dependencies
5. **Flexibility** - Full control over UI without framework constraints

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original BigCapital team for the inspiration and design
- Flask and SQLAlchemy communities for excellent documentation
- Bootstrap team for the UI framework

## 📞 Support

For questions and support:
- Open an issue on GitHub
- Check the documentation
- Join our community discussions

---

**BigCapitalPy** - Simple, smart accounting software built with Python ❤️

  <p align="center">
    <a href="https://my.bigcapital.app">Bigcapital Cloud</a>
  </p>
</p>

# What's Bigcapital?

Bigcapital is a smart and open-source accounting and inventory software, Bigcapital keeps all business finances in right place and automates accounting processes to give the business powerful and intelligent financial statements and reports to help in making decisions.

<p align="center">
  <img src="https://raw.githubusercontent.com/abouolia/blog/main/public/screenshot-2.png" width="270">
  <img src="https://raw.githubusercontent.com/abouolia/blog/main/public/screenshot-1.png" width="270">
  <img src="https://raw.githubusercontent.com/abouolia/blog/main/public/screenshot-3.png" width="270">
</p>

# Getting Started

We've got serveral options on dev and prod depending on your need to get started quickly with Bigcapital.

## Self-hosted 

Bigcapital is available open-source under AGPL license. You can host it on your own servers using Docker.

### Docker

To get started with self-hosted with Docker and Docker Compose, take a look at the [Docker guide](https://docs.bigcapital.app/deployment/docker).

## Development

### Local Setup

To get started locally, we have a [guide to help you](https://github.com/bigcapitalhq/bigcapital/blob/develop/CONTRIBUTING.md).

### Gitpod

- Click the Gitpod button below to open this project in development mode.
- This will open and configure the workspace in your browser with all the necessary dependencies.

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/new/#https://github.com/bigcapitalhq/bigcapital)

## Headless Accounting

You can integrate Bigcapital API with your system to organize your transactions in double-entry system to get the best financial reports.

[![Run in Postman](https://run.pstmn.io/button.svg)](https://www.postman.com/bigcapital/workspace/bigcapital-api)

# Resources

- [Documentation](https://docs.bigcapital.app/) - Learn how to use.
- [API Reference](https://docs.bigcapital.app/api-reference) - API reference docs
- [Contribution](https://github.com/bigcapitalhq/bigcapital/blob/develop/CONTRIBUTING.md) - Welcome to any contributions.
- [Discord](https://discord.com/invite/c8nPBJafeb) - Ask for help.
- [Bug Tracker](https://github.com/bigcapitalhq/bigcapital/issues) - Notify us new bugs.

# Changelog

Please see [Releases](https://github.com/bigcapitalhq/bigcapital/releases) for more information what has changed recently.

# Contact us

Meet our sales team for any commercial inquiries.

<a target="_blank" href="https://cal.com/ahmed-bouhuolia-ekk3ph/30min"><img src="https://cal.com/book-with-cal-dark.svg" alt="Book us with Cal.com"></a>

# Recognition

<a href="https://news.ycombinator.com/item?id=36118990">
  <img
    style="width: 250px; height: 54px;" width="250" height="54"
    alt="Featured on Hacker News"
    src="https://hackernews-badge.vercel.app/api?id=36118990"
  />
</a>

# Contributors

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/abouolia"><img src="https://avatars.githubusercontent.com/u/2197422?v=4?s=100" width="100px;" alt="Ahmed Bouhuolia"/><br /><sub><b>Ahmed Bouhuolia</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/commits?author=abouolia" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://ameir.net"><img src="https://avatars.githubusercontent.com/u/374330?v=4?s=100" width="100px;" alt="Ameir Abdeldayem"/><br /><sub><b>Ameir Abdeldayem</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/issues?q=author%3Aameir" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/elforjani13"><img src="https://avatars.githubusercontent.com/u/39470382?v=4?s=100" width="100px;" alt="ElforJani13"/><br /><sub><b>ElforJani13</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/commits?author=elforjani13" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://scheibling.se"><img src="https://avatars.githubusercontent.com/u/24367830?v=4?s=100" width="100px;" alt="Lars Scheibling"/><br /><sub><b>Lars Scheibling</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/issues?q=author%3Ascheibling" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/suhaibaffan"><img src="https://avatars.githubusercontent.com/u/18115937?v=4?s=100" width="100px;" alt="Suhaib Affan"/><br /><sub><b>Suhaib Affan</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/commits?author=suhaibaffan" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/KalliopiPliogka"><img src="https://avatars.githubusercontent.com/u/81677549?v=4?s=100" width="100px;" alt="Kalliopi Pliogka"/><br /><sub><b>Kalliopi Pliogka</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/issues?q=author%3AKalliopiPliogka" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://me.kochie.io"><img src="https://avatars.githubusercontent.com/u/10809884?v=4?s=100" width="100px;" alt="Robert Koch"/><br /><sub><b>Robert Koch</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/commits?author=kochie" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://cschuijt.nl"><img src="https://avatars.githubusercontent.com/u/5460015?v=4?s=100" width="100px;" alt="Casper Schuijt"/><br /><sub><b>Casper Schuijt</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/issues?q=author%3Acschuijt" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ANasouf"><img src="https://avatars.githubusercontent.com/u/19536487?v=4?s=100" width="100px;" alt="ANasouf"/><br /><sub><b>ANasouf</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/commits?author=ANasouf" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://ragnarlaud.dev"><img src="https://avatars.githubusercontent.com/u/3042904?v=4?s=100" width="100px;" alt="Ragnar Laud"/><br /><sub><b>Ragnar Laud</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/issues?q=author%3Axprnio" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/asenawritescode"><img src="https://avatars.githubusercontent.com/u/67445192?v=4?s=100" width="100px;" alt="Asena"/><br /><sub><b>Asena</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/issues?q=author%3Aasenawritescode" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://snyder.tech"><img src="https://avatars.githubusercontent.com/u/707567?v=4?s=100" width="100px;" alt="Ben Snyder"/><br /><sub><b>Ben Snyder</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/commits?author=benpsnyder" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://vederis.id"><img src="https://avatars.githubusercontent.com/u/13505006?v=4?s=100" width="100px;" alt="Vederis Leunardus"/><br /><sub><b>Vederis Leunardus</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/commits?author=cloudsbird" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.pivoten.com"><img src="https://avatars.githubusercontent.com/u/104120598?v=4?s=100" width="100px;" alt="Chris Cantrell"/><br /><sub><b>Chris Cantrell</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/issues?q=author%3Accantrell72" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/oleynikd"><img src="https://avatars.githubusercontent.com/u/3976868?v=4?s=100" width="100px;" alt="Denis"/><br /><sub><b>Denis</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/issues?q=author%3Aoleynikd" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://myself.vercel.app/"><img src="https://avatars.githubusercontent.com/u/42431274?v=4?s=100" width="100px;" alt="Sachin Mittal"/><br /><sub><b>Sachin Mittal</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/issues?q=author%3Amittalsam98" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.camilooviedo.com/"><img src="https://avatars.githubusercontent.com/u/64604272?v=4?s=100" width="100px;" alt="Camilo Oviedo"/><br /><sub><b>Camilo Oviedo</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/commits?author=Champetaman" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://nklmantey.com/"><img src="https://avatars.githubusercontent.com/u/90279429?v=4?s=100" width="100px;" alt="Mantey"/><br /><sub><b>Mantey</b></sub></a><br /><a href="https://github.com/bigcapitalhq/bigcapital/issues?q=author%3Anklmantey" title="Bug reports">🐛</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
