from flask_login import UserMixin

from db_manager import DataBaseManager


class User(UserMixin):
    def get_user(self, user_id: int, db: DataBaseManager):
        self.user_ = db.user_get_by_id(user_id)
        return self

    def create(self, user):
        self.user_ = user
        return self

    def get_id(self):
        return int(self.user_[0])

    def get_username(self):
        return str(self.user_[1])
