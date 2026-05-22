from sqlalchemy import create_engine, text

# Define the database URL
DB_URL = "sqlite:///data/users.db"
DEBUG = True
# Create the engine
# engine = create_engine(DB_URL, echo=DEBUG)
engine = create_engine(DB_URL)


class BColors:
    """Utility class to represent colors on the terminal."""

    HEADER = "\033[95m"
    MENU_TEXT = "\033[94m"
    OKCYAN = "\033[96m"
    INPUT_TEXT = "\033[92m"
    WARNING = "\033[93m"
    BLINKING = "\033[5m"
    FAIL = "\033[91m"
    LISTING = "\033[0m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# Create the userss table if it does not exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email_address TEXT UNIQUENOT NULL
        )
    """))
    connection.commit()


def list_users():
    """Retrieve all users from the database."""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT user_id, username, email_address Poster FROM users")
        )
        users = result.fetchall()
    return users


def get_user_id_by_username(username):
    """Retrieve the user_id for a given username."""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT user_id FROM users WHERE username = :username"),
            {"username": username},
        )
        user_id = result.scalar()
        print(BColors.LISTING + f"User ID for username '{username}': {user_id}")
    return user_id


# pylint: disable=invalid-name
def add_user(username: str, email_address: str) -> int:
    """Add a user to the database."""
    with engine.connect() as conn:
        try:
            print(f"Inserting user {username} into the database")
            params = {"username": username, "email_address": email_address}

            conn.execute(
                text(
                    "INSERT INTO users (username, email_address) "
                    "VALUES (:username, :email_address)"
                ),
                params,
            )
            conn.commit()
            print(
                BColors.LISTING
                + f"user '{username}' added successfully."
                + BColors.ENDC
            )
            user_id = conn.execute(text("SELECT last_insert_rowid()")).scalar()
            print(BColors.LISTING + f"User ID: {user_id}" + BColors.ENDC)
            return user_id
        # Catch any exception that can occur results in users not stored.
        # pylint: disable=broad-exception-caught
        except Exception as e:
            print(
                BColors.FAIL + f"Error during storage of the users: {e}" + BColors.ENDC
            )
            return -1


def delete_user(user_id) -> bool:
    """Delete a user from the database."""
    with engine.connect() as conn:
        try:
            print(
                BColors.LISTING
                + f"Deleting user with ID {user_id} from the database"
                + BColors.ENDC
            )
            conn.execute(text("DELETE FROM users WHERE user_id = :id"), {"id": user_id})
            conn.commit()
            print(
                BColors.LISTING
                + f"user '{user_id}' deleted successfully."
                + BColors.ENDC
            )
        # Catch any exception that can occur results in users not stored.
        # pylint: disable=broad-exception-caught
        except Exception as e:
            print(BColors.FAIL + f"Error: {e}" + BColors.ENDC)
            return False
    return True


def update_user_profile(user_id, new_username, new_email_address) -> bool:
    """Update a users's rating in the database."""
    all_users = list_users()
    for user in all_users:
        if user[0] == new_username:
            user_id = user[0]
    with engine.connect() as conn:
        try:
            print(
                BColors.LISTING
                + f"updating users table {user_id} with ID {new_username} "
                + f"and {new_email_address} in the database"
                + BColors.ENDC
            )
            conn.execute(
                text(
                    "UPDATE users SET username = :username, email_address = :email_address WHERE user_id = :id"
                ),
                {
                    "id": user_id,
                    "username": new_username,
                    "email_address": new_email_address,
                },
            )
            conn.commit()
            print(
                BColors.LISTING
                + f"users '{user_id}' updated successfully."
                + BColors.ENDC
            )
        # Catch any exception that can occur results in users not stored.
        # pylint: disable=broad-exception-caught
        except Exception as e:
            print(f"Error: {e}")
            return False
    return True
