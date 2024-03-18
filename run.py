# Importing the 'app' object from the module 'Voting_System'.
from Voting_System import app

if __name__ == "__main__":
    # Running the Flask application represented by the 'app' object in debug mode,
    # which provides helpful debugging information on errors.
    # The application is set to run on port 5001.
    app.run(debug=True,port=5001)
