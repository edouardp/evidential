from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from evidential.duck import attach_s3_tables, connect


def test_s3_tables_uses_profile_region(monkeypatch) -> None:
    import boto3

    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
    credentials = SimpleNamespace(access_key="key", secret_key="secret", token=None)
    session = Mock(region_name="us-east-1")
    session.get_credentials.return_value.get_frozen_credentials.return_value = credentials
    monkeypatch.setattr(boto3.session, "Session", Mock(return_value=session))
    connection = Mock()
    attach_s3_tables(connection, table_bucket_arn="arn:aws:s3tables:us-east-1:123:bucket/example")
    assert "s3tables.us-east-1.amazonaws.com" in connection.execute.call_args.args[0]


def test_s3_tables_requires_region_without_credential_configuration(monkeypatch) -> None:
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
    with pytest.raises(ValueError, match="region"):
        attach_s3_tables(Mock(), table_bucket_arn="bucket", configure_credentials=False)


def test_explicit_extensions_are_installed_and_loaded(monkeypatch) -> None:
    import duckdb

    connection = Mock()
    monkeypatch.setattr(duckdb, "connect", Mock(return_value=connection))
    assert connect(extensions=("httpfs",)) is connection
    connection.execute.assert_called_once_with("INSTALL httpfs; LOAD httpfs;")
