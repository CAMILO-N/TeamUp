from teamup.extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)


# Catálogo inicial (lo carga el comando seed)
CATEGORIES = [
    "Cortometraje",
    "Startup",
    "Investigación",
    "Arte",
    "Evento",
    "Podcast",
    "Tecnología",
    "Otro",
]


def category_choices():
    """Opciones del selector de categoría, ordenadas por nombre."""
    return [(category.id, category.name) for category in Category.query.order_by(Category.name).all()]
