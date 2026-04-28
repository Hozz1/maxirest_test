from uuid import UUID

from fastapi import HTTPException, status

from app.models.user import User
from app.repositories.boards import BoardRepository
from app.repositories.pins import PinRepository
from app.schemas.board import BoardCreate, BoardUpdate


class BoardService:
    def __init__(self, board_repo: BoardRepository, pin_repo: PinRepository):
        self.board_repo = board_repo
        self.pin_repo = pin_repo

    def create_board(self, current_user: User, data: BoardCreate):
        return self.board_repo.create(
            owner_id=current_user.id,
            title=data.title,
            description=data.description,
            is_public=data.is_public,
        )

    def list_boards(self, current_user: User | None):
        owner_id = current_user.id if current_user else None
        return self.board_repo.list_visible(owner_id=owner_id)

    def get_board(self, board_id: UUID, current_user: User | None):
        board = self.board_repo.get_by_id(board_id)
        if board is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")

        if not board.is_public and (current_user is None or current_user.id != board.owner_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
        return board

    def update_board(self, board_id: UUID, current_user: User, data: BoardUpdate):
        board = self.board_repo.get_by_id(board_id)
        if board is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
        if board.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

        return self.board_repo.update(
            board,
            title=data.title,
            description=data.description,
            is_public=data.is_public,
        )

    def delete_board(self, board_id: UUID, current_user: User) -> None:
        board = self.board_repo.get_by_id(board_id)
        if board is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
        if board.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        self.board_repo.delete(board)

    def add_pin_to_board(self, board_id: UUID, pin_id: UUID, current_user: User) -> None:
        board = self.board_repo.get_by_id(board_id)
        if board is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
        if board.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

        pin = self.pin_repo.get_by_id(pin_id)
        if pin is None or (not pin.is_public and pin.owner_id != current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pin not found")

        self.board_repo.add_pin(board_id=board_id, pin_id=pin_id)

    def remove_pin_from_board(self, board_id: UUID, pin_id: UUID, current_user: User) -> None:
        board = self.board_repo.get_by_id(board_id)
        if board is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
        if board.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

        removed = self.board_repo.remove_pin(board_id=board_id, pin_id=pin_id)
        if not removed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pin is not in board")
