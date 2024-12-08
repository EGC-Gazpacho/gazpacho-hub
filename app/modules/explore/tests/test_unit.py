import pytest
from app.modules.explore.services import ModelService

def test_filter_models():
    service = ModelService()
    models = service.filter(name="test")
    assert len(models) > 0, "No models found"
    for model in models:
        assert "test" in model.fm_meta_data.title.lower(), "Model title does not match the query"