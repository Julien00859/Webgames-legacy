# socket_io.on('message', namespace='/chat', message_handler)
import views
import events
from os.path import join as pathjoin

def router(app, sio) -> None:
    app.add_route(views.index, "/", methods=["GET"])
    app.add_route(views.signup, "/signup", methods=["POST"])
    app.add_route(views.signin, "/signin", methods=["POST"])
    app.add_route(views.refresh, "/refresh", methods=["POST"])
    app.add_route(views.signout, "/signout", methods=["POST"])
    app.add_route(views.challenge, "/challenge/<token>", methods=["GET"])

    app.static("/assets", pathjoin(".", "client", "assets"))

    sio.on("/join_queue", events.join_queue)
