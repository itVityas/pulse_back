from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModelOnlyId


class MatrixType(BaseModelOnlyId):
    """Модель для предоставления типа матрицы телевизора: id, name
    """
    __tablename__ = "matrix_type"
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    tv_matrix_type = relationship('TV', back_populates='matrix_type', cascade='all, delete-orphan')

    def __str__(self):
        return f'<matrix>: {self.id} {self.name}'
