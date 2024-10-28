import mesop as me
import mesop.labs as mel
from backend.parser import transform


def page_body() -> None:
    with me.box(
        style=me.Style(
            height='95%',
            border_radius='16px',
            margin=me.Margin(top='16px', left='16px', right='16px'),
        )
    ):
        mel.chat(
            transform=transform,
            title='SQLite Virtual Assistant',
            bot_user='Bot',
        )
