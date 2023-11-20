from sqlalchemy.orm import Session, joinedload

from ..models import *
from ..schemas import *


class MessageService:
    def __init__(self, db: Session):
        self.db = db

    def create_message(
        self,
        role: str,
        content: str,
        conversation_id: int,
        actions: list = None,
        function_call: dict = None,
        status: str = None,
        metadata: list = None,
        *args,
        **kwargs
    ):
        message = MessageModel(
            role=role,
            content=content,
            conversation_id=conversation_id,
            actions=actions,
            function_call=function_call,
            status=status,
            meta_data=metadata,
        )

        self.db.add(message)
        self.db.commit()

        return message

    def get_message_by_id(self, message_id: int):
        return self.db.query(MessageModel).filter(MessageModel.id == message_id).first()

    def delete_message(self, message: MessageModel):
        self.db.delete(message)
        self.db.commit()

    def archive_message(self, message: MessageModel):
        message.is_archived = True
        self.db.commit()

    def get_messages_by_conversation_id(
        self, conversation_id: int, archived: bool = False
    ):
        query = self.db.query(MessageModel).filter(
            MessageModel.conversation_id == conversation_id
        )

        if not archived:
            query = query.filter(MessageModel.is_archived == False)

        return query.order_by(MessageModel.id.desc()).all()

    def get_bookmarks(self):
        bookmarks = self.db.query(BookmarkModel).all()
        return bookmarks

    def get_bookmarks_with_details(self):
        bookmarks = (
            self.db.query(BookmarkModel)
            .options(
                joinedload(BookmarkModel.message).joinedload(MessageModel.conversation)
            )
            .all()
        )

        result = []
        for bookmark in bookmarks:
            bookmark_data = {
                "id": bookmark.id,
                "message_id": bookmark.message.id,
                "message_content": bookmark.message.content,
                "conversation_id": bookmark.message.conversation.id,
                "conversation_title": bookmark.message.conversation.title,
                "created_at": bookmark.created_at,
            }
            result.append(bookmark_data)

        print("Returning results: ", result)

        return result

    def add_bookmark(self, message_id: int):
        bookmark = BookmarkModel(message_id=message_id)

        self.db.add(bookmark)
        self.db.commit()
        self.db.refresh(bookmark)

        bookmark_data = {
            "id": bookmark.id,
            "message_id": bookmark.message.id,
            "message_content": bookmark.message.content,
            "conversation_id": bookmark.message.conversation_id,
            "conversation_title": bookmark.message.conversation.title,
            "created_at": bookmark.created_at,
        }

        return bookmark_data

    def remove_bookmark(self, message_id: int):
        bookmark = (
            self.db.query(BookmarkModel)
            .filter(BookmarkModel.message_id == message_id)
            .first()
        )

        if bookmark is not None:
            self.db.delete(bookmark)
            self.db.commit()

        return bookmark
