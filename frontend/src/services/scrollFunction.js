export const scrollToBottom = (highlighting, force = false) => {
    if (highlighting) {
        return;
    }
    const chatWindow = document.getElementById('chat-window');
    if (!chatWindow) {
        return;
    }
    
    const distanceFromBottom = chatWindow.scrollHeight - chatWindow.scrollTop - chatWindow.clientHeight;

    if (distanceFromBottom < 100 || force) {
        setTimeout(() => {
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }, 100);
    }
}