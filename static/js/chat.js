document.addEventListener("DOMContentLoaded", function () {
  const chatbox = document.querySelector("#chatbox");

  // Function to scroll to the bottom of the chatbox
  function scrollToBottom() {
    chatbox.scrollTop = chatbox.scrollHeight;
  }

  // Function to create status indicators
  function createStatusIndicator(status) {
    const statusDiv = document.createElement('div');
    statusDiv.className = 'message-status';
    
    if (status === 'sent') {
      // Una palomita gris
      statusDiv.innerHTML = '<i class="fas fa-check text-secondary ml-2"></i>';
    } else if (status === 'delivered') {
      // Dos palomitas grises
      statusDiv.innerHTML = '<i class="fas fa-check-double text-secondary ml-2"></i>';
    } else if (status === 'read') {
      // Dos palomitas azules
      statusDiv.innerHTML = '<i class="fas fa-check-double text-primary ml-2"></i>';
    }
    
    return statusDiv;
  }

  // Scroll to bottom when the page is loaded
  scrollToBottom();

  const roomName = JSON.parse(document.getElementById("room_name").textContent);
  const userUsername = JSON.parse(document.getElementById("user_username").textContent);

  const chatSocket = new WebSocket(
    "ws://" + window.location.host + "/ws/chat/" + roomName + "/"
  );

  chatSocket.onopen = function (e) {
    console.log("The connection was set up successfully!");
  };
  
  chatSocket.onclose = function (e) {
    console.log("Something unexpected happened!");
  };

  document.querySelector("#my_input").focus();
  document.querySelector("#my_input").onkeyup = function (e) {
    if (e.keyCode == 13) {
      e.preventDefault();
      document.querySelector("#submit_button").click();
    }
  };

  document.querySelector("#submit_button").onclick = function (e) {
    var messageInput = document.querySelector("#my_input").value;

    if (messageInput.length == 0) {
      alert("Add some input first or press the Send button!");
    } else {
      chatSocket.send(
        JSON.stringify({
          message: messageInput,
          username: userUsername,
          room_name: roomName,
        })
      );
      document.querySelector("#my_input").value = ""; // Clear input field after sending
    }
  };

  chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    if (data.type === 'status') {
      // Update user status indicator
      const userItems = document.querySelectorAll('.list-group-item');
      userItems.forEach(item => {
        if (item.querySelector('strong').textContent === data.user) {
          const statusIndicator = item.querySelector('.status-indicator');
          statusIndicator.style.backgroundColor = data.status === 'online' ? '#28a745' : '#dc3545';
          
          // Update status text in chat header if this is the current chat
          if (data.user === roomName) {
            const statusText = document.querySelector('.text-muted');
            if (statusText) {
              statusText.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
            }
          }
        }
      });
      return;
    }

    if (data.message && data.sender) {
      // Display the new message in the chatbox
      const chatbox = document.querySelector("#chatbox");
      const noMessages = document.querySelector(".no-messages");
      if (noMessages) {
        noMessages.style.display = "none";
      }

      const messageContainer = document.createElement("div");
      messageContainer.className = "chat-message " + (data.sender === userUsername ? "sender" : "receiver");
      
      const messageContent = document.createElement("div");
      messageContent.className = "d-flex align-items-center";
      messageContent.innerHTML = `<span>${data.message}</span>`;

      // Add status indicators only for sent messages
      if (data.sender === userUsername) {
        messageContent.appendChild(createStatusIndicator(data.status));
      }

      messageContainer.appendChild(messageContent);
      chatbox.appendChild(messageContainer);
      scrollToBottom();

      // Update the last message in the sidebar
      const lastMessage = document.querySelector(
        ".list-group-item.active #last-message"
      );
      if (lastMessage) {
        lastMessage.innerHTML =
          data.sender === userUsername
            ? "You: " + data.message
            : data.message;

        const timestamp = document.querySelector(".list-group-item.active small");
        const date = new Date().toUTCString();
        timestamp.innerHTML = date.slice(17, 22);

        // Update the chats list sorting
        const chats = document.querySelectorAll(".list-group-item");
        const chatsArray = Array.from(chats);
        const chatsSorted = chatsArray.sort((a, b) => {
          const aTime = a.querySelector("small").innerHTML;
          const bTime = b.querySelector("small").innerHTML;
          return aTime < bTime ? 1 : -1;
        });

        const contacts = document.querySelector(".contacts");
        contacts.innerHTML = "";
        chatsSorted.forEach((chat) => {
          contacts.appendChild(chat);
        });
      }
    }
  };
});