from werkzeug.security import generate_password_hash as hash_, check_password_hash

import sqlite3
from ast import literal_eval


class DataBaseManager:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.cur = self.conn.cursor()

    def user_create(self, username: str, password: str, email: str = ""):
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

    def users_all(self, s: str = False, except_: list = False):
        if s == False:
            if except_ == False:
                result = self.cur.execute(f"SELECT username FROM Users WHERE banned = 'no'")
            else:
                b = [f"'{i}'" for i in except_]
                result = self.cur.execute(
                    f"SELECT username FROM Users WHERE banned = 'no' AND NOT username IN ({','.join(b)})")
        else:
            if except_ == False:
                result = self.cur.execute(f"SELECT username FROM Users WHERE banned = 'no' AND username LIKE '%{s}%'")
            else:
                b = [f"'{i}'" for i in except_]
                result = self.cur.execute(
                    f"SELECT username FROM Users WHERE banned = 'no' AND username LIKE '%{s}%' AND NOT username IN ({','.join(b)})")
        return result.fetchall()

    def post_create(self, poster: str, text: str, room_id: int) -> int:
        self.cur.execute("INSERT INTO Posts (poster, text, room_id) VALUES (?, ?, ?)", (poster, text, room_id))
        post_id = self.cur.lastrowid
        print(post_id)
        self.conn.commit()
        return post_id

    def posts_by_user(self, user: str):
        result = self.cur.execute("SELECT * FROM Posts WHERE poster = ?", (user,))
        return result.fetchall()

    def posts_all(self, last: int, room_id: int):
        if room_id == 0:
            result = self.cur.execute("SELECT * FROM Posts LIMIT 10 OFFSET (SELECT count(*) FROM Posts)-?", (last,))
        else:
            result = self.cur.execute(
                "SELECT * FROM Posts WHERE room_id = ? LIMIT 10 OFFSET (SELECT count(*) FROM Posts)-?", (room_id, last))
        return result.fetchall()

    def post_delete(self, post_id: int):
        self.cur.execute("DELETE FROM Posts WHERE id = ?", (post_id,))
        return self.conn.commit()

    def post_get_info(self, param: dict, returns: str, get_one: bool = True):
        try:
            result = self.cur.execute(f"SELECT {returns} FROM Posts WHERE {list(param.keys())[0]} = ?",
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
                print(f"No post witch {list(param.keys())[0]} {list(param.values())[0]}")
                return False
        except sqlite3.Error as e:
            print(f"Error: {e}")
        return False

    def post_exists(self, post_id: int):
        result = self.cur.execute("SELECT id FROM Posts WHERE id = ?", (post_id,))
        return bool(len(result.fetchall()))

    def room_get_info(self, param: dict, returns: str, get_one: bool = True):
        try:
            result = self.cur.execute(f"SELECT {returns} FROM Rooms WHERE {list(param.keys())[0]} = ?",
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
                print(f"No room witch {list(param.keys())[0]} {list(param.values())[0]}")
                return False
        except sqlite3.Error as e:
            print(f"Error: {e}")
        return False

    def rooms_user_in(self, username: str, room_type: str = False):
        if room_type == False:
            result = self.cur.execute(
                f"SELECT id, name, type FROM Rooms WHERE visibility IN ('*all', '*members') AND (members LIKE '%\"{username}%\"%' OR members = '*all')")
        else:
            result = self.cur.execute(
                f"SELECT id, name, type FROM Rooms WHERE visibility IN ('*all', '*members') AND (members LIKE '%\"{username}\"%' OR members = '*all') AND type = ?",
                (room_type,))
        return result.fetchall()

    def room_create(self, name: str, members: str, type_: str, visibility: str, owner: str, admins: str) -> int:
        self.cur.execute("INSERT INTO Rooms (name, members, type, visibility, owner, admins) VALUES (?, ?, ?, ?, ?, ?)",
                         (name, members, type_, visibility, owner, admins))
        room_id = self.cur.lastrowid
        self.conn.commit()
        return room_id

    def room_exists_by_id(self, room_id: int):
        result = self.cur.execute("SELECT id FROM Rooms WHERE id = ?", (room_id,))
        return bool(len(result.fetchall()))

    def room_delete(self, room_id: int):
        self.cur.execute("DELETE FROM Rooms WHERE id = ?", (room_id,))
        return self.conn.commit()

    def room_add_member(self, room_id: int, username: str):
        members = literal_eval(self.room_get_info({"id": room_id}, "members"))
        members.append(username)

        members_str = [f'"{i}"' for i in members]
        members_str = f'[{",".join(members_str)}]'

        self.cur.execute("UPDATE Rooms SET members = ? WHERE id = ?", (members_str, room_id))
        return self.conn.commit()

    def room_add_admin(self, room_id: int, username: str):
        admins = literal_eval(self.room_get_info({"id": room_id}, "admins"))
        admins.append(username)

        admins_str = [f'"{i}"' for i in admins]
        admins_str = f'[{",".join(admins_str)}]'

        self.cur.execute("UPDATE Rooms SET admins = ? WHERE id = ?", (admins_str, room_id))
        return self.conn.commit()

    def room_remove_member(self, room_id: int, username: str):
        a = self.room_get_info({"id": room_id}, "members, admins", False)
        members = literal_eval(a[0])
        admins = literal_eval(a[1])

        members.remove(username)

        members_str = [f'"{i}"' for i in members]
        members_str = f'[{",".join(members_str)}]'

        if username in admins:
            admins.remove(username)

        admins_str = [f'"{i}"' for i in admins]
        admins_str = f'[{",".join(admins_str)}]'

        self.cur.execute("UPDATE Rooms SET members = ?, admins = ? WHERE id = ?", (members_str, admins_str, room_id))
        return self.conn.commit()

    def room_remove_admin(self, room_id: int, username: str):
        admins = literal_eval(self.room_get_info({"id": room_id}, "admins"))
        admins.remove(username)

        admins_str = [f'"{i}"' for i in admins]
        admins_str = f'[{",".join(admins_str)}]'

        self.cur.execute("UPDATE Rooms SET admins = ? WHERE id = ?", (admins_str, room_id))
        return self.conn.commit()

    def room_user_is_admin(self, room_id: int, username: str):
        result = self.room_get_info({"id": room_id}, "admins")
        admins = literal_eval(result)
        return username in admins

    def chat_exists(self, first_user: str, second_user: str):
        result = self.cur.execute(
            f"SELECT id FROM Rooms WHERE type = 'chat' AND members IN ('[\"{first_user}\", \"{second_user}\"]', '[\"{second_user}\", \"{first_user}\"]')")
        return bool(len(result.fetchall()))

    def close(self):
        self.conn.close()


# db = DataBaseManager("Chat.db")

# db.room_remove_member(8, "other-user")

# print(db.room_get_info({"id": 8}, "*", False))

# db.close()
