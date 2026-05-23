import user_storage_sql as uss
from user_interface import Bcolors, clear_screen
import movie_storage as ms

CURRENT_USER_ID = -1
CURRENT_USERNAME = ""

def command_create_new_user() -> tuple:
    """
    Asks the user to create a new user profile by providing a username and email address.
    It will then create a new user profile in the database and return the username and
    user_id of the created user.
    :return: username and user_id of the created user
    """
    username = input("Enter your username: ")
    email_address = input("Enter your email address: ")
    user_id = uss.add_user(username, email_address)
    if user_id != -1:
        print(
            Bcolors.LISTING
            + f"User profile for {username} created successfully."
            + Bcolors.ENDC
        )
        return user_id, username
    print(
        Bcolors.WARNING
        + f"Failed to create user profile for {username}. Exiting function."
        + Bcolors.ENDC
    )
    return -1, ""


def command_update_user_profile():
    """
    updates the user profile in the database by asking for the username and email address
    :return:
    """
    global CURRENT_USERNAME
    clear_screen()
    command_list_users()
    selected_user_id = input(
        "Enter the ID of the user you want to update or press ENTER to abort: "
    )
    if selected_user_id == "":
        print(Bcolors.WARNING + "User profile update aborted." + Bcolors.ENDC)
        return
    try:
        selected_user_id = int(selected_user_id)
        users = uss.list_users()
        for user in users:
            if user[0] == selected_user_id:
                orig_username = user[1]
                orig_email_address = user[2]
                break
        else:
            print(
                Bcolors.WARNING
                + "Invalid user ID provided. User profile update aborted."
                + Bcolors.ENDC
            )
            return
    except (ValueError, TypeError):
        print(
            Bcolors.WARNING
            + "Invalid input provided. User profile update aborted."
            + Bcolors.ENDC
        )
        return
    username = input(f"Enter a new username (was {orig_username}): ")
    if username == "":
        username = orig_username
        print(Bcolors.LISTING + f"Using original username: {username}" + Bcolors.ENDC)
    email_address = input(
        Bcolors.INPUT_TEXT
        + f"Enter a new email address (was {orig_email_address}): "
        + Bcolors.ENDC
    )
    if email_address == "":
        email_address = orig_email_address
        print(
            Bcolors.LISTING
            + f"Using original email address: {email_address}"
            + Bcolors.ENDC
        )
    if uss.update_user_profile(selected_user_id, username, email_address):
        print(
            Bcolors.LISTING
            + f"User profile for {username} updated successfully for user {selected_user_id}."
            + Bcolors.ENDC
        )
        if CURRENT_USER_ID == selected_user_id:
            CURRENT_USERNAME = username
    else:
        print(
            Bcolors.WARNING
            + f"Failed to update user profile for {CURRENT_USER_ID}."
            + Bcolors.ENDC
        )


def command_select_user() -> tuple:
    """
    Asks the user to select a user profile from the database. Returns the user_id of
    the selected user.
    If no users are available, it will ask to create a new user profile.

    if users are available, it will show the list of users and ask to select one
    by providing the user_id.
    if the user provides an invalid user_id, it will ask again until a valid
    user_id is provided or the user presses ENTER to abort.
    if the user presses ENTER to abort, it will return None.
    If the user selects to create a new user profile, it will ask for the
    username and email address and create a new user profile in the database.

    :return: user_id of the selected user or None if no user is selected
    """
    global CURRENT_USER_ID, CURRENT_USERNAME
    users = uss.list_users()
    if not users:
        print(
            Bcolors.WARNING
            + "No users found in the database. Please create a new user profile."
            + Bcolors.ENDC
        )
        user_id, username = command_create_new_user()
        if user_id != -1:
            print(
                Bcolors.LISTING
                + f"User profile for {username} created successfully."
                + Bcolors.ENDC
            )
            return user_id, username
        print(
            Bcolors.WARNING
            + f"Failed to create user profile for {username}. Exiting application."
            + Bcolors.ENDC
        )
        return -1, ""
    print(Bcolors.LISTING + "Available users:" + Bcolors.ENDC)
    for user in users:
        print(
            Bcolors.LISTING + f"{user[0]} - {user[1]}: ({user[2]})" + Bcolors.ENDC
        )
    while True:
        try:
            selected_user_id = input(
                "Enter the ID of the user you want to select or type "
                "'new' to create a new profile: "
            )
            if selected_user_id.lower() == "new":
                user_id, username = command_create_new_user()
                return user_id, username
            selected_user_id = int(selected_user_id)
            for user in users:
                if user[0] == selected_user_id:
                    CURRENT_USER_ID = selected_user_id
                    CURRENT_USERNAME = user[1]
                    return selected_user_id, user[1]
            print(
                Bcolors.WARNING
                + "Invalid user ID. Please try again."
                + Bcolors.ENDC
            )
        except (ValueError, TypeError):
            print(
                Bcolors.WARNING
                + "Please enter a valid integer for the user ID."
                + Bcolors.ENDC
            )


def command_list_users():
    """
    Lists all the users in the database by showing their user_id, username and email address.
    :return:
    """
    users = uss.list_users()
    if not users:
        print(Bcolors.WARNING + "No users found in the database." + Bcolors.ENDC)
    else:
        print(Bcolors.LISTING + "Available users:" + Bcolors.ENDC)
        for user in users:
            print(
                Bcolors.LISTING + f"{user[0]} - {user[1]}: ({user[2]})" + Bcolors.ENDC
            )


def command_delete_user():
    """
    Deletes a user profile from the database by asking for the user_id of
    the user to delete. It will then delete the user profile and all the
    movies associated with that user from the database.
    :return:
    """

    def delete_all_movies_of_user(user_id: int):
        movies = ms.fetch_movies(user_id)
        for movie in movies:
            ms.delete_movie(movie[0], movie[2], user_id)

    global CURRENT_USER_ID, CURRENT_USERNAME
    users = uss.list_users()
    if not users:
        print(Bcolors.WARNING + "No users found in the database." + Bcolors.ENDC)
        return
    print(Bcolors.LISTING + "Available users:" + Bcolors.ENDC)
    for user in users:
        print(Bcolors.LISTING + f"{user[0]} - {user[1]}: ({user[2]})" + Bcolors.ENDC)
    while True:
        try:
            selected_user_id = input(
                Bcolors.INPUT_TEXT
                + "Enter the ID of the user you want to delete or press ENTER to abort: "
                + Bcolors.ENDC
            )
            if selected_user_id == "":
                print(Bcolors.WARNING + "User deletion aborted." + Bcolors.ENDC)
                return
            selected_user_id = int(selected_user_id)
            for user in users:
                if user[0] == selected_user_id:
                    if uss.delete_user(selected_user_id):
                        delete_all_movies_of_user(selected_user_id)
                        print(
                            Bcolors.LISTING
                            + f"User {user[1]} and all associated movies deleted successfully."
                            + Bcolors.ENDC
                        )
                        if CURRENT_USER_ID == selected_user_id:
                            CURRENT_USER_ID = -1
                            CURRENT_USERNAME = ""
                            command_select_user()
                        print(
                            Bcolors.LISTING
                            + f"User {user[1]} deleted successfully."
                            + Bcolors.ENDC
                        )
                    else:
                        print(
                            Bcolors.WARNING
                            + f"Failed to delete user {user[1]}."
                            + Bcolors.ENDC
                        )
                    return
            print(Bcolors.WARNING + "Invalid user ID. Please try again." + Bcolors.ENDC)
        except (ValueError, TypeError):
            print(
                Bcolors.WARNING
                + "Please enter a valid integer for the user ID."
                + Bcolors.ENDC
            )

def get_current_user() -> tuple:
    """
    Returns the current user profile:
    - the user_id of the current user
    - the username of the current user
    """
    return CURRENT_USER_ID, CURRENT_USERNAME

def get_current_userid() -> int:
    """
    Returns the current user profile:
    - the user_id of the current user
    """
    return CURRENT_USER_ID
