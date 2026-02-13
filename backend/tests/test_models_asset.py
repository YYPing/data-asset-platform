from app.models.organization import Organization  # noqa: F401 - needed for relationship resolution
from app.models.asset import DataAsset, AssetStage, STAGE_ORDER
from app.models.stage import StageRecord, StageStatus
from app.models.material import StageMaterial


def test_asset_stage_enum():
    assert AssetStage.RESOURCE_INVENTORY.value == "resource_inventory"
    assert AssetStage.OPERATION.value == "operation"


def test_8_stages_defined():
    assert len(AssetStage) == 8


def test_stage_order():
    assert STAGE_ORDER[0] == AssetStage.RESOURCE_INVENTORY
    assert STAGE_ORDER[-1] == AssetStage.OPERATION


def test_data_asset_model():
    asset = DataAsset(name="测试数据资产", current_stage=AssetStage.RESOURCE_INVENTORY)
    assert asset.name == "测试数据资产"


def test_stage_record_model():
    record = StageRecord(stage=AssetStage.RESOURCE_INVENTORY, status=StageStatus.DRAFT)
    assert record.status == StageStatus.DRAFT


def test_stage_material_model():
    mat = StageMaterial(file_name="test.pdf", file_path="/uploads/test.pdf", hash_sha256="a" * 64)
    assert len(mat.hash_sha256) == 64
