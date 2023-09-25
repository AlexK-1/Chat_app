from werkzeug.security import generate_password_hash as hash_, check_password_hash

import sqlite3


class DataBaseManager:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.cur = self.conn.cursor()

    def user_create(self, username: str, password: str, email: str):
        self.cur.execute("INSERT INTO Users (username, password, email) VALUES (?, ?, ?)",
                         (username, hash_(password), email))
        return self.conn.commit()

    def user_exists(self, username: str, password: str = False):
        if password != False:
            result = self.cur.execute("SELECT id FROM Users WHERE username = ? AND password = ?",
                                      (username, hash_(password)))
        else:
            result = self.cur.execute("SELECT id FROM Users WHERE username = ?", (username,))
        return bool(len(result.fetchall()))

    def user_get_info(self, param: dict, returns: str, get_one: bool = True):
        try:
            result = self.cur.execute(f"SELECT {returns} FROM Users WHERE {list(param.keys())[0]} = ?",
                                      (list(param.values())[0],))
            result = result.fetchone()
            if result:
                if get_one:
                    try:
                        return result[0]
                    except TypeError:
                        return result
                else:
                    return result
            else:
                print(f"No user witch {list(param.keys())[0]} {list(param.values())[0]}")
                return False
        except sqlite3.Error as e:
            print(f"Error: {e}")
        return False

    def user_get_by_id(self, user_id: int):
        return self.user_get_info({"id": user_id}, "*", False)

    def post_create(self, poster: str, text: str):
        self.conn.execute("INSERT INTO Posts (poster, text) VALUES (?, ?)", (poster, text))
        return self.conn.commit()

    def posts_by_user(self, user: str):
        result = self.cur.execute("SELECT * FROM Posts WHERE poster = ?", (user,))
        return result.fetchall()

    def posts_all(self, last: int):
        result = self.cur.execute("SELECT * FROM Posts LIMIT 10 OFFSET (SELECT count(*) FROM Posts)-?", (last,))
        return result.fetchall()

    def close(self):
        self.conn.close()

db = DataBaseManager("Chat.db")

db.close()