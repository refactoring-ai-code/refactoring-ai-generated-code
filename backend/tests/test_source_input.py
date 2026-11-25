"""Exercise F03 through FastAPI, the shared F02 state and the real ZIP reader."""

import base64
import io
import json
import secrets
import stat
import zipfile
from hashlib import sha256

import pytest
from backend.api import source_input
from backend.app.main import app
from backend.core.schemas.models import Scope
from backend.core.workflow import Mutation, Workflow
from backend.storage.input_schema import blobs, consents, snapshots
from backend.storage.input_validation import MAX_ENTRIES, MAX_FILE_BYTES
from backend.storage.state_schema import mutations, versions
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select

KINDS = ("terms", "retention", "cloud_transmission", "dynamic_execution")


def policy_decisions():
    return {
        kind: {"version": f"{kind}.test-v1", "granted": kind in ("terms", "retention")}
        for kind in KINDS
    }


@pytest.fixture
async def intake_api(tmp_path, monkeypatch):
    token, other_token = secrets.token_hex(32), secrets.token_hex(32)
    monkeypatch.setenv("GENESIS_DATABASE_PATH", str(tmp_path / "state.db"))
    monkeypatch.setenv(
        "GENESIS_INPUT_ACTOR_DIGESTS",
        json.dumps(
            {
                "actor:owner": sha256(token.encode()).hexdigest(),
                "actor:other": sha256(other_token.encode()).hexdigest(),
            }
        ),
    )
    monkeypatch.setenv(
        "GENESIS_INPUT_POLICY",
        json.dumps(
            {
                "versions": {k: v["version"] for k, v in policy_decisions().items()},
                "retention_days": 1,
            }
        ),
    )
    async with (
        app.router.lifespan_context(app),
        AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client,
    ):
        yield (
            client,
            {"Authorization": "Bearer " + token},
            {
                "Authorization": "Bearer " + other_token,
            },
        )


def encoded(data):
    return base64.b64encode(data).decode("ascii")


def zip_bytes(entries, compression=zipfile.ZIP_STORED):
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=compression) as archive:
        for name, data in entries:
            archive.writestr(name, data)
    return out.getvalue()


def snippet():
    return {
        "kind": "snippet",
        "filename": "Example.java",
        "text": "class Example {}\r\n",
        "consents": policy_decisions(),
    }


async def upload(client, headers, value, key="test-key"):
    return await client.post(
        "/api/projects",
        json=value,
        headers={
            **headers,
            "Idempotency-Key": key,
        },
    )


def count(table):
    with app.state.input_service.snapshots.engine.connect() as db:
        return db.scalar(select(func.count()).select_from(table))


async def test_snippet_creates_owner_only_v0_and_separate_consents(intake_api):
    client, owner, other = intake_api
    payload = snippet()
    payload["selected_language"] = "python"
    payload["consents"]["cloud_transmission"]["granted"] = True
    response = await upload(client, owner, payload)
    assert response.status_code == 201, response.text
    body = response.json()
    path = response.headers["location"]
    entries = body["manifest"]["files"]
    assert body["selected_language"] == "python"
    assert entries[0] == {
        "path": "Example.java",
        "size": len(payload["text"].encode()),
        "sha256": sha256(payload["text"].encode()).hexdigest(),
        "is_source": True,
        "detected_language": "java",
        "access_mode": "owner",
    }
    assert len(body["consents"]) == 4
    recorded = {item["kind"]: item for item in body["consents"]}
    assert recorded["cloud_transmission"]["granted"] is True
    assert recorded["dynamic_execution"]["granted"] is False
    for name, item in recorded.items():
        assert item["policy_version"] == payload["consents"][name]["version"]
        assert item["actor_id"] == "actor:owner"
        assert item["created_at"] == body["created_at"]
        assert item["created_at"].endswith("Z")
    assert (await client.get(path, headers=owner)).json() == body
    for target in (path, path + "/download"):
        assert (await client.get(target, headers=other)).status_code == 404
        assert (await client.get(target, headers={"X-Actor-Id": "actor:owner"})).status_code == 401
    download = await client.get(path + "/download", headers=owner)
    assert download.status_code == 200
    assert download.headers["cache-control"] == "no-store"
    assert download.headers["content-disposition"] == 'attachment; filename="source-v0.zip"'
    assert download.headers["x-genesis-manifest-sha256"] == body["manifest_sha256"]
    with zipfile.ZipFile(io.BytesIO(download.content)) as archive:
        assert archive.namelist() == ["Example.java"]
        assert archive.read("Example.java") == payload["text"].encode()

    state = Workflow(app.state.input_service.snapshots.engine)
    state.create_run(
        Scope(
            project_id=body["project_id"],
            version_id=body["version_id"],
            analysis_id="analysis:integration",
            run_id="run:integration",
            baseline_sha256=body["manifest_sha256"],
            source_revision="a" * 40,
        ),
        Mutation("actor:owner", "create-run"),
    )
    replay = await upload(client, owner, {**payload, "text": "class Other {}"})
    assert replay.status_code == 409
    assert count(versions) == 1
    assert count(consents) == 4
    assert (await upload(client, other, payload)).status_code == 201


async def test_zip_records_exact_archive_and_excludes_files_from_download(intake_api):
    client, owner, _ = intake_api
    archive = zip_bytes(
        [
            ("source/", b""),
            ("source/Example.java", b"class Example {}\r\n"),
            ("node_modules/cache.js", b"ignored"),
            (".env", b"fixture"),
            ("logo.bin", b"\x00\xff"),
        ]
    )
    response = await upload(
        client,
        owner,
        {
            "kind": "zip",
            "data_base64": encoded(archive),
            "consents": policy_decisions(),
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["upload_sha256"] == sha256(archive).hexdigest()
    assert {x["reason"] for x in body["manifest"]["excluded"]} == {
        "potential-credentials",
        "tooling-directory",
        "non-utf8-or-binary",
    }
    store = app.state.input_service.snapshots
    with store.engine.connect() as db:
        assert (
            db.scalar(
                select(blobs.c.data).where(
                    blobs.c.sha256 == body["upload_sha256"],
                )
            )
            == archive
        )
    zipped = await client.get(response.headers["location"] + "/download", headers=owner)
    with zipfile.ZipFile(io.BytesIO(zipped.content)) as repacked:
        assert repacked.namelist() == ["source/Example.java"]
        assert repacked.read("source/Example.java") == b"class Example {}\r\n"


async def test_folder_and_derivatives_preserve_exact_bytes_and_isolate_changes(intake_api):
    client, owner, _ = intake_api
    body = (
        await upload(
            client,
            owner,
            {
                "kind": "folder",
                "consents": policy_decisions(),
                "files": [
                    {"path": "worker.go", "data_base64": encoded(b"package main\r\n")},
                    {"path": "src/main.ts", "data_base64": encoded(b"export {}\n")},
                    {"path": "module.unknown", "data_base64": encoded(b"plain")},
                ],
            },
        )
    ).json()
    assert {f["detected_language"] for f in body["manifest"]["files"]} == {
        "go",
        "typescript",
        "unknown",
    }
    store = app.state.input_service.snapshots
    version = body["version_id"]
    initial_hash, initial_zip = store.download("actor:owner", version)
    with (
        store.workspace("actor:owner", version, "candidate") as candidate,
        store.workspace("actor:owner", version, "final") as final,
    ):
        assert candidate.path != final.path
        assert candidate.baseline_version_id == final.baseline_version_id == version
        assert candidate.baseline_sha256 == final.baseline_sha256 == initial_hash
        (candidate.path / "worker.go").write_bytes(b"changed")
        assert (final.path / "worker.go").read_bytes() == b"package main\r\n"
        (final.path / "worker.go").write_bytes(b"changed differently")
    assert not candidate.path.exists()
    assert not final.path.exists()
    assert store.download("actor:owner", version) == (initial_hash, initial_zip)


@pytest.mark.parametrize(
    "paths",
    [
        ["../outside.txt"],
        ["/absolute.txt"],
        ["dir\\file.txt"],
        ["C:/file.txt"],
        ["dir/A.py", "dir/a.py"],
        ["caf\u00e9.py", "cafe\u0301.py"],
        ["tree", "tree/child.py"],
        ["src/A.py", "SRC/B.py"],
        ["aux.py"],
    ],
)
async def test_unsafe_paths_are_rejected_without_persistence(intake_api, paths):
    client, owner, _ = intake_api
    invalid = zip_bytes([(path, b"fixture") for path in paths])
    response = await upload(
        client,
        owner,
        {
            "kind": "zip",
            "data_base64": encoded(invalid),
            "consents": policy_decisions(),
        },
    )
    assert response.status_code == 422
    assert count(versions) == count(blobs) == count(mutations) == 0
    assert (await upload(client, owner, snippet())).status_code == 201


async def test_archive_member_types_bomb_and_limits(intake_api):
    client, owner, _ = intake_api
    link = zipfile.ZipInfo("fixture-link")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    cases = (
        zip_bytes([(link, b"fixture")]),
        zip_bytes([("repeated.txt", b"A" * 50000)], zipfile.ZIP_DEFLATED),
        zip_bytes([(f"{i}.py", b"") for i in range(MAX_ENTRIES + 1)]),
        zip_bytes([("large.txt", b"x" * (MAX_FILE_BYTES + 1))]),
        zip_bytes([(f"{i}.txt", b"x" * 2_000_000) for i in range(5)], zipfile.ZIP_DEFLATED),
        b"broken archive",
    )
    for archive in cases:
        result = await upload(
            client,
            owner,
            {
                "kind": "zip",
                "data_base64": encoded(archive),
                "consents": policy_decisions(),
            },
        )
        assert result.status_code == 422
    assert count(blobs) == count(versions) == 0


async def test_consent_validation_request_size_and_retry(intake_api, monkeypatch):
    client, owner, _ = intake_api
    payload = snippet()
    omitted = payload["consents"].pop("dynamic_execution")
    assert (await upload(client, owner, payload)).status_code == 422
    payload["consents"]["dynamic_execution"] = omitted
    payload["consents"]["terms"]["version"] = "no-longer-current"
    assert (await upload(client, owner, payload)).status_code == 422
    payload["consents"] = policy_decisions()
    payload["consents"]["retention"]["granted"] = False
    assert (await upload(client, owner, payload)).status_code == 422
    with monkeypatch.context() as scoped:
        scoped.setattr(source_input, "MAX_BODY_BYTES", 15)
        assert (await upload(client, owner, snippet())).status_code == 413
    assert count(mutations) == 0
    assert (await upload(client, owner, snippet())).status_code == 201


async def test_byte_corruption_is_rejected_without_sending_source(intake_api):
    client, owner, _ = intake_api
    uploaded = await upload(client, owner, snippet())
    store = app.state.input_service.snapshots
    with store.engine.begin() as db:
        db.execute(blobs.update().values(data=b"private-corrupt-sample"))
    r = await client.get(uploaded.headers["location"] + "/download", headers=owner)
    assert r.status_code == 503
    assert "private-corrupt-sample" not in r.text


async def test_retention_denies_reads_and_purges_only_unreferenced_bytes(intake_api):
    client, owner, other = intake_api
    a = await upload(client, owner, snippet())
    b = await upload(client, other, snippet())
    store = app.state.input_service.snapshots
    assert count(blobs) == 1
    with store.engine.begin() as db:
        db.execute(
            snapshots.update()
            .where(snapshots.c.version_id == a.json()["version_id"])
            .values(expires_at="2000-01-01T00:00:00.000000Z")
        )
    assert (await client.get(a.headers["location"], headers=owner)).status_code == 404
    assert store.purge_expired() == 1
    assert store.purge_expired() == 0
    assert count(versions) == 2 and count(consents) == 8 and count(blobs) == 1
    other_read = await client.get(b.headers["location"] + "/download", headers=other)
    assert other_read.status_code == 200


async def test_default_app_disables_intake_without_policy(monkeypatch):
    monkeypatch.delenv("GENESIS_INPUT_POLICY", raising=False)
    monkeypatch.delenv("GENESIS_INPUT_ACTOR_DIGESTS", raising=False)
    async with (
        app.router.lifespan_context(app),
        AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client,
    ):
        assert (await upload(client, {}, snippet())).status_code == 503
        assert (await client.get("/health/live")).status_code == 200


async def test_concurrent_upload_keys_create_one_snapshot(intake_api):
    import asyncio

    client, owner, _ = intake_api
    results = await asyncio.gather(*(upload(client, owner, snippet()) for _ in range(2)))
    assert sorted(x.status_code for x in results) == [201, 409]
    assert count(versions) == count(blobs) == count(mutations) == 1
    assert count(consents) == 4


def test_existing_f02_database_upgrades_without_changing_its_v0(tmp_path):
    from pathlib import Path

    from alembic import command
    from alembic.config import Config
    from backend.storage.database import migrate_state, state_engine, state_write

    engine = state_engine(tmp_path / "existing.db")
    try:
        config = Config()
        location = Path(__file__).resolve().parents[1] / "storage" / "migrations"
        config.set_main_option("script_location", location.as_posix().replace("%", "%%"))
        with state_write(engine) as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "0001_state")
        Workflow(engine).register_version(
            "project:legacy",
            "version:legacy",
            "version:legacy",
            "a" * 64,
            Mutation("actor:legacy", "create-legacy"),
        )
        migrate_state(engine)
        with engine.connect() as db:
            row = db.execute(select(versions)).mappings().one()
            assert row["id"] == "version:legacy" and row["manifest_sha256"] == "a" * 64
            assert db.scalar(select(func.count()).select_from(snapshots)) == 0
    finally:
        engine.dispose()
