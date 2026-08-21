radio = playlist("/music")
radio_secure = mksafe(radio)
output.icecast(
	%mp3,
	host="icecast",
	port=8000,
	password="hackme",
	mount="/radio.mp3",
	radio_secure
)
