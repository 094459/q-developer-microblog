# Microblogging Application

This is a web-based Microblogging application built with Flask, SQLAlchemy, and PostgreSQL.

## Features

- User registration and authentication
- Write posts
- Favoruite posts

## Requirements

- Python 3.7+
- PostgreSQL
- Flask, Flask-SQLAlchemy, Flask-Login, and Werkzeug

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/q-developer-microblog.git
   cd q-developer-quiz
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install flask flask-sqlalchemy flask-login werkzeug psycopg2
   ```

4. Set up the PostgreSQL database:
   - Create a new PostgreSQL database
   - Update the `SQLALCHEMY_DATABASE_URI` in `app.py` with your database credentials

5. Set the environment variables:
   ```
   export SECRET_KEY=your-secret-key
   export DATABASE_URL=postgresql://username:password@localhost/database_name
   ```

## Running the Application

1. Initialize the database:
   ```
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Open a web browser and navigate to `http://localhost:5000`

## Usage

1. Register a new account or log in if you already have one
2. Login with that account
3. Write posts
4. Favorite posts
5. View other people and your favourited posts

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)