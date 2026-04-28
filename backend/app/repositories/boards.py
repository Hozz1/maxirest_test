from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.board import Board
from app.models.board_pin import BoardPin


class BoardRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, owner_id: UUID, title: str, description: str | None, is_public: bool) -> Board:
        board = Board(owner_id=owner_id, title=title, description=description, is_public=is_public)
        self.db.add(board)
        self.db.commit()
        self.db.refresh(board)
        return board

    def list_visible(self, owner_id: UUID | None = None, limit: int = 50) -> list[Board]:
        if owner_id is None:
            stmt = select(Board).where(Board.is_public.is_(True)).order_by(Board.created_at.desc()).limit(limit)
        else:
            stmt = (
                select(Board)
                .where((Board.is_public.is_(True)) | (Board.owner_id == owner_id))
                .order_by(Board.created_at.desc())
                .limit(limit)
            )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, board_id: UUID) -> Board | None:
        stmt = select(Board).where(Board.id == board_id)
        return self.db.scalar(stmt)

    def update(self, board: Board, title: str | None, description: str | None, is_public: bool | None) -> Board:
        if title is not None:
            board.title = title
        if description is not None:
            board.description = description
        if is_public is not None:
            board.is_public = is_public
        self.db.add(board)
        self.db.commit()
        self.db.refresh(board)
        return board

    def delete(self, board: Board) -> None:
        self.db.delete(board)
        self.db.commit()

    def add_pin(self, board_id: UUID, pin_id: UUID) -> BoardPin:
        existing = self.db.scalar(
            select(BoardPin).where(BoardPin.board_id == board_id, BoardPin.pin_id == pin_id)
        )
        if existing:
            return existing

        board_pin = BoardPin(board_id=board_id, pin_id=pin_id)
        self.db.add(board_pin)
        self.db.commit()
        self.db.refresh(board_pin)
        return board_pin

    def remove_pin(self, board_id: UUID, pin_id: UUID) -> bool:
        stmt = delete(BoardPin).where(BoardPin.board_id == board_id, BoardPin.pin_id == pin_id)
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0
