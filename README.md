# TogglCheck

Check if all Toggl entries for selected month (current or last) contain pattern (default: `\#[a-z0-9]{5}(\s|$)`)

## Installation

- `pip install -r requirements.txt`
- `cp .env.sample .env`
- fill in your Toggl API key from https://toggl.com/app/profile#reset_api_token in `.env` file

## Usage

`python togglcheck.py`

- without argument list current month
- with argument `last` will list entries for last month

