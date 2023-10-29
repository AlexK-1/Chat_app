const socket = io();

const makeAdmin = function(member_name) {
    data = {member: member_name, room_id: room[0]};
    socket.emit("promote_member", data);
}

socket.on("promoted_member", function(data) {
    if (data["room_id"] == room[0]) {
        const ul_admins = document.getElementById("admins");

        const li_member = document.getElementById("member_"+data["member"]);
        li_member.getElementsByTagName("button")[0].remove();
        const span_admin = document.createElement("span")
        span_admin.innerHTML = "admin";
        li_member.getElementsByTagName("div")[0].append(span_admin);

        const li_admin = document.createElement("li");
        li_admin.id = "admin_"+data["member"];
        const div_admin = document.createElement("div");
        const span_username = document.createElement("span");
        span_username.innerHTML = data["member"];
        div_admin.append(span_username);

        const demote_button = document.createElement("button");
        demote_button.type = "button";
        demote_button.innerHTML = "Demote";
        demote_button.setAttribute("onclick", `demoteAdmin('${data["member"]}')`);
        div_admin.append(demote_button);

        const remove_button = document.createElement("button");
        remove_button.type = "button";
        remove_button.innerHTML = "Remove";
        remove_button.setAttribute("onclick", `removeMember('${data["member"]}')`);
        div_admin.append(remove_button);

        li_admin.append(div_admin);

        ul_admins.append(li_admin);
    }
});

const demoteAdmin = function(admin_name) {
    data = {admin: admin_name, room_id: room[0]};
    socket.emit("demote_admin", data);
}

socket.on("demoted_admin", function(data) {
    if (data["room_id"] == room[0]) {
        if (data["admin"] == user) {
            window.location.replace(location.protocol + '//' + location.host + "/rooms/" + room[0]);
        } else {
            const li_admin = document.getElementById("admin_"+data["admin"]);
            li_admin.remove();

            const li_member = document.getElementById("member_"+data["admin"]);
            const div_member = li_member.getElementsByTagName("div")[0];
            div_member.getElementsByTagName("span")[1].remove();

            const promote_button = document.createElement("button");
            promote_button.type = "button";
            promote_button.innerHTML = "Promote";
            promote_button.setAttribute("onclick", `makeAdmin('${data["admin"]}')`);
            div_member.append(promote_button);
        }
    }
});

const removeMember = function(member_name) {
    data = {member: member_name, room_id: room[0]};
    socket.emit("remove_member", data);
}

socket.on("removed_member", function(data) {
    if (data["room_id"] == room[0]) {
        if (data["member"] == user) {
            window.location.replace(location.protocol + '//' + location.host + "/rooms/" + room[0]);
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