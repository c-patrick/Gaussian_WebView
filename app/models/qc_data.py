from app.extensions import db
from sqlalchemy import Integer, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal


class QC_data(db.Model):
    __tablename__ = "data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    qc_name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    HOMO: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    LUMO: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    Eg: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    Energy: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    Dipole: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    Quadrupole: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    def __repr__(self) -> str:
        return f"QC_data(id={self.id!r}, qc_name={self.qc_name!r})"
