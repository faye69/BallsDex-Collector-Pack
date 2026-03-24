# BallsDex V3 Collector Package

Collector card system for **BallsDex V3**. Players collect enough of a specific collectible to earn tiered cards (Bronze, Silver, Gold, etc.). Each card is permanently untradeable and auto-revoked if the player drops below the threshold.

## Installation

### 1 — Configure extra.toml

**If the file doesn't exist:** Create a new file `extra.toml` in your `config` folder under the BallsDex directory.

**If you already have other packages installed:** Simply add the following configuration to your existing `extra.toml` file. Each package is defined by a `[[ballsdex.packages]]` section, so you can have multiple packages installed.

Add the following configuration:

```toml
[[ballsdex.packages]]
location = "git+https://github.com/faye69/BallsDex-Collector-Pack.git"
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
location = "git+https://github.com/faye69/BallsDex-Collector-Pack.git"
path = "collector.collector"
enabled = true
editable = false
```

### 2 — Run migrations

```bash
python admin_panel/manage.py migrate
```

### 3 — Restart the bot

`collector` will appear in the packages loaded log. Admin commands (`/admin collector`) wire up automatically — no extra steps needed.
