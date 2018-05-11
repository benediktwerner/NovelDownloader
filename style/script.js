console.log("loaded script");

document.onkeydown = function(evt) {
	if (evt.keyCode == 39) {
		document.getElementById("next").click();
	}
	else if (evt.keyCode == 37) {
		document.getElementById("prev").click();
	}
}