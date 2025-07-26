if __name__ == '__main__':
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'

    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    CERT_PATH = os.path.join(PROJECT_ROOT, 'ssl', 'cert.pem')
    KEY_PATH = os.path.join(PROJECT_ROOT, 'ssl', 'key.pem')

    logger.info(f"🚀 Starting BigCapitalPy on port {port}")
    logger.info(f"📍 Looking for SSL certs in: {CERT_PATH}, {KEY_PATH}")

    # Ensure database tables and sample data are created when running directly
    with app.app_context():
        db.create_all()

        # Create default organization if it doesn't exist
        if not Organization.query.first():
            org = Organization(
                name='Sample Company',
                currency='USD',
                fiscal_year_start='01-01',
                timezone='UTC'
            )
            db.session.add(org)

            # Create default admin user
            admin_user = User(
                email='admin@bigcapitalpy.com',
                first_name='Admin',
                last_name='User',
                password_hash=generate_password_hash('admin123'),
                is_active=True,
                role='admin',
                organization_id=1
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Default organization and admin user created")
            print("📧 Admin email: admin@bigcapitalpy.com")
            print("🔑 Admin password: admin123")

    if os.path.exists(CERT_PATH) and os.path.exists(KEY_PATH):
        logger.info("✅ SSL certificates found. Running in HTTPS mode.")
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=debug, 
            ssl_context=(CERT_PATH, KEY_PATH),
            threaded=True,  # CRITICAL: This enables concurrent request handling
            use_reloader=False  # Disable auto-reloader for better performance
        )
    else:
        logger.warning("⚠️ SSL certificates not found. Running in HTTP mode.")
        logger.warning("💡 To enable HTTPS, generate them using:")
        logger.warning("   openssl genrsa -out ssl/key.pem 2048 && openssl req -new -x509 -key ssl/key.pem -out ssl/cert.pem -days 365")
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=debug,
            threaded=True  # Enable threading for HTTP mode too
        )