from database_utils import (
    home_dir,
    AccountManager,
    ProjectManager,
    TaskManager,
    Internals,
    Externals,
    ProjectStructure,
    AccountStructure,
    TaskLogStructure,
    TaskStructure,
    ExternalsStructure,
    InternalsStructure,
)

import sqlite3

conn = sqlite3.connect(home_dir + "/.corem/crator.db")


def project_interface(projem, project_id, author):
    while True:
        print(
            """ 
            Select action:
                1. Start Task Manager
                2. Update Project
                3. Delete Project
                4. Start Externals Manager
                5. Exit
        """
        )
        ch = input("Enter action code: ").strip()

        if ch == "2":
            projem.update_project(project_id)
        elif ch == "3":
            projem.delete_project(project_id)
        elif ch == "4":
            external_contacts_interface(author, project_id)
        elif ch != "1":
            break
        else:
            task_interface(conn, author, project_id)


def task_interface(conn, author, project_id):
    taskm = TaskManager(conn, author, project_id)
    while True:
        print(
            """ 
            1. Add task
            2. Add task log
            3. Update task
            4. Delete task
            5. Add Internals
        """
        )
        ch = input("Enter action code: ").strip()

        if ch == "2":
            taskm.add_task_log()
        elif ch == "3":
            taskm.update_task()
        elif ch == "4":
            taskm.delete_task()
        elif ch == "5":
            internal_contacts_interface(project_id, author)
        elif ch != "1":
            break
        else:
            taskm.add_task()
    del taskm


def internal_contacts_interface(project_id, author):
    intm = Internals(project_id, author, conn)
    while True:
        print(
            """ 
            1. Add Internal
            2. Revoke Access
            3. Return
        """
        )
        ch = input(">> ").strip()

        if ch == "1":
            intm.add()
        elif ch == "2":
            intm.revoke()
        else:
            break

    del intm


def external_contacts_interface(author, project_id):
    extm = Externals(conn, author, project_id)
    while True:
        print(
            """ 
            1. Add External
            2. Revoke Access
            3. Return
        """
        )
        ch = input(">> ").strip()

        if ch == "1":
            extm.add_external()
        elif ch == "2":
            extm.revoke_access()
        else:
            break
    del extm


def abort():
    conn.close()
    exit(1)


if __name__ == "__main__":
    conn = sqlite3.connect(home_dir + "/.corem/crator.db")

    ax = AccountManager(conn)
    xs = input("Enter any character for new account or press return to login: ").strip()
    if xs:
        print("\n\tRegistration Portal\n")
        ax.new_account()
    print("\nLogin Portal\n")
    author = ax.login()

    if not author:
        print("oh crap")
        abort()

    print("[*] Logged in as {}".format(author))

    projem = ProjectManager(conn, author)

    ch = input("Choose 1 for new Project or 2 to set project: ").strip()

    if ch == "1":
        project_data = projem.new_project()
    elif ch != "2":
        print("[!] Unknown choice. Exiting...")
        abort()

    project_id = projem.select_project()

    if not project_id:
        print("[!] No selected project. Exiting...")
        abort()

    project_interface(projem, project_id, author)

    ax.sign_out()
    conn.close()
    exit(0)
