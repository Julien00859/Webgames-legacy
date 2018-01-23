import urwid

views = {
    "login": urwid.Columns([
        get_register_form(),
        get_login_form()
    ]),
    "profile": 
}

def form(callback: callable, title, *fields: Tuple[FieldName, urwid.Edit]) -> Dict[FieldName, Any]:
    body = [
        *map(itemgetter(1), fields),
        urwid.Divider(),
        urwid.Button("Send", on_press=(lambda _: callback({fields[n][0]: body[n].edit_text for n in range(len(fields)) if isinstance(body[n], urwid.Edit)})))
    ]
    return urwid.LineBox(urwid.Pile(body), f"{title} form")

def get_profile_form():
    return form(logging.info, "Register",
        ("nickname", urwid.Edit("Nickname: ", User.me.nickname)),
        ("email", urwid.Edit("Email: ", User.me.email)),
        ("password", urwid.Edit("Password: ", mask="*")),
        ("pwd-check", urwid.Edit("Retype your password: ", mask="*")))


def get_register_form():
    return form(logging.info, "Register",
        ("nickname", urwid.Edit("Nickname: ")),
        ("email", urwid.Edit("Email: ")),
        ("password", urwid.Edit("Password: ", mask="*")),
        ("pwd-check", urwid.Edit("Retype your password: ", mask="*")))


def get_login_form():
    def fetch(form):
        async def coro():
            async with request_api("post", "/auth/session", json=form) as resp_session:
                await process_response(resp_session, ok_session)
        asyncio.ensure_future(coro())
        u_footer.set_text("Authenticating...")

    return form(fetch, "Login",
        ("login", urwid.Edit("Login: ")),
        ("password", urwid.Edit("Password: ", mask="*")))

