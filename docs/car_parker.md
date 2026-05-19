# Car Parker

A LAN-resident parking reminder for San Francisco street-sweeping rules,
exposed inside Home Assistant. Captures GPS from your phone, asks you to
confirm the block and side of the street, then surfaces the next sweeping
window and any applicable time-limit regulations.

## Architecture

```
            ┌────────────────────────────────────────────────────────────┐
            │                                                            │
   📱 lugh ──┤── (HA mobile app, push + actionable notifications)         │
            │                                                            │
            ▼                                                            │
   ┌───────────────────┐   coordinator polls /api/status every 60s       │
   │  ha-home  (Pi)    │ ──────────────────────────────────────────────► │
   │  HA OS 2026.5     │                                                 │
   │                   │   service calls → POST /api/park/*              │
   │  custom_components│ ──────────────────────────────────────────────► │
   │   /car_parker/    │                                                 │
   │                   │                                              ┌──┴───────────────┐
   │  dashboards/      │                                              │  loki (Debian)   │
   │   parking.yaml    │                                              │                  │
   └───────────────────┘                                              │  car-parker      │
                                                                      │  Flask/gunicorn  │
                                                                      │  systemd:5050    │
                                                                      │                  │
                                                                      │  data/           │
                                                                      │   sweeping.json  │
                                                                      │   regs.geojson   │
                                                                      └──────────────────┘
                                                                              ▲
                                                                              │
                                                                       weekly sync
                                                                              │
                                                                      DataSF (yhqp-riqs,
                                                                      hi6h-neyh)
```

All hosts are on a Tailscale tailnet so the phone can reach HA when off-LAN.
Inside the LAN, HA talks to the API by IP (`192.168.0.3:5050`) because HA's
bundled aiohttp uses an aiodns resolver that doesn't speak mDNS — so
`loki.local` would silently time out from inside HA.

## Components

| Path | Role |
|---|---|
| `car_parker_api/` | Flask + gunicorn HTTP API. Reads SF data, computes nearby blocks, holds the parking state file. Runs on loki. |
| `custom_components/car_parker/` | Home Assistant custom integration. Polls `/api/status` and exposes entities + services. |
| `ha_config/dashboards/parking.yaml` | The "Parking" dashboard. YAML mode, uses HACS `custom:button-card` for dynamic candidate/side buttons. |
| `ha_config/configuration.yaml.partial` | Snippet to add to HA's `configuration.yaml` to register the dashboard. |
| `reference/car_parker/` | Frozen snapshot of the original app from zephyr. |

## The park flow

```
empty
  │
  │   service: car_parker.park_here
  │   (or POST /api/park/tentative with lat/lng)
  ▼
pending / stage=pick_block
  │
  │   service: car_parker.pick_block { street, limits }
  │   (or POST /api/park/pick_block)
  ▼
pending / stage=pick_side
  │
  │   service: car_parker.confirm_side { side }
  │   (or POST /api/park/confirm)
  ▼
parked
  │
  │   service: car_parker.clear
  │   (or POST /api/clear)
  ▼
empty
```

GPS alone isn't enough to know which side of a street you're on — and even
the block can be ambiguous near corners. The pick_block stage shows up to 5
nearby blocks (within 80m of your GPS fix) so you confirm where you actually
are. The pick_side stage then only offers the sides that are valid for
*that* block (e.g. E/W for north-south streets).

The server validates both the chosen block (must be among the original
candidates) and the chosen side (must be among the block's sides). The
dashboard's dynamic side buttons also reflect this — only valid directions
are shown.

## Manual entry

A free-text field at the bottom of the dashboard calls
`car_parker.park_manual`, which feeds the input through a regex parser.
Recognized phrasings:

- `Anza between 7th and 8th, north side`
- `north side of 9th Ave between Cabrillo and Fulton`
- `9th Ave between Geary and Anza west` (side suffix without "side")
- `9th Ave between Geary and Anza` (side defaults to Unknown)

The parser:
1. Normalizes ordinal avenues (`9th` → `09th`) and street suffixes
   (`ave` → `Ave`).
2. Extracts the side phrase as a pre-pass (prefix or trailing form) and
   strips it from the input.
3. Matches the remaining text against the block patterns.
4. Looks up the chosen block among the candidates for the matched street.

## Data sources

Both come from DataSF and are synced by `car_parker_api/sync.py`. They use
Socrata's `rowsUpdatedAt` timestamp so re-runs are cheap.

| Dataset | ID | File | Approx size |
|---|---|---|---|
| Street sweeping schedule | `yhqp-riqs` | `data/street_sweeping_sf.json` | 25 MB / ~37 k records |
| Parking regulations (non-color-curb) | `hi6h-neyh` | `data/parking_regulations_sf.geojson` | 10 MB / ~7.8 k features |

The geojson is used for the time-limit lookup (RPP exemptions, hourly
limits). The sweeping JSON has line geometry plus per-blockface schedule
records (weekday, week-of-month, hours, holidays).

## HA entities & services

### Entities

| Entity | Description |
|---|---|
| `binary_sensor.car_parked` | On when fully parked. |
| `binary_sensor.car_parker_needs_side_confirmation` | On during pending state. |
| `binary_sensor.move_car_now` | On when sweeping is imminent (urgency=urgent or now). `device_class: problem`. |
| `sensor.car_parker_status` | `empty` / `pending` / `parked`. Carries the entire payload as attributes (stage, candidates, chosen_block, candidate_sides, time_limit, location, next_sweeping, lat, lng). |
| `sensor.car_parker_urgency` | `safe` / `soon` / `urgent` / `now` / `awaiting_side`. |
| `sensor.next_street_sweep` | Timestamp of the next sweeping window. |
| `sensor.next_street_sweep_label` | Human-readable, e.g. "tomorrow 8am–10am". |
| `sensor.parked_location` | Joined street + block + side; attributes include split fields. |
| `sensor.parking_time_limit` | E.g. "2-hour parking 9am–6pm (M-F)". |

### Services

| Service | Notes |
|---|---|
| `car_parker.park_here` | Accepts `latitude`/`longitude` directly, or an `entity_id` (reads lat/lng from a `person` or `device_tracker` attributes). |
| `car_parker.pick_block` | `street` + optional `limits`. Must match a candidate from the current pending state. |
| `car_parker.confirm_side` | `side` ∈ {North, South, East, West}. |
| `car_parker.park_manual` | `text` for free-text parser, or `street`/`block`/`side` for structured input. |
| `car_parker.clear` | Returns to empty state. |

Service handlers call `coord.async_refresh()` (not `async_request_refresh`)
so entities update instantly after a mutation rather than waiting up to 10s
for the coordinator's debouncer.

## Deployment

### car_parker_api → loki

```sh
# Sync source (excluding venv and the cached data files)
rsync -av --exclude=venv --exclude=__pycache__ \
  --exclude='data/*.json' --exclude='data/*.geojson' \
  --exclude='data/parking_state.json' \
  car_parker_api/ loki.local:/opt/car-parker/

# First time: set up venv and fetch data
ssh loki.local '
  cd /opt/car-parker
  python3 -m venv venv
  venv/bin/pip install -r requirements.txt
  venv/bin/python sync.py
'

# Install systemd unit (one-time)
# See /etc/systemd/system/car-parker.service on loki — runs:
#   /opt/car-parker/venv/bin/gunicorn -w 1 -b 0.0.0.0:5050 app:app

ssh loki.local 'sudo systemctl restart car-parker'
```

### HA integration → ha-home

```sh
# Tar-pipe over ssh; HA OS doesn't ship rsync
tar cf - -C custom_components car_parker \
  | ssh root@ha-home 'cd /config/custom_components && tar xf -'
ssh root@ha-home 'ha core restart'
```

After first install, add the integration via HA's UI:
Settings → Devices & Services → Add Integration → "Car Parker".

### Dashboard → ha-home

```sh
scp ha_config/dashboards/parking.yaml \
  root@ha-home:/config/dashboards/parking.yaml
```

To register the dashboard the first time, append the contents of
`ha_config/configuration.yaml.partial` to `/config/configuration.yaml`,
then `ha core check && ha core restart`. The dashboard URL slug must
contain a hyphen (HA's lovelace validator requires this), hence
`car-parker` rather than `parking`.

### Prerequisites on HA

- **HACS** with `custom:button-card` installed (Frontend section).
- **`input_text.car_parker_manual_text`** helper for the manual entry
  field — defined in `automations/keypad_helpers.yaml` (the existing
  shared `input_text:` include file).
- **`person.<you>`** entity with the HA Companion app reporting GPS, so
  `car_parker.park_here` has lat/lng attributes to read from.

## Known limitations / follow-ups

- **Time-limit threshold.** Currently 25m radius from the GPS point. After
  `pick_block`, the time limit could be re-looked-up using the chosen
  block's geometry for a more reliable answer. Right now if the regulation
  isn't within 25m of your raw GPS fix, no time limit is reported.
- **Spatial-index perf.** Geo lookups are a linear scan over ~7-37k
  features with a coarse midpoint pre-filter (~50ms per call). Drop-in
  `rtree` would push this to <1ms; PostGIS would unlock proper spatial
  joins. Not yet a bottleneck.
- **Parser brittleness.** Free-text manual entry handles common phrasings
  but isn't exhaustive. Hit something that doesn't parse? File it and we
  add a pattern.
- **Single-user.** State file holds one parked location. Multi-vehicle
  would mean either separate state files per vehicle or a vehicle ID in
  state.
- **Actionable push notifications** for "which side?" aren't wired yet —
  the dashboard handles this for now. Phone-side automation would push
  with side buttons when status flips to pending.

## Related Tailscale & HA notes

- Tailnet: `tail51b1d6.ts.net`. Devices: `loki`, `ha-home`, `lugh`
  (phone), `styx` (laptop).
- The HA mobile app's external URL is set to
  `http://ha-home.tail51b1d6.ts.net:8123` so notifications and the app
  work off-LAN. Internal URL stays `http://homeassistant.local:8123`.
- The Tailscale add-on on the HA Pi joins the tailnet but doesn't
  configure HA's internal DNS to use Tailscale's resolver, which is why
  the integration uses loki's LAN IP rather than the tailnet hostname.
