import mesop as me
from frontend.bot import page_body


@me.page(
    path='/',
    title='Virtual Assistant',
    on_load=lambda e: me.set_theme_mode(theme_mode='dark'),
    security_policy=me.SecurityPolicy(dangerously_disable_trusted_types=True),
)
def page_main() -> None:
    with me.box(
        style=me.Style(
            width='720px',
            height='100%',
            justify_self='center',
            border_radius='8px',
            font_family='Roboto',
            font_size=12,
            border=me.Border.all(
                value=me.BorderSide(width=1, color='white', style='solid')
            ),
        )
    ):
        page_body()
