var global_channel_list = [];
var global_user_list = [];
var global_current_channel;
var msgType = "PUBLIC";
let displayname = localStorage.getItem('displayname');

function clickhandler(chn) {
    // unweight the previous channel
    if (global_channel_list.includes(global_current_channel)) {
	document.getElementById(global_current_channel).style.fontWeight = "normal";
    }

    global_current_channel =  chn;
    msgType = "PUBLIC";
    let hdr = document.getElementById("message_header");

    // weight font on the new channel
    document.getElementById(global_current_channel).style.fontWeight = "bold";

    hdr.innerHTML = " Messages on " + global_current_channel + " channel";
    localStorage.setItem("channel", global_current_channel);
    configure_msgs(global_current_channel, msgType);
}

function dm_clickhandler(usr) {
    let hdr = document.getElementById("message_header");
    msgType = "PRIVATE";

    // unweight the regular channel.
    document.getElementById(global_current_channel).style.fontWeight = "normal";
    
    global_current_channel = usr;
    // weight font on the new channel
    document.getElementById(usr).style.fontWeight = "bold";

    hdr.innerHTML = "Conversations with " + usr;
    configure_msgs(usr, msgType);
}


// Add a channel to the list.  
function add_channel(chn, selected) {
    const new_chn_row = document.createElement('TR');
    var c = new_chn_row.insertCell(-1);

    c.innerHTML = chn;
    c.setAttribute("id", chn);
    c.setAttribute("class", "channel-listing");
    c.setAttribute("data-channel", chn);

    let chntrow = chn + "row"
    new_chn_row.setAttribute("id", chntrow);
    new_chn_row.setAttribute("class", "channel-listing");
    new_chn_row.setAttribute("data-channel", chn);
    global_channel_list.push(chn);

    var emnt = new_chn_row.querySelector("td");
    emnt.addEventListener("click", function() { clickhandler (chn); });
    document.getElementById('hoverTable').append(new_chn_row);
    if (selected == 1) {
	clickhandler(chn);
    }
}

// Activate a user
function activate_user(usr) {
    const logged_in = document.getElementById(usr);
    console.log ("AU: usr = ", usr);
    logged_in.style.fontWeight = "normal";
}

// Deactivate a user
function deactivate_user(usr) {
    const logged_in = document.getElementById(usr);

    console.log ("DU: logged in is ", logged_in);
    logged_in.style.fontWeight = "normal";
    logged_in.style.fontStyle = "italic";
}

// Add a user to the list.  
function add_user(usr) {
    const new_usr_row = document.createElement('TR');
    var c = new_usr_row.insertCell(-1);

    c.innerHTML = usr;
    c.setAttribute("id", usr);
    c.setAttribute("class", "user-listing");
    c.setAttribute("data-user", usr);

    let usrtrow = usr + "row"
    new_usr_row.setAttribute("id", usrtrow);
    new_usr_row.setAttribute("class", "user-listing");
    new_usr_row.setAttribute("data-user", usr);
    global_user_list.push(usr);

    var emnt = new_usr_row.querySelector("td");
    emnt.addEventListener("click", function() { dm_clickhandler (usr); });
    document.getElementById('user_list').append(new_usr_row);
}

function configure_channels() {
    // Get List of Channels
    const request = new XMLHttpRequest();
    request.open('POST', '/query_channels');
	 
    if (localStorage.getItem('channel')) {
	global_current_channel = localStorage.getItem('channel');
    }
    else {
	global_current_channel = "General";
    }
    // Callback function for when request completes
    request.onload = () => {

	// Extract JSON data from request
	const data = JSON.parse(request.responseText);
		
	// Extract list of channels and populate variable and dropdown menu
	if (data.success) {
	    var channels = data["channel_list"];
	    for (var i = 0, len = channels.length; i < len; i++) {
		if (channels[i] == global_current_channel){
		    add_channel(channels[i], 1);
		}
		else {
		    add_channel(channels[i],0);
		}
	    }
	}
	else {
	    console.log("API call failed");
	}
    }

    // Send request
    request.send();
}

// Add a message to the displayed message list.  
function add_message(msg) {
    const new_row = document.createElement('TR');
    var c = new_row.insertCell(0);

    let ts = "<font class='tstamp'>" + msg["timestamp"] + "</font>";
    let dn = " <font class='dname'> @" + msg["user_from"] + "</font><br>";

    let n_msg = ts + dn + msg["msg_txt"];
    c.innerHTML = n_msg;
    document.getElementById('message_list').append(new_row);
}

// Clear messages when switching channels
function clear_messages() {
    var myNode = document.getElementById('message_list');

    while (myNode.firstChild) {
	myNode.removeChild(myNode.firstChild);
    }
}

// Clear user list
function clear_users() {
    var myNode = document.getElementById('user_list');

    while (myNode.firstChild) {
	myNode.removeChild(myNode.firstChild);
    }
}
function configure_msgs(chn, isPub) {
    // Clear out old message list
    clear_messages();

    // Get Messages on this channel

    const request = new XMLHttpRequest();
    request.open('POST', '/query_messages');

    console.log ("CM: msgType = ", msgType)
    // Callback function for when request completes
    request.onload = () => {

	// Extract JSON data from request
	const data = JSON.parse(request.responseText);
		
	// Extract dictionary of messages and populate message pane
	if (data.success) {
	    console.log ("configure_msgs: success.  messages =", data["channel_msgs"])
	    var messages = data["channel_msgs"];
	    for (var i = 0, len = messages.length; i < len; i++) {
		add_message(messages[i]);
	    }
	}
    }

    // Add data to send with request for messages on this channel
    const data = new FormData();
    data.append('channel', chn);
    data.append('displayname', displayname);
    data.append('msg_type', msgType);
    
    console.log ("CM: data = ", data)

    // Send request
    request.send(data);
    return false;
}

function configure_users() {
    // Clear out old user list
    clear_users();

    // Get active users

    const request = new XMLHttpRequest();
    request.open('POST', '/query_users');
	    
    // Callback function for when request completes
    request.onload = () => {

	// Extract JSON data from request
	const data = JSON.parse(request.responseText);
		
	// Extract dictionary of messages and populate message pane
	if (data.success) {
	    users = data["active_users"]
	    for (var i = 0, len = users.length; i < len; i++) {
		if (users[i] != 'None') {
		    console.log ("configure:users: adding ", users[i]);
		    add_user(users[i]);
		}
	    }
	}
	else {
	    console.log("API query users failed");
	}
    }

    // Add data to send with request for messages on this channel
    //const data = new FormData();
    //data.append('channel', chn);
    //data.append('username', displayname);

    // Send request
    request.send();
    return false;
}

document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // Get/Set displayname
    let dn = document.getElementById("dname").innerHTML;
    if (dn != displayname) {
	displayname = dn;
	localStorage.setItem("displayname", dn);
    }

    socket.on('connect', () => {
	    var id = socket.io.engine.id;

	    socket.emit ("join", {"displayname": displayname, "room": id});
	    configure_channels();
	    configure_users();
	});


    // By default, submit buttons are disabled
    document.getElementById('submit').disabled = true;
    document.getElementById('msg_submit').disabled = true;

    // Enable button only if there is text in the input field
    document.getElementById('channel_name').onkeyup = () => {
	if (document.getElementById('channel_name').value.length > 0)
	    document.getElementById('submit').disabled = false;
	else
	    document.getElementById('submit').disabled = true;
    };

    document.getElementById('message_text').onkeyup = () => {
	if (document.getElementById('message_text').value.length > 0)
	    document.getElementById('msg_submit').disabled = false;
	else
	    document.getElementById('msg_submit').disabled = true;
    };

    // Set the displayname
    document.getElementById("new_channel").onsubmit = () => {
	    
	var chn  = document.getElementById('channel_name').value;

	if (global_channel_list.includes(chn)) {
	    alert ("Channel already exists");
	}
	else {
	    document.getElementById('channel_name').value = "";
	    document.getElementById('submit').disabled = true;
	    socket.emit('submit channel', {'channel': chn});
	}
	return false;
    };
	    
    document.getElementById("logout_button").onclick = () => {
	const request = new XMLHttpRequest();
	request.open('POST', '/logout');

	socket.emit('logout user', {'displayname': displayname});
	// Callback function for when request completes
	request.onload = () => {

	    // Extract JSON data from request
	    //	    const data = JSON.parse(request.responseText);
	}

	const data = new FormData();
	data.append('displayname', displayname);

	// Send request
	request.send();
	return false;
	 
    };

    // When a new channel is announced, add to the channel list
    socket.on('announce channel', data => {
	    add_channel(data["channel"], 0);
	});

    socket.on('new user', data => {
	    // Don't add self twice
	    if ((data["username"] == displayname) || 
	        (global_user_list.includes(data["username"]))) {
		return false;
	    }
	    else {
		add_user(data["username"]);
	    }
	});

    socket.on('user logged in', data => {
	    activate_user(data["username"]);
	});

    socket.on('user logged out', data => {
	    console.log ("Received logout message for ", data["username"])
	    deactivate_user(data["username"]);
	});

    // When a new message is announced, add to the message list
    socket.on('announce message', data => {
	    if (data["channel"] == global_current_channel) {
		add_message(data);
	    }
	});

    document.getElementById("new_message").onsubmit = () => {
	    
	var val  = document.getElementById('message_text').value;
	var dt = new Date();
	var dn = document.getElementById('displayname').value;

	document.getElementById('message_text').value = "";
	document.getElementById('msg_submit').disabled = true;
	chn = global_current_channel;
	// Submit channel (or user_to), timestamp, user_from, msg_txt
	socket.emit('submit message', {'msg_txt': val, 'channel': chn,'timestamp': dt, 'user_from': displayname});
	return false;
    };
    });

