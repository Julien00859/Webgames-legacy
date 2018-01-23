#!./venv/bin/python

import asyncio
import aiohttp
import urwid
import uvloop
from typing import Tuple, Dict, Any, NewType
import logging
from collections import namedtuple
from operator import itemgetter
from os import system
from functools import partial
from uuid import UUID
from contextlib import suppress, closing

from config import API_URL, LOG_LEVEL
from urllib.parse import urljoin

User = namedtuple("User", ["userid", "nickname", "is_admin"])
FullUser = namedtuple("FullUser", ["userid", "nickname", "email", "is_verified", "is_admin"])
me = None

FieldName = NewType("FieldName", str)
def form(callback: callable, title, *fields: Tuple[FieldName, urwid.Edit]) -> Dict[FieldName, Any]:
    body = [
        *map(itemgetter(1), fields),
        urwid.Divider(),
        urwid.Button("Send", on_press=(lambda _: callback({fields[n][0]: body[n].edit_text for n in range(len(fields)) if isinstance(body[n], urwid.Edit)})))
    ]
    return urwid.LineBox(urwid.Pile(body), f"{title} form")

def main():
    loop = asyncio.get_event_loop()
    logging.basicConfig(filename="log", level=LOG_LEVEL)
    if LOG_LEVEL == logging.DEBUG:
        loop.set_debug(True)

    asyncio_logger = logging.getLogger("asyncio")

    with closing(aiohttp.ClientSession(loop=loop)) as http:
        global request_api
        def request_api(method, url, *args, **kwargs):
            return http.request(method, urljoin(API_URL, url), *args, **kwargs)

        async def is_api_online():
            with suppress(aiohttp.client_exceptions.ClientConnectorError):
                async with request_api("get", "/status") as resp:
                    return resp.status == 200
            return False
        if not loop.run_until_complete(is_api_online()):
            logging.fatal("WebAPI unavailable")
            return

        u_header = urwid.Pile([
            urwid.Text("WebGames Terminal Client", align="center"),
            urwid.Divider()])
        
        u_body = urwid.Pile([
            navs["not_connected"],
            panels["login"]])

        global change_panel_to
        def change_panel_to(panel):
            u_body.contents[1] = (panels[panel], u_body.options())

        global change_nav_to
        def change_nav_to(nav):
            u_body.contents[0] = (navs[nav], u_body.options())

        global u_footer
        u_footer = urwid.Text("")

        mainloop = urwid.MainLoop(urwid.Frame(urwid.Filler(u_body, valign="top"), u_header, u_footer),
            event_loop=urwid.AsyncioEventLoop(
                loop=loop)).run()

async def process_response(resp, callback, *args, **kwargs):
    try:
        if resp.status == 200:
            if asyncio.iscoroutinefunction(callback):
                await callback(resp, *args, **kwargs)
            else:
                callback(resp, *args, **kwargs)
        elif resp.status != 500 and resp.content_type == "application/json":
            error = (await resp.json())["error"]
            u_footer.set_text(f"{resp.reason}: {error}")
            logging.error(f"[{resp.url}] {resp.reason}: {error}")
        else:
            body = (await resp.read()).decode()
            u_footer.set_text(resp.reason)
            logging.error(f"{resp.reason}\n{body}")
    except:
        logging.fatal("Error while processing response. URL: %s", resp.url, exc_info=True)
        raise urwid.ExitMainLoop()

async def ok_session(resp):
    u_footer.set_text("Authenticated ! Fetching user profile...")
    data = await resp.json()
    global request_api_jwt
    request_api_jwt = partial(request_api, headers={"Authorization": "Bearer: " + data["token"]})
    async with request_api_jwt("get", "/auth/account") as resp_account:
        await process_response(resp_account, ok_account_get, token=data["token"])

async def ok_account_get(resp, token):
    data_account = await resp.json()
    global me
    me = FullUser(**data_account)
    panels["profile"] = get_profile_form()
    change_nav_to("connected_as_user")
    change_panel_to("profile")
    u_footer.set_text("Welcome " + me.nickname)

async def ok_account_update(resp, form):
    global me
    d = me._asdict()
    d.update(form)
    me = FullUser(**d)
    u_footer.set_text("Updated")

def form_validation(func):
    def form_validation_wrapped(form, *args):
        if any(map(lambda value: value.strip() == "", form.values())):
            u_footer.set_text("Fill the blanks")
            return
        func(form, *args)
    return form_validation_wrapped


@form_validation
def fetch_forget(form):
    async def coro():
        async with request_api("post", "/auth/account/forget", json=form) as resp:
            #await process_response(resp, lambda _: u_footer.set_text("Please follow the link sent to your mail box"))
            #TODO email dans l'api x)
            async def truc(resp):
                logging.info((await resp.json()))
            await process_response(resp, truc)
    asyncio.ensure_future(coro())
    u_footer.set_text("Send request...")

def get_login_form():
    @form_validation
    def fetch_login(form):
        async def coro():
            async with request_api("post", "/auth/session", json=form) as resp:
                await process_response(resp, ok_session)
        asyncio.ensure_future(coro())
        u_footer.set_text("Authenticating...")


    log_ed = urwid.Edit("Login: ")
    return form(fetch_login, "Login",
        ("login", log_ed),
        ("password", urwid.Edit("Password: ", mask="*")),
        ("", urwid.Divider()),
        ("", urwid.Button("Password Forgotten", on_press=lambda _: fetch_forget({"login": log_ed.edit_text}))))

def get_register_form():
    @form_validation
    def fetch(form):
        if form["password"] != form["pwd-check"]:
            u_footer.set_text("The passwords don't match.")
            return
        del form["pwd-check"]
        async def coro():
            async with request_api("post", "/auth/account", json=form) as resp:
                #await process_response(resp, lambda _: u_footer.set_text("Please follow the link sent to your mail box"))
                #TODO email dans l'api x)
                async def truc(resp):
                    logging.info((await resp.json()))
                await process_response(resp, truc)
        asyncio.ensure_future(coro())
        u_footer.set_text("Registering...")

    return form(fetch, "Register",
        ("nickname", urwid.Edit("Nickname: ")),
        ("email", urwid.Edit("Email: ")),
        ("password", urwid.Edit("Password: ", mask="*")),
        ("pwd-check", urwid.Edit("Retype the password: ", mask="*")))


def get_profile_form():
    @form_validation
    def fetch(form):
        async def coro():
            async with request_api_jwt("put", "/auth/account", json=form) as resp:
                callback = partial(ok_account_update, form=form)
                await process_response(resp, callback)
        asyncio.ensure_future(coro())
        u_footer.set_text("Updating...")

    return form(fetch, "Profile",
        ("", urwid.Text(f"ID: {me.userid}")),
        ("nickname", urwid.Edit("Nickname: ", me.nickname)),
        ("email", urwid.Edit("Email: ", me.email)),
        ("", urwid.Button("Reset password", on_press=lambda _: fetch_forget(me.nickname))),
        ("", urwid.Text("Admin: %s" % "yes" if me.is_admin else "no")))

def get_reset_form(userid=""):
    @form_validation
    def fetch(form):
        if form["password"] != form["pwd-check"]:
            u_footer.set_text("The passwords don't match.")
            return
        async def coro():
            async with request_api("post", f"/auth/accounts/{form['id']}/reset", json={"password": form["password"], "token": form["token"]}) as resp:
                await process_response(resp, lambda _: u_footer.set_text("Password reset."))
        asyncio.ensure_future(coro())
        u_footer.set_text("Resetting password...")
    
    return form(fetch, "Reset Password",
        ("id", urwid.Edit("User ID: ", userid)),
        ("token", urwid.Edit("Reset Token: ")),
        ("password", urwid.Edit("Password: ", mask="*")),
        ("pwd-check", urwid.Edit("Retype the password: ", mask="*")))

def get_activation_form():
    @form_validation
    def fetch(form):
        async def coro():
            async with request_api("get", f"/auth/accounts/{form['id']}>/activation/{form['token']}") as resp:
                await process_response(resp, lambda _: u_footer.set_text("Account activated."))
        asyncio.ensure_future(coro())
        u_footer.set_text("Resetting password...")
    
    return form(fetch, "Account Activation",
        ("id", urwid.Edit("User ID: ")),
        ("token", urwid.Edit("Activation Token: ")))

def disconnect(*_):
    global me
    me = None

    global request_api_jwt
    request_api_jwt = None

    change_panel_to("login")
    change_nav_to("not_connected")

def exit_(*_):
    raise urwid.ExitMainLoop()

panels = {
    "login": urwid.Pile([
        urwid.Columns([
            get_register_form(),
            get_login_form()
        ]),
        get_activation_form(),
        get_reset_form()
    ])
}

navs = {
    "not_connected": urwid.Columns([
        urwid.Button("Quit", on_press=exit_)
    ]),
    "connected_as_user": urwid.Columns([
        urwid.Button("Profile", on_press=lambda _: change_panel_to("profile")),
        urwid.Button("Disconnect", on_press=disconnect),
        urwid.Button("Quit", on_press=exit_)
    ]),
    "connected_as_admin": urwid.Columns([
        urwid.Button("Quit", on_press=exit_)
    ])
}
if __name__ == "__main__":
    main()