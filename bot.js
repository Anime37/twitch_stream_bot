const tmi = require('tmi.js');
const fs = require('fs');

// Get token
token = ''
try {
    token = fs.readFileSync('./user_data/token', 'utf8');
} catch (err) {
    console.error(err);
}

const opts = {
    identity: {
        username: 'nullptrrrrrrrrrrrrrrtwtich',
        password: token
    },
    channels: [
        'nullptrrrrrrrrrrrrrrrrrrr'
    ]
};

// Create a client with our options
const client = new tmi.client(opts);

// Register our event handlers (defined below)
client.on('message', onMessageHandler);
client.on('connected', onConnectedHandler);

// Connect to Twitch:
client.connect();

last_receive_time = 0;
last_send_time = 0;
const comm_tmo_s = 5;
function onMessageHandler(target, context, msg, self) {
    if (self) { return; } // Ignore messages from the bot
    const commandName = msg.trim();
    console.log(`${context.username}: ${commandName}`);

    const current_time = (Date.now() / 1000);
    if ((last_receive_time && ((last_receive_time + comm_tmo_s) > current_time)) &&
        ((last_send_time + comm_tmo_s) < current_time)) {
        const msg = context.username + ', ' + getRandomThreat();
        client.say(target, msg);
        last_send_time = current_time;
        return;
    }
    last_receive_time = current_time;
    fs.writeFile('chat.txt', `${context.username}:\n${commandName}`, err => {
        if (err) {
            console.error(err);
        }
    });
}

// Called every time the bot connects to Twitch chat
function onConnectedHandler(addr, port) {
    console.log(`* Connected to ${addr}:${port}`);
}

// Read random line from a file
function getRandomThreat() {
    base_line = 'If you keep spamming, I will '
    filePath = 'spam_threats.txt'
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const lines = fileContent.split('\n').filter(line => line.trim() !== '');

    if (lines.length === 0) {
        throw new Error('File is empty or contains only empty lines.');
    }

    const randomIndex = Math.floor(Math.random() * lines.length);
    return base_line + lines[randomIndex];
}