#!/usr/bin/env python3
"""
Script to initialize the permission system.
This script creates all system permissions and roles, and assigns default permissions to roles.
"""


def main():
    """Main function - this script is meant to be run from the backend directory"""
    print(
        "To initialize the permission system, run the following command from the backend directory:"
    )
    print("  python -m app.utils.init_db")
    print("")
    print(
        "This will create all system permissions and roles, and set up default users."
    )


if __name__ == "__main__":
    main()
