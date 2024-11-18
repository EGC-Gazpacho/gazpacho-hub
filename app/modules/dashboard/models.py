from app import db


class Dashboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_count = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Dashboard<{self.id}, Dataset Count={self.dataset_count}>'
