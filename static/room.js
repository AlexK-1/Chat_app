const ROOM_ID = Number(window.location.pathname.split("/")[2]);
let IS_ADMIN = undefined;
let IS_OWNER = undefined;
let ROOM_OWNER = undefined;
let ROOM_ADMINS = undefined;
let ROOM_MEMBERS = undefined;

const addAdminToList = function(name) {
    const admins_label = document.getElementById("admins-label");

    const li = document.createElement("li");
    li.className = "member-name-item";
    li.id = `admin_${name}`;

    const span_name = document.createElement("span");
    span_name.innerHTML = name
    span_name.className = "member-name";
    li.append(span_name);

    if (name === ROOM_OWNER) {
        const span_owner = document.createElement("span");
        span_owner.className = "member-status member-owner";
        span_owner.innerHTML = "owner";
        li.append(span_owner);
    }

    if (IS_OWNER && ROOM_OWNER !== name) {
        const demote_admin_button = document.createElement("button");
        demote_admin_button.type = "button";
        demote_admin_button.setAttribute("onclick", `demoteAdmin('${name}')`);
        demote_admin_button.innerHTML = "Demote";
        li.append(demote_admin_button);
        
        const remove_button = document.createElement("button");
        remove_button.type = "button";
        remove_button.setAttribute("onclick", `removeMember('${name}')`);
        remove_button.innerHTML = "Remove";
        li.append(remove_button);
    }

    admins_label.after(li);
}

const addMemberToList = function(name) {
    const members_label = document.getElementById("members-label");

    const li = document.createElement("li");
    li.className = "member-name-item";
    li.id = `member_${name}`;

    const span_name = document.createElement("span");
    span_name.innerHTML = name
    span_name.className = "member-name";
    li.append(span_name);

    if (ROOM_ADMINS.includes(name)) {
        const span_admin = document.createElement("span");
        span_admin.className = "member-status member-admin";
        span_admin.innerHTML = "admin";
        li.append(span_admin);
    }

    if (name === ROOM_OWNER) {
        const span_owner = document.createElement("span");
        span_owner.className = "member-status member-owner";
        span_owner.innerHTML = "owner";
        li.append(span_owner);
    }

    if (IS_ADMIN && ROOM_OWNER !== name) {
        if (!ROOM_ADMINS.includes(name)) {
            const make_admin_button = document.createElement("button");
            make_admin_button.type = "button";
            make_admin_button.setAttribute("onclick", `makeAdmin('${name}')`);
            make_admin_button.innerHTML = "Promote";
            li.append(make_admin_button);
        }

        if (IS_OWNER) {
            const remove_button = document.createElement("button");
            remove_button.type = "button";
            remove_button.setAttribute("onclick", `removeMember('${name}')`);
            remove_button.innerHTML = "Remove";
            li.append(remove_button);
        }
    }

    members_label.after(li);
}

const addPost = function(post_data) {
    const no_posts = document.getElementById("no-posts-message");
    if (no_posts !== null) {
        no_posts.remove();
    }

    const posts_container = document.getElementById("posts-container");

    const post = document.createElement("div");
    post.className = "post";
    post.id = `post${post_data[0]}`;

    const strong = document.createElement("strong");
    strong.className = "poster-name";
    strong.innerHTML = post_data[1];

    const p = document.createElement("p");
    p.className = "post-text";
    p.innerHTML = post_data[2];

    post.append(strong);
    post.append(p);

    if (IS_ADMIN || post_data[1] === user) {
        const del_button = document.createElement("button");
        del_button.type = "button";
        del_button.className = "delete-post-button";
        del_button.setAttribute("onclick", `deletePost(${post_data[0]})`);
        del_button.innerHTML = "Delete";
        post.append(del_button);
    }

    posts_container.prepend(post);
}

const init_data = function(room_){
    room = room_;
    console.log(room);
}

//Создание страницы

const createRoomsList = function(data) {

    if (data.successful) {
        const ul = document.getElementById("rooms-list")

        const loading = document.getElementById("rooms_loading");
        loading.remove();

        if (data.groups.length > 0) {
            const li_label = document.createElement("li");
            li_label.className = "rooms-label";

            const p_label = document.createElement("p");
            p_label.innerHTML = "Your groups:";

            li_label.append(p_label);
            ul.append(li_label);

            data.groups.forEach(element => {
                const li = document.createElement("li");

                const a = document.createElement("a");
                a.href = "/rooms/" + element[0];
                a.className = "room-container";

                const div = document.createElement("div");

                const p = document.createElement("p");
                p.innerHTML = `${element[1]} ${element[2]}`;
                p.className = "room-name";

                div.append(p);
                a.append(div);
                li.append(a);
                ul.append(li);
            });
        }

        if (data.chats.length > 0) {
            const li_label = document.createElement("li");
            li_label.className = "rooms-label";

            const p_label = document.createElement("p");
            p_label.innerHTML = "Your chats:";

            li_label.append(p_label);
            ul.append(li_label);

            data.chats.forEach(element => {
                const li = document.createElement("li");

                const a = document.createElement("a");
                a.href = "/rooms/" + element[0];
                a.className = "room-container";

                const div = document.createElement("div");

                const p = document.createElement("span");
                p.innerHTML = `${element[1]} ${element[2]}`;
                p.className = "room-name";

                div.append(p);
                a.append(div);
                li.append(a);
                ul.append(li);
            });
        }
    }
}

const createMembersList = function(data) {

    if (data.successful) {
        IS_ADMIN = data.is_admin;
        IS_OWNER = data.is_owner;
        ROOM_OWNER = data.owner;
        ROOM_MEMBERS = data.members;
        ROOM_ADMINS = data.admins;

        const ul = document.getElementById("room-members-list");
        const members_label = document.getElementById("members-label");
        const admins_label = document.getElementById("admins-label");

        const loadings = document.getElementsByClassName("members-loading");
        loadings[0].remove(); loadings[0].remove();

        if (data.members === "*all") {
            const li = document.createElement("li");
            li.className = "member-name";

            const span = document.createElement("span");
            span.innerHTML = "all";

            li.append(span);
            members_label.after(li);
        } else {
            data.members.forEach(element => {
                addMemberToList(element);
            });
        }

        data.admins.forEach(element => {
            addAdminToList(element);
        });
    } else {
        const panel = document.getElementById("right-panel");
        panel.remove();

        const wrapper = document.getElementById("main-wrapper");
        wrapper.style.gridTemplateColumns = "315px auto";
    }
}

const createPosts = function(data) {
    console.log(data);

    if (data.successful) {
        const main = document.getElementsByTagName("main")[0];
        const sticky_panel = document.getElementById("upper-sticky-panel");

        const loading = document.getElementById("posts-loading");
        loading.remove();
        
        const write_post_container = document.createElement("div");
        write_post_container.id = "write-post-container";
        const posts_container = document.createElement("div");
        posts_container.id = "posts-container";

        if (data.can_write) {
            const textarea = document.createElement("textarea");
            textarea.placeholder = "Write a message";
            textarea.id = "post-textarea";

            textarea.addEventListener("input", event => {
                textarea.style.height = 0;
                textarea.style.height = textarea.scrollHeight + "px";
            })

            const send_button = document.createElement("button");
            send_button.type = "button";
            send_button.id = "send-message";
            send_button.onclick = sendMessage;
            send_button.innerHTML = "Send";

            write_post_container.append(textarea);
            write_post_container.append(send_button);
        } else {
            const cant_write = document.createElement("p");
            cant_write.innerHTML = "You can't write in this room."
            write_post_container.append(cant_write);
        }

        sticky_panel.append(write_post_container);
        main.append(posts_container);

        if (data.posts.length === 0) {
            const no_posts = document.createElement("p");
            no_posts.id = "no-posts-message";
            no_posts.innerHTML = "There is nothing in this chat yet.";

            posts_container.append(no_posts);
        } else {
            data.posts.reverse();
            data.posts.forEach(element => {
                addPost(element);
            });
        }
    }
}

fetch(`${location.protocol + '//' + location.host}/api/user_rooms`)
    .then(data => data.json())
    .then(json => createRoomsList(json));

fetch(`${location.protocol + '//' + location.host}/api/room_members/${room[0]}`)
    .then(data => data.json())
    .then(json => createMembersList(json));

fetch(`${location.protocol + '//' + location.host}/api/room_posts/${room[0]}?e=20`)
    .then(data => data.json())
    .then(json => createPosts(json));

//Обработка событий

const socket = io();

socket.on("connect", function(data) {
    console.log("Socket.IO is connected!!!")
});

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

const sendMessage = function() {
    const message_text = document.getElementById("post-textarea");
    const data = {poster: user, text: message_text.value, room: ROOM_ID};
    console.log(data);
    socket.emit("new_message", data);
}

socket.on("new_message_created", function(data) {
    if (data.room === ROOM_ID) {
        const new_data = [data.post_id, data.poster, data.text];
        addPost(new_data);
    }
});

const makeAdmin = function(member_name) {
    data = {member: member_name, room_id: ROOM_ID};
    socket.emit("promote_member", data);
}

socket.on("promoted_member", function(data) {
    if (data["room_id"] == ROOM_ID) {
        const admins_label = document.getElementById("admins-label");

        const member = document.getElementById(`member_${data.member}`);
        member.remove();

        ROOM_ADMINS.push(data.member);

        addMemberToList(data.member);
        addAdminToList(data.member);
    }
});

const demoteAdmin = function(admin_name) {
    data = {admin: admin_name, room_id: ROOM_ID};
    socket.emit("demote_admin", data);
}

socket.on("demoted_admin", function(data) {
    ROOM_ADMINS.splice(ROOM_ADMINS.indexOf(data.admin));

    if (data["room_id"] == ROOM_ID) {
        if (data["admin"] == user) {
            const right_panel = document.getElementById("right-panel");
            right_panel.remove()
            IS_ADMIN = false;
        } else {
            const li_admin = document.getElementById("admin_"+data.admin);
            li_admin.remove();
            const li_member = document.getElementById("member_"+data.admin);
            li_member.remove();
            addMemberToList(data.admin);
        }
    }
});

const removeMember = function(member_name) {
    data = {member: member_name, room_id: room[0]};
    socket.emit("remove_member", data);
}

socket.on("removed_member", function(data) {
    if (data["room_id"] == ROOM_ID) {
        if (data["member"] == user) {
            window.location.reload();
        } else {
            const li_member = document.getElementById("member_"+data["member"]);
            li_member.remove();
            
            try {
                const li_admin = document.getElementById("admin_"+data["member"]);
                li_admin.remove();
            } catch(e) {}
        }
    }
});