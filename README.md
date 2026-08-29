# wall-tidbits

Daily content gateway for reTerminal and other e-paper displays. It combines a
Wiktionary word of the day, Wikipedia's On This Day and Did You Know feeds, and
a deterministic local riddle into JSON and e-paper-friendly HTML.

## Local deployment

Copy the example environment file and set a long random token:

```sh
cp .env.example .env
openssl rand -hex 32
```

Put the generated value in `PUBLIC_TOKEN`, then start the service:

```sh
docker compose up --build --detach
```

Check that it is healthy:

```sh
curl http://127.0.0.1:8080/healthz
```

The display endpoints are:

- `/v1/display.html`
- `/v1/display.json`
- `/v1/daily`
- `/v1/credits`
- `/e/<PUBLIC_TOKEN>/display.html`

The service writes its cache under `data/cache`. The cache is intentionally
ignored by Git and survives container restarts through the `./data:/data`
volume. If the host data directory is not owned by UID/GID 1000, set
`WALL_TIDBITS_UID` and `WALL_TIDBITS_GID` in `.env` to match its owner.

## LAN deployment from GHCR

The GitHub Actions workflow publishes `main` as `latest`, version tags such as
`v0.1.0` as semver tags, and every build with a commit SHA tag. On the LAN host,
set the image in `.env`:

```dotenv
WALL_TIDBITS_IMAGE=ghcr.io/mitchins/wall-tidbits:latest
```

Then pull and start it:

```sh
docker compose pull
docker compose up --detach
```

If the package is private, authenticate the host to GHCR before pulling. The
container listens on port 8080 internally; set `PORT` in `.env` to choose the
host port.

## Development

```sh
python -m pip install -e ".[dev]"
pytest -q
ruff check .
```

Pull requests run tests, linting, and a container build. Pushes to `main` and
version tags publish the container to GHCR. CodeRabbit is configured to review
ready, non-draft pull requests automatically; the CodeRabbit GitHub app must be
enabled for the repository.
