from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class BarModel(Base):
    __tablename__ = "bars"

    symbol: Mapped[str] = mapped_column(String, nullable=False)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    timeframe: Mapped[str] = mapped_column(String, nullable=False)

    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("symbol", "ts", "timeframe", name="pk_bars"),
    )