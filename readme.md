# REDDIT BOT SYSTEM

## OVERVIEW
The Reddit Bot System is a multi-account automated bot framework built using Python, PRAW, and OpenAI's API. Each bot is tied to a unique Reddit account and can be configured with its own personality and knowledge base. The system is designed to post and reply to Reddit threads by generating dynamic, context-aware content via an external content provider (e.g., OpenAI).

## TABLE OF CONTENTS
1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Components and Interactions](#components-and-interactions)
   - [Configuration](#1-configuration)
   - [Account Manager](#2-account-manager)
   - [RedditBot](#3-redditbot)
   - [Bot Manager](#4-bot-manager)
   - [OpenAI Provider](#5-openai-provider)
   - [Main Script](#6-main-script)
   - [Tests](#7-tests)
4. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Configuration](#configuration)
   - [Running the Program](#running-the-program)
   - [Running the Tests](#running-the-tests)
5. [Customization](#customization)
6. [Contributing](#contributing)
7. [License](#license)

## COMPONENTS AND INTERACTIONS

### 1. CONFIGURATION
- **Files:** `config/config.yaml`, `config/config.py`
- **Purpose:**  
  Defines all settings required by the bot system. This includes:
  - Reddit account credentials
  - Target subreddits
  - Posting and reply intervals
  - OpenAI API key and custom prompts
  - Per-account personality settings (unique description and memory)
- **Usage:**  
  Update `config.yaml` with your details before running the program.

### 2. ACCOUNT MANAGER
- **File:** `core/account_manager.py`
- **Purpose:**  
  Initializes and manages multiple Reddit API instances using PRAW (one per account).
- **Functionality:**  
  Uses a round-robin mechanism (with a threading lock if needed) to supply a Reddit instance.

### 3. REDDITBOT
- **File:** `bots/reddit_bot.py`
- **Purpose:**  
  The unified bot class that can post new content and reply to existing submissions on Reddit.
- **Features:**  
  - Uses a dedicated Reddit instance per account.
  - Incorporates a content provider (e.g., OpenAIProvider) for AI-generated content.
  - Executes commands via its `handle_command` method.
  - Stores its username for identification.

### 4. BOT MANAGER
- **File:** `core/bot_manager.py`
- **Purpose:**  
  Instantiates and manages one RedditBot per configured account.
- **Functionality:**  
  - Reads per-account personality settings from the configuration file.
  - Initializes a content provider for each bot.
  - Provides methods to execute commands for all bots or a specific bot (targeted by username).

### 5. OPENAI PROVIDER
- **File:** `providers/openai_provider.py`
- **Purpose:**  
  Integrates with OpenAI's API to generate dynamic post and reply content.
- **Features:**  
  - Uses customizable prompts along with personality and memory to generate context-aware content.
  - For reply generation, collects the entire thread context (original post and parent comments) for a comprehensive prompt.

### 6. MAIN SCRIPT
- **File:** `main.py`
- **Purpose:**  
  Acts as the entry point for the application.
- **Functionality:**  
  Loads configuration, initializes the Account Manager and Bot Manager, and demonstrates how to execute commands (e.g., posting, replying, targeted commands).

### 7. TESTS
- **Directory:** `tests/`
- **Purpose:**  
  Contains pytest files to verify the functionality of each module without making actual API calls or Reddit posts.
- **Key Test Files:**  
  - `test_config.py`: Verifies configuration loading.
  - `test_account_manager.py`: Tests account retrieval and round-robin mechanism.
  - `test_openai_provider.py`: Ensures content generation (including thread context collection) works as expected.
  - `test_reddit_bot.py`: Tests the RedditBot's post and reply methods.
  - `test_bot_manager.py`: Tests the Bot Manager's ability to instantiate bots and execute commands (both globally and targeted).

## GETTING STARTED

### Prerequisites
- Python 3.8 or later.
- Reddit API credentials from your Reddit developer account.
- OpenAI API key (if using OpenAI for content generation).

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/reddit_bot.git
   cd reddit_bot
   ```

2. Install required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Configuration
1. Open `config/config.yaml` and update the following sections:
   - **Accounts:** Add your Reddit account details.
   - **Subreddits:** List the subreddits you want the bots to interact with.
   - **OpenAI Settings:** Insert your OpenAI API key and customize the `post_prompt` and `reply_prompt`.
   - **Personalities:** For each account (keyed by username), set a unique personality (`description`) and knowledge (`memory`).

### Running the Program
Run the main script to start the bot system:
   ```sh
   python main.py
   ```

The system will:
- Load your configuration.
- Initialize Reddit API instances for each account.
- Create a RedditBot for each account with its unique personality.
- Execute sample commands (e.g., posting across all bots).

To target a specific bot to reply to a particular thread, modify `main.py` or use the Bot Manager's `execute_command_for_bot` method as needed.

### Running the Tests
To run all tests, use:
   ```sh
   pytest
   ```

This will execute tests from the `tests/` directory. The tests use monkeypatching and dummy classes to simulate API calls, so no real posts or OpenAI requests are made.

## CUSTOMIZATION
- **Personality & Memory:**  
  Customize each bot's behavior by modifying the personalities section in `config/config.yaml`. This influences the content generated by the OpenAI provider.
- **OpenAI Prompts:**  
  Adjust the `post_prompt` and `reply_prompt` in `config/config.yaml` to tailor how posts and replies are generated.
- **Thread Context in Replies:**  
  The OpenAI provider gathers the entire thread context for generating context-aware replies. You can modify this behavior in `providers/openai_provider.py` if needed.

## CONTRIBUTING
Contributions are welcome!
- If you find a bug or have a feature request, please open an issue or submit a pull request.
- When contributing:
  - Include tests for new features.
  - Update this README if changes affect usage or configuration.

## LICENSE
This project is licensed under the MIT License.
