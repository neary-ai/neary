from sqlalchemy.orm import Session
from sqlalchemy import cast, String

from core.services.message_handler import MessageHandler
from modules.messages.schemas import FunctionMessage
from modules.plugins.models import FunctionInstanceModel
from modules.messages.models import MessageModel
from modules.messages.services.message_service import MessageService
from ..models import ApprovalRequestModel


class ApprovalService:
    def __init__(self, db: Session, message_handler: "MessageHandler" = None):
        self.db = db
        self.message_handler = (
            message_handler if message_handler else MessageHandler(db=db)
        )

        self.actions = {
            "handle_approval_response": self.handle_approval_response,
        }

    async def request_approval(
        self,
        tool: FunctionInstanceModel,
        tool_args: dict,
        conversation_id: int,
    ):
        """
        Issues an approval request and sends it to the frontend
        """
        pending_request = ApprovalRequestModel(
            conversation_id=conversation_id, tool_name=tool.name, tool_args=tool_args
        )
        self.db.add(pending_request)
        self.db.commit()

        # Then send notification to ui
        actions = [
            {
                "type": "function",
                "name": "handle_approval_response",
                "label": "Approve",
                "conversation_id": conversation_id,
                "data": {"request_id": str(pending_request.id), "response": "approve"},
            },
            {
                "type": "function",
                "name": "handle_approval_response",
                "label": "Reject",
                "conversation_id": conversation_id,
                "data": {"request_id": str(pending_request.id), "response": "reject"},
            },
        ]

        args_string = "\n".join(
            [
                f"| {k.replace('_', ' ').title()} | {', '.join(v) if isinstance(v, list) else v} |"
                for k, v in tool_args.items()
            ]
        )
        table_header = "| Name | Value |\n| --- | --- |"

        if args_string:
            notification = f"Neary would like to use the **{tool.function.display_name}** tool<<args>>{table_header}\n{args_string}<</args>>"
        else:
            notification = (
                f"Neary would like to use the **{tool.function.display_name}** tool"
            )

        metadata = [{"approval_request": pending_request.id}]

        await self.message_handler.send_notification_to_ui(
            message=notification,
            conversation_id=conversation_id,
            actions=actions,
            metadata=metadata,
            save_to_db=True,
        )

    def get_approval_request(self, request_id: str, status: str):
        return (
            self.db.query(ApprovalRequestModel)
            .filter(
                ApprovalRequestModel.id == request_id,
                ApprovalRequestModel.status == status,
            )
            .first()
        )

    def update_approval_request_status(
        self, approval_request: ApprovalRequestModel, status: str
    ):
        approval_request.status = status
        self.db.commit()
        return approval_request

    async def handle_approval_response(
        self,
        data: dict,
        message_id: int,
        conversation_id: int,
    ):
        request_id = data.get("request_id")
        response = data.get("response")
        print("Handling approval response.")
        if response.lower() not in ["approve", "reject"]:
            print("Invalid action. Use 'approve' or 'reject'")

        approval_request = self.get_approval_request(request_id, "pending")

        if not approval_request:
            print(f"Approval request not found: {request_id}")
            return

        if response.lower() == "approve":
            self.update_approval_request_status(approval_request, "approved")
            print("Sending update status message: accepted.")
            await self.message_handler.send_status_to_ui(
                message={"approval_response_processed": message_id},
                conversation_id=conversation_id,
            )

        elif response.lower() == "reject":
            print("Sending update status message: rejected.")
            await self.message_handler.send_status_to_ui(
                message={"approval_response_processed": message_id},
                conversation_id=conversation_id,
            )
            approval_request = self.update_approval_request_status(
                approval_request, "rejected"
            )

        await self.process_approval(approval_request)

        message = (
            self.db.query(MessageModel)
            .filter(
                MessageModel.role == "notification",
                cast(MessageModel.meta_data, String).like(f"%{request_id}%"),
            )
            .first()
        )

        if message:
            MessageService(self.db).delete_message(message)

        return f"Request {approval_request.status}"

    async def process_approval(self, approved_request: ApprovalRequestModel):
        from modules.plugins.services.plugin_service import PluginService
        from modules.conversations.services.chat_service import ChatService
        from modules.conversations.services.conversation_service import (
            ConversationService,
        )

        status = approved_request.status
        tool_name = approved_request.tool_name
        tool_args = approved_request.tool_args
        conversation_id = approved_request.conversation_id

        if status == "rejected":
            function_message = FunctionMessage(
                conversation_id=conversation_id,
                content="User rejected function approval request; function not executed.",
                function_call={"name": tool_name, "arguments": tool_args},
                metadata=[],
            )

            MessageService(self.db).create_message(**function_message.model_dump())

            return

        conversation = ConversationService(self.db).get_conversation_by_id(
            conversation_id
        )

        function_message, follow_up_requested = await PluginService(
            self.db, self.message_handler
        ).execute_tool(tool_name, tool_args, conversation, bypass_approval=True)

        if follow_up_requested:
            await ChatService(self.db, self.message_handler).handle_message(
                conversation_id=conversation_id, function_message=function_message
            )

    async def handle_action(self, name, data, message_id, conversation_id):
        print("handling action: ", message_id)
        action_handler = self.actions.get(name)
        if action_handler:
            response = await action_handler(data, message_id, conversation_id)
            return response
        else:
            print(f"Unrecognized action: {name}")
            raise Exception("Unrecognized action: {name}")
