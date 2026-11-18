from teamup.extensions import db

# Una persona tiene muchas habilidades y una habilidad la tienen muchas personas
user_skills = db.Table(
    "user_skills",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    db.Column("skill_id", db.Integer, db.ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)


class Skill(db.Model):
    """Una habilidad del perfil, como "Edición de video" o "Python"."""
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)

    @classmethod
    def from_names(cls, names):
        """Las habilidades con esos nombres; las que no existen se crean. Sin importar mayúsculas."""
        skills = []
        for name in names:
            skill = cls.query.filter(db.func.lower(cls.name) == name.lower()).first()
            if skill is None:
                skill = cls(name=name)
                db.session.add(skill)
            if skill not in skills:
                skills.append(skill)
        return skills
