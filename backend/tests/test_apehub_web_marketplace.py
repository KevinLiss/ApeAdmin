import hashlib
import json
import zipfile
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.plugins.builtin.apehub_web.analysis import PackageValidationError, inspect_package
from src.plugins.builtin.apehub_web.schemas import WalletIn, WithdrawIn
from src.plugins.builtin.apehub_web.services import (
    calc_split,
    calc_withdrawal_fee,
    lempay_md5_sign,
)


def _write_plugin_zip(path, *, member_name="plugin.py", version="1.2.3"):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "plugin.json",
            json.dumps({"name": "sample", "version": version, "entry": "plugin:Plugin"}),
        )
        archive.writestr(member_name, "class Plugin:\n    pass\n")


def test_lempay_signing_matches_documented_ascii_contract():
    params = {
        "pid": 3103,
        "type": "usdt",
        "out_trade_no": "AH10001",
        "money": "12.30",
        "param": "",
        "rawurl": 0,
        "sign_type": "MD5",
    }
    key = "test-key"
    raw = "money=12.30&out_trade_no=AH10001&pid=3103&type=usdttest-key"
    assert lempay_md5_sign(params, key) == hashlib.md5(raw.encode()).hexdigest()


def test_usdt_split_and_withdrawal_fee_keep_eight_decimal_places():
    developer, platform = calc_split(Decimal("19.99"), Decimal("12.5"))
    assert developer == Decimal("17.49125000")
    assert platform == Decimal("2.49875000")
    assert calc_withdrawal_fee(Decimal("100"), "fixed", Decimal("1.5")) == Decimal("1.50000000")
    assert calc_withdrawal_fee(Decimal("100"), "percent", Decimal("0.8")) == Decimal("0.80000000")


def test_zip_inspection_reads_manifest_without_extracting(tmp_path):
    package = tmp_path / "plugin.zip"
    _write_plugin_zip(package)
    report = inspect_package(package)
    assert report["manifest"]["name"] == "sample"
    assert report["manifest"]["version"] == "1.2.3"
    assert report["file_count"] == 2
    assert any(item["path"] == "plugin.py" for item in report["file_tree"])


def test_zip_inspection_rejects_path_traversal(tmp_path):
    package = tmp_path / "unsafe.zip"
    _write_plugin_zip(package, member_name="../escape.py")
    with pytest.raises(PackageValidationError, match="非法路径"):
        inspect_package(package)


@pytest.mark.parametrize("schema", [WalletIn, lambda **data: WithdrawIn(amount="100", **data)])
def test_trc20_address_validation(schema):
    valid = "T" + "1" * 33
    assert schema(address=valid).address == valid if schema is WalletIn else schema(account=valid).account == valid
    with pytest.raises(ValidationError):
        schema(address="0x123") if schema is WalletIn else schema(account="0x123")
