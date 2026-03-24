# BallsDex V3 Collector Package

Collector card system for **BallsDex V3**. Players collect enough of a specific collectible to earn tiered cards (Bronze, Silver, Gold, etc.). Each card is permanently untradeable and auto-revoked if the player drops below the threshold.

## Commands

**Players**
| Command | Description |
|---|---|
| `/collector list` | All collectibles and their tier thresholds, sorted by rarity |
| `/collector info <collectible>` | All tiers for one collectible with your count and status |
| `/collector check <collectible>` | Same as info but only visible to you |
| `/collector claim <collectible> <tier>` | Claim a card — pick collectible first, then tier |
| `/collector mycards` | All your claimed collector cards |
| `/collector leaderboard` | Top 10 players by cards claimed |

**Staff**
| Command | Description |
|---|---|
| `/admin collector give @user <tier> <collectible>` | Give a card bypassing requirements |
| `/admin collector remove @user <tier> <collectible>` | Remove a card and delete the awarded instance |
| `/admin collector check @user` | List all cards a player owns |
| `/admin collector refresh` | Trigger the revoke check immediately |

Auto-revoke runs every **10 minutes** — revokes cards, soft-deletes the awarded instance, and DMs the player.

## Admin panel setup

**Step 1 — Create a Special**
Go to **Special events → Add Special**. Set a name (e.g. `Bronze Collector`), uncheck Tradeable, leave dates blank, and upload your background image.

**Step 2 — Create the tier**
Go to **Collector → Collector Tiers → Add**. Set a name (`Bronze`), optional emoji (`🥉`), link the Special, and leave Enabled checked.

**Step 3 — Add per-ball thresholds**
In the **Per-ball thresholds** inline table, add one row per collectible: select the collectible and set the count required. Save.

Repeat for each tier. After any change, run `@YourBot reloadcache` in Discord.

## Notes

- Uses BallsDex models (`Ball`, `BallInstance`, `Player`, `Special`) — no custom fields required.
- Admin commands (`/admin collector`) wire up automatically when the package loads; no changes to the admin cog needed.
- The awarded `BallInstance` has `tradeable=False` permanently.
- Auto-revoke excludes the awarded card instance from the count so it does not count against itself.
