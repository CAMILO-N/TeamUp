from teamup.extensions import db


class Major(db.Model):
    __tablename__ = "majors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculties.id"), nullable=False)

    faculty = db.relationship("Faculty", back_populates="majors")

