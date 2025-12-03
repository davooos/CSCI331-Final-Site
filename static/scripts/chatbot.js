function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

document.getElementById('chatForm').addEventListener('htmx:beforeRequest', async function () {
    let ul = document.getElementById('all_messages');
    let li_user = document.createElement('li');
    li_user.className = 'user-message';
    li_user.appendChild(document.createTextNode(document.getElementById('userInput').value));
    ul.appendChild(li_user);

    document.getElementById('userInput').value = '';

    await sleep(1000)

    let li_bot = document.createElement('li');
    li_bot.className = 'bot-message';
    li_bot.appendChild(document.createTextNode('...'));
    ul.appendChild(li_bot);
});

document.getElementById('endChat').addEventListener('htmx:beforeRequest', async function () {
    let ul = document.getElementById('all_messages');
    let li_bot = document.createElement('li');
    li_bot.className = 'bot-message';
    li_bot.appendChild(document.createTextNode('...'));
    ul.appendChild(li_bot);
});
