document.addEventListener('DOMContentLoaded',()=>{
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    
    socket.on('connect', ()=>{
      socket.emit('joined');
      
      document.querySelector('#join_channel').onclick = ()=>{
        localStorage.removeItem('last_channel');
      }
      
      // When user leaves channel redirect to '/'
      document.querySelector('#leave_channel').addEventListener('click', () => {

          // Notify the server user has left
          socket.emit('left');

          localStorage.removeItem('last_channel');
          window.location.replace('/');
      })

      // Forget user's last channel when logged out
      document.querySelector('#logout').addEventListener('click', () => {
          localStorage.removeItem('last_channel');
      });

      // 'Enter' key on textarea also sends a message
      // https://developer.mozilla.org/en-US/docs/Web/Events/keydown
      document.querySelector('#message').addEventListener("keydown", event => {
          if (event.key == "Enter") {
              document.getElementById("msg_send_btn").click();
          }
      });
      
      // Send button emits a "message sent" event
      document.querySelector('#msg_send_btn').addEventListener("click", () => {
          
          // Save time in format HH:MM:SS
          let timestamp = new Date;
          timestamp = timestamp.toLocaleTimeString();

          // Save user input
          let msg = document.getElementById("message").value;

          socket.emit('send message', msg, timestamp);
          
          // Clear input
          document.getElementById("message").value = '';
      });
  });
  
  // When user joins a channel, add a message and on users connected.
  socket.on('status', data => {

      // Broadcast message of joined user.

      let message = `${data.msg}`;

      document.querySelector('#joinedmessage').innerHTML = message

      // Save user current channel on localStorage
      localStorage.setItem('last_channel', data.channel)
  })

  // When a message is announced, add it to the textarea.
  socket.on('announce message', data => {
      // Format message
    document.querySelector('#time').innerHTML = `${data.timestamp}`;
    document.querySelector('#textmsg').innerHTML = `${data.msg}`;
    document.querySelector('#uname').innerHTML = `${data.name}`;
  })

    });
