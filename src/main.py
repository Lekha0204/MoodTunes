#!/usr/bin/env python3
"""
Spotify MCP Server Main Program
Using fastmcp library
"""

import os
import asyncio
# from dotenv import load_dotenv
from spotify_client import SpotifySuperClient as SpotifyClient
from mcp_server import SpotifyMCPSuperServer as SpotifyMCPServer, SpotifyMCPSuperServerV2
from lastfm_client import LastfmClient
from llm_client import LLMClient
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """main"""
    # Load environment variables
    load_dotenv()
    
    # Get Spotify API configuration
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
    lastfm_api_key = os.getenv("LASTFM_API_KEY")
    lastfm_api_secret = os.getenv("LASTFM_API_SECRET")
    
    # LLM Configuration
    llm_provider = os.getenv("LLM_PROVIDER", "ollama")
    # dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
    username = os.getenv("SPOTIFY_USERNAME")

    logger.info(f"""
    client_id: {client_id}
    client_secret: {client_secret}
    redirect_uri: {redirect_uri}
    lastfm_api_key: {lastfm_api_key}
    lastfm_api_secret: {lastfm_api_secret}
    llm_provider: {llm_provider}
    username: {username}
    """)
    
    # Validate Core Dependencies
    required_vars = [client_id, client_secret, redirect_uri, lastfm_api_key, lastfm_api_secret, username]
    missing_vars = []
    
    if not all(required_vars):
        missing_vars.extend(["SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "SPOTIFY_REDIRECT_URI", "LASTFM_API_KEY", "LASTFM_API_SECRET", "SPOTIFY_USERNAME"])
        
    # Validate LLM Provider specific deps
    # if llm_provider == 'dashscope' and not dashscope_api_key:
    #     missing_vars.append("DASHSCOPE_API_KEY")

    # if missing_vars:
    #     logger.info("Error: Please set the following environment variables:")
    #     for var in missing_vars:
    #         logger.info(f"- {var}")
    #     return
    
    try:
        # Create Spotify client
        logger.info("Initializing Spotify client...")
        spotify_client = SpotifyClient(client_id, client_secret, redirect_uri, username)
        logger.info("Spotify client initialized successfully!")
        
        # Create Lastfm client
        logger.info("Initializing Lastfm client...")
        lastfm_client = LastfmClient(lastfm_api_key, lastfm_api_secret)
        logger.info("Lastfm client initialized successfully!")
        
        # Create LLM client
        logger.info(f"Initializing LLM client ({llm_provider})...")
        llm_client = LLMClient(api_key=os.getenv("DASHSCOPE_API_KEY"), provider=llm_provider)
        logger.info("LLM client initialized successfully!")
        
        # Create MCP server
        logger.info("Starting MCP server...")
        # mcp_server = SpotifyMCPServer(spotify_client, lastfm_client, llm_client)
        mcp_server = SpotifyMCPSuperServerV2(spotify_client, lastfm_client, llm_client)
        logger.info("MCP server initialized successfully!")
        
        # Run server
        logger.info("MCP server started, waiting for connections...")
        logger.info("Using fastmcp library, supporting more concise API")
        
        # Check if event loop is already running
        mcp_server.run()
        
    except Exception as e:
        logger.info(f"Startup failed: {e}")
        logger.info("\nPlease ensure:")
        logger.info("1. Spotify API credentials are correctly set")
        logger.info("2. All dependencies are installed: uv sync")
        logger.info("3. Network connection is normal")


if __name__ == "__main__":
    main()