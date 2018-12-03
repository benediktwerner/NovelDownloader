
document.onreadystatechange = function() {
    if (document.readyState == "complete") {
        let nodes = document.getElementsByTagName("*");

        for (let node of nodes) {
            node.style = null;
        }
    }
}

document.onkeydown = function(evt) {
	if (evt.keyCode == 39) {
		document.getElementById("next").click();
	}
	else if (evt.keyCode == 37) {
		document.getElementById("prev").click();
	}
}
