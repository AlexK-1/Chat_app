const socket = io();

const updateForm = function(room_type) {
    const form = document.getElementsByTagName("form")[0];

    switch(room_type) {
        case "chat":
            form.innerHTML = `
            <input id="csrf_token" name="csrf_token" type="hidden" value="${csrf_token}">
            <p><input type="radio" name="type" value="chat" id="type_chat" onchange="updateForm('chat')" checked> Chat
            <input type="radio" name="type" value="group" id="type_group" onchange="updateForm('group')"> Group
            </p>

            <label for="username">Username</label><br>
            <input type="text" id="username" oninput="getUsersListChat()" name="username">
            <ul id="users_list"></ul>

            <input type="submit" name="submit" value="Create">
            `;

            break;
        case "group":
            form.innerHTML = `
            <input id="csrf_token" name="csrf_token" type="hidden" value="${csrf_token}">
            <p><input type="radio" name="type" value="chat" id="type_chat" onchange="updateForm('chat')"> Chat
                <input type="radio" name="type" value="group" id="type_group" onchange="updateForm('group')" checked> Group
            </p>

            <label for="group_name">Group name</label><br>
            <input type="text" id="group_name" name="group_name"><br><br>

            <label for="member_1">Mambers</label><br>
            <ul id="members">
                <li id="member_li_1"><input type="text" id="member_1" name="member_1" value="${user}" readonly></li>
            </ul>
            <input type="text" id="member_field" name="member_field" oninput="getUsersListGroup()"><button type="button" id="add_member" onclick="addMember()">Add</button><br><br>
            <ul id="users_list_members"></ul>

            <label for="admin_1">Admnis</label><br>
            <ul id="admins">
                <li id="admin_li_1" class="admin"><input type="text" id="admin_1" name="admin_1" value="${user}" readonly></li>
            </ul>
            <input type="text" id="admin_field" name="admin_field" oninput="getAdminsListGroup()"><button type="button" id="add_admin" onclick="addAdmin()">Add</button><br><br>
            <ul id="users_list_admins"></ul>

            <p><input type="radio" name="open" value="open" id="type_chat"> Open
                <input type="radio" name="open" value="closed" id="type_group" checked> Closed
            </p>

            <input type="submit" name="submit" value="Create">
            `;
            break;
    }
}

const insertIntoUsernameField = function(username) {
    field = document.getElementById("username");
    field.value = username;
    ul = document.getElementById("users_list");
    ul.innerHTML = "";
}

const insertIntoMemberField = function(username) {
    field = document.getElementById("member_field");
    field.value = username;
    ul = document.getElementById("users_list_members");
    ul.style.display = "none";
}

const insertIntoAdminsField = function(username) {
    field = document.getElementById("admin_field");
    field.value = username;
    ul = document.getElementById("users_list_admins");
    ul.style.display = "none";
}

const getUsersListChat = function() {
    const username = document.getElementById("username");
    if (username.value === "") {
        ul = document.getElementById("users_list");
        ul.innerHTML = "";
    } else {
        socket.emit("get_users_list", {s: username.value, user: [user]});

        socket.on("send_users_list", function(data) {
            ul = document.getElementById("users_list");
            ul.innerHTML = "";
            data.forEach(element => {
                li = document.createElement("li");

                text = document.createElement("p");
                //text.onclick = "insertIntoUsernameField(this.innerHTML)";
                text.setAttribute("onclick", "insertIntoUsernameField(this.innerHTML)")
                text.innerHTML = element;

                li.append(text);
                ul.append(li);
            });
            
        })
    }
}

const addMember = function() {
    const field = document.getElementById("member_field");
    if (field.value !== "") {
        let users = [...document.getElementById("users_list_members").getElementsByTagName("li")];
        users = users.map(function(value) {
            const p = value.getElementsByTagName("p")[0];
            return p.innerHTML;
        });

        if (users.includes(field.value)) {
            const ul = document.getElementById("members");
            const li = document.createElement("li");
            li.id = "member_li_"+(ul.getElementsByTagName("li").length+1);

            const member = document.createElement("input");
            member.tupe = "text";
            member.id = "member_"+(ul.getElementsByTagName("li").length+1);
            member.name = member.id;
            member.value = field.value;
            member.readOnly = true;

            const button = document.createElement("button");
            button.innerHTML = "✖";
            button.id = "mx"+(ul.getElementsByTagName("li").length+1);
            button.setAttribute("onclick", "removeMember(this.id[2])")
            button.type = "button"; 

            li.append(member);
            li.append(button);
            ul.append(li);

            field.value = "";
        }
    }
}

const removeMember = function(id) {
    const member_li = document.getElementById("member_li_"+id);
    const input = member_li.getElementsByTagName("input")[0];
    const admin_li = document.querySelector(`.admin[v="${input.value}"]`);

    member_li.remove();
    try {
        admin_li.remove();
    } catch {}
}

const getUsersListGroup = function() {
    const field = document.getElementById("member_field");
    const ul = document.getElementById("users_list_members");
    ul.style.display = "";

    if (field.value === "") {
        ul.innerHTML = "";
    } else {
        let members = [...document.getElementById("members").getElementsByTagName("li")];
        members = members.map(function(item) {
            const input = item.getElementsByTagName("input")[0];
            return input.value;
        });
        socket.emit("get_users_list", {s: field.value, user: members});
    }

    socket.on("send_users_list", function(data) {
        ul.innerHTML = "";
        data.forEach(element => {
            li = document.createElement("li");

            text = document.createElement("p");
            //text.onclick = "insertIntoUsernameField(this.innerHTML)";
            text.setAttribute("onclick", "insertIntoMemberField(this.innerHTML)")
            text.innerHTML = element;

            li.append(text);
            ul.append(li);
        });
    })
}

const addAdmin = function() {
    const field = document.getElementById("admin_field");

    if (field.value !== "") {
        let users = [...document.getElementById("users_list_admins").getElementsByTagName("li")];
        users = users.map(function(value) {
            const p = value.getElementsByTagName("p")[0];
            return p.innerHTML;
        });

        if (users.includes(field.value)) {
            const ul = document.getElementById("admins");
            const li = document.createElement("li");
            li.id = "admin_li_"+(ul.getElementsByTagName("li").length+1);
            li.className = "admin";
            li.setAttribute("v", field.value)

            const admin = document.createElement("input");
            admin.tupe = "text";
            admin.id = "admin_"+(ul.getElementsByTagName("li").length+1);
            admin.name = admin.id;
            admin.value = field.value;
            admin.readOnly = true;

            const button = document.createElement("button");
            button.innerHTML = "✖";
            button.id = "ax"+(ul.getElementsByTagName("li").length+1);
            button.setAttribute("onclick", "removeAdmin(this.id[2])")
            button.type = "button"; 

            li.append(admin);
            li.append(button);
            ul.append(li);

            field.value = "";
        }
    }

}

const removeAdmin = function(id) {
    const li = document.getElementById("admin_li_"+id);
    li.remove();
}

const getAdminsListGroup = function() {
    const field = document.getElementById("admin_field");
    const ul = document.getElementById("users_list_admins");
    ul.style.display = "";
    ul.innerHTML = "";

    if (field.value !== "") {
        let members = [...document.getElementById("members").getElementsByTagName("li")];
        members = members.map(function(item) {
            const input = item.getElementsByTagName("input")[0];
            return input.value;
        });
    
        let admins = [...document.getElementById("admins").getElementsByTagName("li")];
        admins = admins.map(function(item) {
            const input = item.getElementsByTagName("input")[0];
            return input.value;
        });

        const not_admins_users = members.filter(element => !admins.includes(element));

        const list = not_admins_users.filter(element => element.includes(field.value));

        list.forEach(element => {
            li = document.createElement("li");

            text = document.createElement("p");
            //text.onclick = "insertIntoUsernameField(this.innerHTML)";
            text.setAttribute("onclick", "insertIntoAdminsField(this.innerHTML)")
            text.innerHTML = element;

            li.append(text);
            ul.append(li);
        });
    }
    
}