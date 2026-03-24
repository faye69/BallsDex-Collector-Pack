# BallsDex V3 Collector Package

Collector card system for **BallsDex V3**. Players collect enough of a specific collectible to earn tiered cards (Bronze, Silver, Gold, etc.). Each card is permanently untradeable and auto-revoked if the player drops below the threshold.

## Installation

### 1 — Configure extra.toml

**If the file doesn't exist:** Create a new file `extra.toml` in your `config` folder under the BallsDex directory.

**If you already have other packages installed:** Simply add the following configuration to your existing `extra.toml` file. Each package is defined by a `[[ballsdex.packages]]` section, so you can have multiple packages installed.

Add the following configuration:

```toml
[[ballsdex.packages]]
location = "git+https://github.com/YOUR_USERNAME/YOUR_REPO.git"
path = "collector.collector"
enabled = true
editable = false
```

**Example of multiple packages:**

```toml
# First package
[[ballsdex.packages]]
location = "git+https://github.com/example/other-package.git"
path = "other"
enabled = true
editable = false

# Collector Package
[[ballsdex.packages]]
location = "git+https://github.com/YOUR_USERNAME/YOUR_REPO.git"
path = "collector.collector"
enabled = true
editable = false
```

### 2 — Fix the migration dependency

Find your latest `bd_models` migration:

```bash
python admin_panel/manage.py showmigrations bd_models
```

Open this file:

```
.venv/lib/python3.x/site-packages/collector/migrations/0001_initial.py
```

Find the `dependencies` block and replace `"0001_initial"` with the last migration name from the command above:

```python
dependencies = [
    ("bd_models", "0001_initial"),  # ← replace this with your latest
]
```

### 3 — Register the Django app

In your settings file (e.g. `admin_panel/settings/production.py`):

```python
INSTALLED_APPS += ["collector"]
```

### 4 — Register the bot package

In `ballsdex/core/bot.py`, add to `DEFAULT_PACKAGES`:

```python
("collector", "collector.collector"),
```

### 5 — Run migrations

```bash
python admin_panel/manage.py migrate
```

### 6 — Restart the bot

`collector` will appear in the packages loaded log. Admin commands (`/admin collector`) wire up automatically — no extra steps needed.
