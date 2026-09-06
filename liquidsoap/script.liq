settings.server.telnet.bind_addr.set("0.0.0.0")
server.telnet()
dj_queue = request.queue(id="dj")
radio = playlist("/tmp/music")
radio_secure = mksafe(radio)
final = fallback([dj_queue, radio_secure])
output.icecast(
	%mp3,
	host="icecast",
	port=8000,
	password=getenv("ICECAST_SOURCE_PASSWORD"),
	mount="/radio.mp3",
	icy_metadata="true",
	final
)
