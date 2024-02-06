document.addEventListener('DOMContentLoaded', function() {
    const inputField = document.getElementById('inputField');
    const sendButton = document.getElementById('sendButton');
    const chatContainer = document.querySelector('.chat-container');
    const options = document.getElementById('options');
  
    // Function to handle sending a message
    function sendMessage() {
      const message = inputField.value.trim();
      if (message) {
        // Create a div element for the message
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.textContent = message;
  
        // Append the message div to the chat container
        chatContainer.appendChild(messageDiv);
  
        // Clear the input field
        inputField.value = '';
  
        // Scroll to the bottom of the chat container
        chatContainer.scrollTop = chatContainer.scrollHeight;
  
        // Hide options
        options.style.display = 'none';
      }
    }
  
    // Event listener for the Enter key in the input field
    inputField.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        sendMessage();
      }
    });
  
    // Event listener for the Send button
    sendButton.addEventListener('click', sendMessage);
  });
  