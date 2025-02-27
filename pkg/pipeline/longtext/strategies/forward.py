# 转发消息组件
from __future__ import annotations
import typing

import pydantic.v1 as pydantic

from .. import strategy as strategy_model
from ....core import entities as core_entities
from ....platform.types import message as platform_message


class ForwardMessageDiaplay(pydantic.BaseModel):
    title: str = "群聊的聊天记录"
    brief: str = "[聊天记录]"
    source: str = "聊天记录"
    preview: typing.List[str] = []
    summary: str = "查看x条转发消息"


class Forward(platform_message.MessageComponent):
    """合并转发。"""
    type: str = "Forward"
    """消息组件类型。"""
    display: ForwardMessageDiaplay
    """显示信息"""
    node_list: typing.List[platform_message.ForwardMessageNode]
    """转发消息节点列表。"""
    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            self.node_list = args[0]
            super().__init__(**kwargs)
        super().__init__(*args, **kwargs)

    def __str__(self):
        return '[聊天记录]'


@strategy_model.strategy_class("forward")
class ForwardComponentStrategy(strategy_model.LongTextStrategy):

    async def process(self, message: str, query: core_entities.Query) -> list[platform_message.MessageComponent]:
        display = ForwardMessageDiaplay(
            title="群聊的聊天记录",
            brief="[聊天记录]",
            source="聊天记录",
            preview=["QQ用户: "+message],
            summary="查看1条转发消息"
        )

        node_list = [
            platform_message.ForwardMessageNode(
                sender_id=query.adapter.bot_account_id,
                sender_name='QQ用户',
                message_chain=platform_message.MessageChain([message])
            )
        ]

        forward = Forward(
            display=display,
            node_list=node_list
        )

        return [forward]
