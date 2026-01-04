document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');
    const userProfileEl = document.getElementById('user-profile');
    const playlistListEl = document.getElementById('playlist-list');
    const nowPlayingEl = document.getElementById('now-playing');

    // State
    let isWaitingForResponse = false;

    // --- Init ---
    fetchUserProfile();
    fetchPlaylists();
    fetchNowPlaying();
    setInterval(fetchNowPlaying, 5000); // Polling for now playing

    // --- Event Listeners ---
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // --- Chat Functions ---
    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text || isWaitingForResponse) return;

        // Add User Message
        addMessage(text, 'user');
        chatInput.value = '';
        
        isWaitingForResponse = true;
        sendBtn.disabled = true;

        // Add Loading bubble
        const loadingId = addLoadingMessage();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            
            const data = await response.json();
            
            // Remove loading and add response
            removeMessage(loadingId);
            addMessage(data.response, 'system');
        } catch (error) {
            console.error('Chat error:', error);
            removeMessage(loadingId);
            addMessage('Sorry, something went wrong with the connection.', 'system');
        } finally {
            isWaitingForResponse = false;
            sendBtn.disabled = false;
        }
    }

    function addMessage(text, type) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${type}`;
        
        const icon = type === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';
        
        // Convert newlines to br for simple formatting
        const formattedText = text.replace(/\n/g, '<br>');

        msgDiv.innerHTML = `
            <div class="avatar">${icon}</div>
            <div class="bubble">${formattedText}</div>
        `;
        
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addLoadingMessage() {
        const id = 'msg-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = `message system`;
        msgDiv.id = id;
        msgDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="bubble"><i class="fa-solid fa-ellipsis fa-bounce"></i></div>
        `;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    // --- Spotify Data Functions ---
    async function fetchUserProfile() {
        try {
            const res = await fetch('/api/me');
            const data = await res.json();
            
            const imgUrl = data.images && data.images.length > 0 ? data.images[0].url : null;
            const imgHtml = imgUrl 
                ? `<img src="${imgUrl}" class="user-avatar" alt="Avatar">`
                : `<div class="user-avatar" style="display:flex;align-items:center;justify-content:center"><i class="fa-solid fa-user"></i></div>`;

            userProfileEl.innerHTML = `
                ${imgHtml}
                <div class="user-name">${data.display_name}</div>
            `;
        } catch (e) {
            console.error('Profile load error', e);
            userProfileEl.innerHTML = '<div style="color:red">Failed to load profile</div>';
        }
    }

    async function fetchPlaylists() {
        try {
            const res = await fetch('/api/playlists');
            const data = await res.json();
            
            playlistListEl.innerHTML = '';
            data.items.forEach(pl => {
                const li = document.createElement('li');
                li.textContent = pl.name;
                li.title = pl.name; // Tooltip
                playlistListEl.appendChild(li);
            });
        } catch (e) {
            console.error('Playlist load error', e);
            playlistListEl.innerHTML = '<li style="color:red">Error loading playlists</li>';
        }
    }

    async function fetchNowPlaying() {
        try {
            const res = await fetch('/api/now_playing');
            const data = await res.json();
            
            if (data.is_playing === false || !data.item) {
                // Not playing
                updatePlayerState(null);
                return;
            }
            updatePlayerState(data);

        } catch (e) {
            console.error('Now playing error', e);
        }
    }

    function updatePlayerState(data) {
        const artContainer = nowPlayingEl.querySelector('.album-art');
        const trackNameEl = nowPlayingEl.querySelector('.track-name');
        const artistNameEl = nowPlayingEl.querySelector('.artist-name');
        const progressBar = nowPlayingEl.querySelector('.progress');

        if (!data) {
            artContainer.innerHTML = '<i class="fa-solid fa-music"></i>';
            trackNameEl.textContent = 'Not Playing';
            artistNameEl.textContent = '-';
            progressBar.style.width = '0%';
            return;
        }

        const track = data.item;
        const imgUrl = track.album.images[0]?.url;
        
        artContainer.innerHTML = `<img src="${imgUrl}" alt="Album Art">`;
        trackNameEl.textContent = track.name;
        artistNameEl.textContent = track.artists.map(a => a.name).join(', ');
        
        // Update progress
        if (data.progress_ms && track.duration_ms) {
            const pct = (data.progress_ms / track.duration_ms) * 100;
            progressBar.style.width = `${pct}%`;
        }
    }
});
