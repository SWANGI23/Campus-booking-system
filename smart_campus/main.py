# main.py - run this file to start the Smart Campus Resource Booking System.
import database
import gui


def main():
    database.setup_database()     # creates campus.db and starting data on first run
    gui.SmartCampusApp()          # builds the window and starts the event loop


if __name__ == '__main__':
    main()
