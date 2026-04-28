from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_optional_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.boards import BoardRepository
from app.repositories.pins import PinRepository
from app.schemas.board import BoardCreate, BoardRead, BoardUpdate
from app.services.boards import BoardService

router = APIRouter(prefix="/boards", tags=["boards"])


@router.post("", response_model=BoardRead, status_code=status.HTTP_201_CREATED)
def create_board(data: BoardCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> BoardRead:
    board = BoardService(BoardRepository(db), PinRepository(db)).create_board(current_user, data)
    return BoardRead.model_validate(board)


@router.get("", response_model=list[BoardRead])
def list_boards(
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> list[BoardRead]:
    boards = BoardService(BoardRepository(db), PinRepository(db)).list_boards(current_user)
    return [BoardRead.model_validate(board) for board in boards]


@router.get("/{board_id}", response_model=BoardRead)
def get_board(
    board_id: UUID,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> BoardRead:
    board = BoardService(BoardRepository(db), PinRepository(db)).get_board(board_id, current_user)
    return BoardRead.model_validate(board)


@router.patch("/{board_id}", response_model=BoardRead)
def update_board(
    board_id: UUID,
    data: BoardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BoardRead:
    board = BoardService(BoardRepository(db), PinRepository(db)).update_board(board_id, current_user, data)
    return BoardRead.model_validate(board)


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(board_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Response:
    BoardService(BoardRepository(db), PinRepository(db)).delete_board(board_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{board_id}/pins/{pin_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_pin_to_board(
    board_id: UUID,
    pin_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    BoardService(BoardRepository(db), PinRepository(db)).add_pin_to_board(board_id, pin_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{board_id}/pins/{pin_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_pin_from_board(
    board_id: UUID,
    pin_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    BoardService(BoardRepository(db), PinRepository(db)).remove_pin_from_board(board_id, pin_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
