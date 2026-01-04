# 🎵 PersonalAIs (Python Edition) 🤖

**Your Personal Music Assistant based on Spotify and LLM.**

PersonalAIs is an intelligent music recommendation assistant, integrating Spotify API and AI conversation systems. It operates as an MCP (Model Context Protocol) server.

## 🚀 Key Features

*   **🤖 AI Conversation Interface**: Support for text interactions with intelligent suggestions (via MCP).
*   **🎵 Deep Spotify Integration**: Complete user authentication, playback control, and queue management.
*   **😊 Mood-based Recommendations**: Personalized recommendations based on user mood and Spotify profile.
*   **🔧 MCP Toolchain**: Fully compatible with MCP clients.

## 🛠️ Tech Stack

*   **Python**: Core logic.
*   **FastMCP**: MCP server implementation.
*   **Spotipy**: Spotify Web API wrapper.
*   **Pylast**: Last.fm integration.

## 🛠️ Getting Started

### Prerequisites

*   Python >= 3.12
*   [uv](https://docs.astral.sh/uv/) (recommended for package management)
*   Spotify (if possible Premium Account for playback control)

### Installation

1.  **Clone the repository**

2.  **Install dependencies**
    ```bash
    uv sync
    ```

3.  **Configure Environment**
    Copy the example environment file and fill in your API keys:
    ```bash
    cp .env.example .env
    ```
    
    You will need:
    *   **Spotify API Keys**: `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REDIRECT_URI` (from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard))
    *   **Last.fm API Keys**: `LASTFM_API_KEY`, `LASTFM_API_SECRET` (optional, for Last.fm features)

### Running the Application

You can run the MCP server directly using Python:

```bash
uv run python src/main.py
```

Or using an MCP client configured with `mcp_servers_config.yaml`.

## 📂 Project Structure

*   `src/`: Source code for the MCP server and logic.
*   `tests/`: Unit tests.
*   `BLOG/`: Development logs and additional docs.


