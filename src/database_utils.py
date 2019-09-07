import pymongo
import pathlib
import sqlite3
import os
from getpass import getpass
from dataclasses import dataclass
import json

from core_utils import is_invalid_email, random_salt, secure_hash, console_input

home_dir = str(pathlib.Path.home())

if not os.path.exists(home_dir + "/.corem"):
    os.makedirs(home_dir + "/.corem", 0o755)

conn = sqlite3.connect(home_dir + "/.corem/crator.db")


@dataclass
class AccountStructure:
    name: str
    mail: str
    security_key: str
    salt: str


class AccountManager:
    """ 
        Managing account locally and with remote service
    """

    def __init__(self, connection):
        self.is_authorized = False
        self._conn = connection
        self._cursor = connection.cursor()
        self._cursor.execute(
            """
        
        CREATE TABLE IF NOT EXISTS ACCOUNTS (
         MAIL           TEXT  PRIMARY KEY   NOT NULL,
         NAME           TEXT                NOT NULL,
         SECURITYKEY      TEXT                NOT NULL,
         SALT           TEXT                NOT NULL);

         """
        )

        self._conn.commit()

    def new_account(self):
        """
            Creates new accounts
        """
        mail = input("Enter your email: ").strip()
        name = input("Enter your name: ").strip()
        pass_phrase = getpass("Enter password: ").strip()
        cpass = getpass("Confirm password: ").strip()

        if cpass != pass_phrase:
            print("[!] Passwords do not match!!")
            return

        if (not name) or (not mail) or (not pass_phrase):
            print("[!] Name, mail & password are mandatory.")
            return

        if is_invalid_email(mail):
            print("[!] Unsupported email format")
            return

        salt = random_salt()
        secure_key = secure_hash(pass_phrase, salt)

        self._cursor.execute(
            """
            INSERT INTO ACCOUNTS(mail, name, securitykey, salt)
            VALUES(?, ?, ?, ?); """,
            (mail, name, secure_key, salt),
        )

        self._conn.commit()

        self.account_data = AccountStructure(name, mail, secure_key, salt)

    def publish_account(self):
        pass

    def update_account(self):

        """ 
            User can update name & password.
            Mail id is freezed.
        """

        if not self.is_authorized:
            print("[!] Please login first!")
            return

        name = input("Enter your name: ").strip()
        pass_phrase = getpass("Enter password: ").strip()
        cpass = getpass("Confirm password: ").strip()

        if cpass != pass_phrase:
            print("[!] Passwords do not match.")
            return

        if (not name) or (not cpass):
            print("[!] Name and passwords are mandatory")
            return

        salt = random_salt()
        secure_key = secure_hash(pass_phrase, salt)
        self._cursor.execute(
            """UPDATE ACCOUNTS SET name = ?, securitykey = ?, salt = ? WHERE mail = ? """,
            (name, secure_key, salt, self.account_data.mail),
        )

        self._conn.commit()

    def delete_account(self):
        """
            Deletes user account
        """

        if not self.is_authorized:
            print("[!] Please login first!")
            return

        self._cursor.execute(
            """DELETE FROM ACCOUNTSWHERE mail = ? """, (self.account_data.mail,)
        )

        self._conn.commit()

    def login(self):
        """
            Logs user in and maintains session
        """
        try:
            with open(home_dir + "/.corem/session.data", "r") as f:
                data = json.load(f)
            if data["session-type"] == "local":
                user = self._cursor.execute(
                    "Select * from ACCOUNTS WHERE mail = ?", (data["session-id"],)
                ).fetchone()
                if data["session-key"] == secure_hash(data["session-id"], user[1]):
                    self.account_data = AccountStructure(
                        user[0], user[1], user[2], user[3]
                    )
                    self.is_authorized = True
                    return data["session-id"]
        except:
            print("No local or remote session found, falling back to login mode.")

        mail = input("Enter email: ").strip()
        password = getpass("Enter passphrase: ").strip()

        if (not mail) or (not password):
            print("[!] email and password is required.")
            return None

        user = self._cursor.execute(
            "Select * from ACCOUNTS WHERE mail = ?", (mail,)
        ).fetchone()
        if user[2] == secure_hash(password, user[3]):
            data = {
                "session-type": "local",
                "session-id": mail,
                "session-key": secure_hash(mail, user[1]),
            }
            with open(home_dir + "/.corem/session.data", "w") as f:
                json.dump(data, f)

            self.account_data = AccountStructure(user[0], user[1], user[2], user[3])
            self.is_authorized = True
            return mail
        else:
            print("[!] Invalid credentials.")
            return None

    def sign_out(self):
        """
            Sign out user and clear session data
        """
        self.is_authorized = False
        os.remove(home_dir + "/.corem/session.data")
        del self.account_data
        exit(0)


@dataclass
class ProjectStructure:
    key: int
    name: str
    category: str
    tags: str
    description: str
    start: str
    end: str
    author: str


class ProjectManager:
    """
        Project class manages project and consist of properties:- 
            project name, 
            category, 
            tags, 
            description,  
            start & end date. 
        
        Detailed-docs can also be added allowing .md and .html and .pdf descriptions.
    """

    def __init__(self, connection, author):
        self.author = author
        self._conn = connection
        self._cursor = connection.cursor()
        self._cursor.execute(
            """
        
        CREATE TABLE IF NOT EXISTS PROJECTS (
         ID            INTEGER AUTOINCREMENT  PRIMARY KEY    NOT NULL,
         NAME           TEXT                        NOT NULL,
         CATEGORY       TEXT                        NOT NULL,
         TAGS           TEXT                        NOT NULL,
         DESCRIPTION    TEXT                        NOT NULL,
         START          TEXT                        NOT NULL,
         END            TEXT                        NOT NULL,
         CREATED_BY      TEXT                        NOT NULL
         );

         """
        )

        self._conn.commit()

    def project_summary(self):
        pass

    def select_project(self):
        print("Select Project: ")
        i = 0
        for row in self._cursor.execute("Select * from Projects;"):
            print("{}. {} - {}".format(row[0], row[1], row[4]))
            i += 1

        x = input("Enter Project id: ").strip()
        if not x or int(x) > i:
            return

        print("Project with id: {} selected.".format(x))
        return int(x)


    def new_project(self):
        # TODO : Add files support
        name = input("Enter project name: ").strip()
        category = input("Enter project category: ").strip()
        tags = input("Enter tags separated by comma(,): ").strip()
        description = input("Enter project description: ").strip()
        start = input("Enter start date (as dd-mm-yyyy): ").strip()
        end = input(
            "Enter end date (as dd-mm-yyyy) (use -1 for leaving blank): "
        ).strip()

        if (
            (not name)
            or (not category)
            or (not tags)
            or (not description)
            or (not start)
            or (not end)
        ):
            print("[!] Insufficient fields!!")
            return None

        self._cursor.execute(
            """
            INSERT INTO PROJECTS(name, category, tags, description, start, end, created_by)
            VALUES(?, ?, ?, ?, ?, ?, ?); """,
            (name, category, tags, description, start, end, self.author),
        )

        project_data = ProjectStructure(
            self._cursor.lastrowid,
            name,
            category,
            tags,
            description,
            start,
            end,
            self.author,
        )

        self._conn.commit()
        return project_data

    def add_files(self):
        pass

    def delete_project(self):
        print("Select Project to delete: ")
        i = 0

        for row in self._cursor.execute("Select * from Projects;"):
            print("{}. {} - {}".format(row[0], row[1], row[4]))
            i += 1

        x = input("Enter Project No to delete: ").strip()
        if not x or int(x) > i:
            return

        conf = input(
            "Are you sure you want to delete the project? (All related tasks will also be deleted) y/N:"
        ).strip()

        if conf != "y" or conf != "yes":
            return

        self._cursor.execute("DELETE FROM PROJECTS WHERE id=? ;", x)
        self._cursor.execute("DELETE FROM TASKS WHERE project_id=? ;", x)
        self._cursor.execute("DELETE FROM INTERNALS WHERE project_id=? ;", x)
        self._cursor.execute("DELETE FROM EXTERNALS WHERE project_id=? ;", x)
        # self._cursor.execute("DELETE FROM REMINDERS WHERE id=? ;", x)

        self._conn.commit()

    def update_project(self):
        """
            Allow updating project details
        """

        print("Select Project to update: ")
        i = 0
        print("ID. NAME  -  DESCRIPTION")
        for row in self._cursor.execute("Select * from Projects;"):
            print("{}. {} - {}".format(row[0], row[1], row[4]))
            i += 1

        x = input("Enter Project id to update: ").strip()

        if (not x) or int(x) > i:
            return

        project = self._cursor("Select * from Projects where id=?", x).fetchone()
        project_data = ProjectStructure(
            project[0],
            project[1],
            project[2],
            project[3],
            project[4],
            project[5],
            project[6],
            project[7],
        )
        name = input("Enter project's new name: ").strip()
        category = input("Enter project category: ").strip()
        tags = input("Enter tags separated by comma(,): ").strip()
        description = input("Enter project description: ").strip()
        start = input("Enter start date (as dd-mm-yyyy): ").strip()
        end = input(
            "Enter end date (as dd-mm-yyyy) (use -1 for leaving blank): "
        ).strip()

        if not name:
            name = project_data.name

        if not category:
            category = project_data.category

        if not tags:
            tags = project_data.tags

        if not description:
            description = project_data.description

        if not start:
            start = project_data.start

        if not end:
            end = project_data.end

        self._cursor.execute(
            """UPDATE PROJECTS SET name = ?, category = ?, tags = ?, description = ?, start = ?, end = ? WHERE id = ? """,
            (name, category, tags, description, start, end, x),
        )

        self._conn.commit()


@dataclass
class TaskStructure:
    key: int
    priority: str
    objective: str
    description: str
    start: str
    end: str
    status: str
    status_info: str
    dependent_on: str
    project_id: str


@dataclass
class TaskLogStructure:
    key: int
    status: str
    status_info: str
    task_id: int
    created_by: str


class TaskManager:
    """
        A Task is an activity which needs to be completed. 
        A task has:
            - task-id
            - priority
            - objective
            - description
            - start date
            - end date
            - status
            - status description
            - dependence on task
            - project_id
    """

    def __init__(self, connection, author, project):
        self.project_data = project
        self.author = author
        self._conn = connection
        self._cursor = connection.cursor()
        self._cursor.execute(
            """
        
        CREATE TABLE IF NOT EXISTS TASKS (
         ID            INTEGER AUTOINCREMENT  PRIMARY KEY    NOT NULL,
         PRIORITY       TEXT                        NOT NULL,
         OBJECTIVE      TEXT                        NOT NULL,
         DESCRIPTION    TEXT                        NOT NULL,
         START          TEXT                        NOT NULL,
         END            TEXT                        NOT NULL,
         STATUS         TEXT                        NOT NULL,
         STATUS_INFO    TEXT                        NOT NULL, 
         DEPENDENT_ON   TEXT                        NOT NULL,
         PROJECT_ID     INTEGER                     NOT NULL,       
         CREATED_BY      TEXT                        NOT NULL
         );


        CREATE TABLE IF NOT EXISTS TASKLOGS (
         ID            INTEGER AUTOINCREMENT  PRIMARY KEY    NOT NULL,
         STATUS         TEXT                        NOT NULL,
         STATUS_INFO    TEXT                        NOT NULL,
         TASK_ID        INTEGER                        NOT NULL,       
         CREATED_BY     TEXT                        NOT NULL
         );
         """
        )

        self._conn.commit()

    def add_task(self):
        """ 
            Add task to projects
        """

        statements = [
            "Enter task priority(0 for low, 1 for mid, 2 for high): ",
            "Enter task objective: ",
            "Enter task description: ",
            "Enter start date: ",
            "Enter end date (-1 for unknown) : ",
            "Enter current status: ",
            "Enter status description"
            "Enter task_id(s) separated by comma(,) if task depends on other tasks (-1 in any-other case): ",
        ]

        fields = console_input(statements)

        if (
            (not fields[0])
            or (not fields[1])
            or (not fields[3])
            or (not fields[5])
            or (not fields[6])
            or (not fields[7])
        ):
            print(
                "[!] Please provide priority, objective, start date, current status & status description & dependent tasks."
            )
            return None

        self._cursor.execute(
            """ 
             INSERT INTO TASKS(priority, objective, description, start, end, status, status_info,dependent_on, project_id, created_by)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?); """,
            (
                fields[0],
                fields[1],
                fields[2],
                fields[3],
                fields[4],
                fields[5],
                fields[6],
                fields[7],
                self.project_data.key,
                self.author,
            ),
        )

        self.task = TaskStructure(
            self._cursor.lastrowid,
            fields[0],
            fields[1],
            fields[2],
            fields[3],
            fields[4],
            fields[5],
            fields[6],
            fields[7],
            self.project_data.key,
            self.author,
        )

        self._conn.commit()

    def add_task_log(self):
        statements = ["Enter current status: ", "Enter status description"]
        fields = console_input(statements)

        if (not fields[0]) or (not fields[1]):
            print("[!] Please provide status and status description.")
            return None

        self._cursor.execute(
            """
            INSERT INTO TASKLOGS (status, status_info, task_id, created_by)
            VALUES(?, ?, ?, ?);
         """,
            (fields[0], fields[1], self.task.key, self.author),
        )

        self._cursor.execute(
            """UPDATE TASKS SET status = ?, status_info = ? WHERE id = ? ;""",
            (fields[0], fields[1], self.task.key),
        )

        self._conn.commit()

    def add_reminder(self):
        # Beta feature:- uses daemon to show desktop notification.
        pass

    def delete_task(self):
        """
            Delete task and related logs
        """

        self._cursor.execute(""" DELETE FROM TASKS WHERE id=? ;""", (self.task.key,))
        self._cursor.execute(
            """ DELETE FROM TASKLOGS WHERE task_id = ?;""", (self.task.key,)
        )
        self._conn.commit()

    def update_task(self):
        """
            Update certain data about tasks 
        """
        statements = [
            "Enter task priority(0 for low, 1 for mid, 2 for high): ",
            "Enter end date (-1 for unknown) : ",
            "Enter task_id(s) separated by comma(,) if task depends on other tasks (-1 in any-other case): ",
        ]

        fields = console_input(statements)

        if (not fields[0]) or (not fields[1]) or (not fields[2]):
            print("[!] Please provide priority, end date, & dependent tasks.")
            return None

        self._cursor.execute(
            """ 
             UPDATE TASKS set priority=?, end=?, dependent_on=? Where id=?
            VALUES(?, ?, ?, ?); """,
            (fields[0], fields[1], fields[2], self.task.key),
        )

        self._conn.commit()

        self.task.priority = fields[0]
        self.task.end = fields[1]
        self.task.dependent_on = fields[2]


@dataclass
class InternalsStructure:
    key: int
    name: str
    email: str
    phone: int
    task_id: str
    project_id: str


class Internals:

    """
        Adding users to project (or task) or revoking access
    """

    def __init__(self, project_id, author, connection):
        self.project_id = project_id
        self.author = author
        self._conn = connection
        self._cursor = connection.cursor()
        self._cursor.execute(
            """
        
        CREATE TABLE IF NOT EXISTS INTERNALS (
         ID       INTEGER  AUTOINCREMENT  PRIMARY KEY    NOT NULL,
         NAME      TEXT                                  NOT NULL,
         EMAIL     TEXT                                  NOT NULL,
         PHONE    INTEGER                                        ,
         TASK_ID  INTEGER                                        ,
         PROJECT_ID INTEGER                              NOT NULL,
        );
        
        """
        )

        self._conn.commit()

    def add(self):
        statements = [
            "Enter contact name: ",
            "Enter contact email: ",
            "Enter contact phone number: ",
            "Enter task id (optional): ",
            "Enter project_id: ",
        ]

        fields = console_input(statements)

        if (not fields[0]) or (not fields[1]) or (not fields[2]) or (not fields[4]):
            print("[!] Please provide neccessary details")
            return None

        self._cursor.execute(
            """ 
            INSERT into INTERNALS (name, email, phone, task_id, project_id)
            VALUES (?, ?, ?, ?, ?);
        """,
            (fields[0], fields[1], fields[2], fields[3], fields[4]),
        )

        self._conn.commit()

        self.internal = InternalsStructure(
            self._cursor.lastrowid,
            fields[0],
            fields[1],
            fields[2],
            fields[3],
            fields[4],
        )

    def revoke(self):
        self._cursor.execute(
            """ DELETE FROM INTERNALS WHERE id=?;""", (self.internal.key)
        )
        self._conn.commit()


@dataclass
class ExternalsStructure:
    key: int
    name: str
    email: str
    phone: int
    project_id: str


class Externals:
    """    
        Manage external contacts to a project (indirect contributors to the project.)
    """

    def __init__(self, project_id, author, connection):
        self.project_id = project_id
        self.author = author
        self._conn = connection
        self._cursor = connection.cursor()
        self._cursor.execute(
            """
        
        CREATE TABLE IF NOT EXISTS EXTERNALS (
         ID       INTEGER  AUTOINCREMENT  PRIMARY KEY    NOT NULL,
         NAME      TEXT                                  NOT NULL,
         EMAIL     TEXT                                  NOT NULL,
         PHONE    INTEGER                                        ,
         PROJECT_ID INTEGER                              NOT NULL,
        );
        
        """
        )

        self._conn.commit()

    def make_contact(self):
        # TODO: Add mailing service here
        pass

    def add_external(self):
        statements = [
            "Enter contact name: ",
            "Enter contact email: ",
            "Enter contact phone number: ",
            "Enter project_id: ",
        ]

        fields = console_input(statements)

        if (not fields[0]) or (not fields[1]) or (not fields[2]) or (not fields[3]):
            print("[!] Please provide neccessary details")
            return None

        self._cursor.execute(
            """ 
            INSERT into EXTERNALS (name, email, phone, project_id)
            VALUES (?, ?, ?, ?);
        """,
            (fields[0], fields[1], fields[2], fields[3]),
        )

        self._conn.commit()

        self.external = InternalsStructure(
            self._cursor.lastrowid, fields[0], fields[1], fields[2], fields[3]
        )

    def revoke_access(self):
        self._cursor.execute(
            """ DELETE FROM EXTERNALS WHERE id=?;""", (self.external.key)
        )
        self._conn.commit()


# Unknown why this class was created ??
class Review:
    pass
