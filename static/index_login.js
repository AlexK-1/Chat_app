const socket = io();
socket.on("connect", function(data) {
    console.log("Socket.IO is connected!!!")
});

const body = document.body;

const send_message = document.getElementById("send_message");

send_message.addEventListener("click", function(){
    const message_text = document.getElementById("message_text");
    const username = document.getElementById("username");
    socket.emit("new_message", {poster: username.innerHTML, text: message_text.value});
    console.log("new_message");
});

socket.on("new_message", function(data) {
    console.log(`new_message recived ${data}`);

    const new_message = document.createElement("div");
    new_message.className = "post";
    const user = document.createElement("strong");
    user.innerHTML = data.poster;
    new_message.append(user);
    const text = document.createElement("p");
    text.innerHTML = data.text;
    new_message.append(text);

    try{
        const messages = body.getElementsByClassName("message");
        messages[0].before(new_message);
    }
    catch(err){
        const no_posts = document.getElementById("no_posts");
        no_posts.before(new_message)
        no_posts.remove()
    }
});