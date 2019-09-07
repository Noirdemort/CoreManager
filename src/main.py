from database_utils import conn, Account

if __name__ == "__main__":
    ax = Account(conn)
    ax.new_account()
    z = ax.login()
    if not z:
        print("oh crap")
        exit(1)

    print("[*] Logged in as {}".format(z))

    ax.sign_out()
    conn.close()
