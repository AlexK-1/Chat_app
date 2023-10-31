const socket = io();

socket.on("connect", function(data) {
    console.log("Socket.IO is connected!!!")
});

const init_data = function(room_){
    room = room_;
    console.log(room);
}

const body = document.body;

const send_message = document.getElementById("send_message");

const deletePost = function(post_id) {
    const data = {post_id: post_id};
    socket.emit("delete_post", data);
}

socket.on("post_deleted", function(data) {
    if (data["room_id"] === room[0]) {
        const post = document.getElementById("post"+data["post_id"])
        try {
            post.remove()
        } catch {}
    }
})

send_message.addEventListener("click", function(){
    const message_text = document.getElementById("message_text");
    const username = document.getElementById("username");
    const data = {poster: user, text: message_text.value, room: room[0]};
    console.log(data);
    socket.emit("new_message", data);
});

socket.on("new_message_created", function(data) {
    if (data.room === room[0]) {
        const new_message = document.createElement("div");
        new_message.className = "post";
        new_message.id = "post"+data["post_id"];
        const user_strong = document.createElement("strong");
        user_strong.innerHTML = data.poster;
        new_message.append(user_strong);
        const text = document.createElement("p");
        text.innerHTML = data.text;
        new_message.append(text);
        console.log(data["poster"]);
        console.log(user);
        if (is_admin || data["poster"] == user) {
            const del_button = document.createElement("button");
            del_button.type = "button";
            del_button.setAttribute("onclick", `deletePost(${data["post_id"]})`);
            del_button.innerHTML = "Delete post";
            new_message.append(del_button);
        }

        try{
            const messages = body.getElementsByClassName("post");
            messages[0].before(new_message);
        }
        catch(err){
            const no_posts = document.getElementById("no_posts");
            no_posts.before(new_message);
            no_posts.remove();
    }}
});