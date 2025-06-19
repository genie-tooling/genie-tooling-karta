# karta-engine/tests/test_types.py
import pytest
from pydantic import ValidationError

from karta.types import Entity, Fact


class TestEntityType:
    """Tests the Entity Pydantic model."""

    def test_entity_creation_success(self):
        """Test successful instantiation with valid data."""
        entity = Entity(
            text="Genie",
            label="ORG",
            start_char=0,
            end_char=5,
        )
        assert entity.text == "Genie"
        assert entity.label == "ORG"
        assert entity.start_char == 0
        assert entity.end_char == 5

    def test_entity_missing_required_fields(self):
        """Test that ValidationError is raised for missing required fields."""
        with pytest.raises(ValidationError) as excinfo:
            Entity(text="Missing label and indices")
        errors = excinfo.value.errors()
        assert len(errors) == 3  # label, start_char, end_char
        error_fields = {e["loc"][0] for e in errors}
        assert "label" in error_fields
        assert "start_char" in error_fields
        assert "end_char" in error_fields

    def test_entity_invalid_types(self):
        """Test that ValidationError is raised for incorrect data types."""
        with pytest.raises(ValidationError):
            Entity(text="Test", label="TYPE", start_char="zero", end_char=5)

    def test_entity_model_dump(self):
        """Test the model_dump method."""
        data = {
            "text": "Athens",
            "label": "GPE",
            "start_char": 20,
            "end_char": 26,
        }
        entity = Entity(**data)
        assert entity.model_dump() == data


class TestFactType:
    """Tests the Fact Pydantic model."""

    def test_fact_creation_minimal(self):
        """Test successful instantiation with only required fields."""
        fact = Fact(
            entity="Earth",
            attribute="mass",
            value="5.972 × 10^24 kg",
        )
        assert fact.entity == "Earth"
        assert fact.attribute == "mass"
        assert fact.value == "5.972 × 10^24 kg"
        assert fact.source is None

    def test_fact_creation_with_source(self):
        """Test successful instantiation with all fields."""
        fact = Fact(
            entity="Jupiter",
            attribute="moons",
            value="95",
            source="https://solarsystem.nasa.gov/planets/jupiter/moons/",
        )
        assert fact.value == "95"
        assert fact.source == "https://solarsystem.nasa.gov/planets/jupiter/moons/"

    def test_fact_missing_required_fields(self):
        """Test that ValidationError is raised for missing required fields."""
        with pytest.raises(ValidationError) as excinfo:
            Fact(entity="Mars", value="Red Planet")
        errors = excinfo.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"][0] == "attribute"

    def test_fact_model_dump(self):
        """Test the model_dump method."""
        data = {
            "entity": "Saturn",
            "attribute": "rings",
            "value": "Yes",
            "source": "Wikipedia",
        }
        fact = Fact(**data)
        assert fact.model_dump() == data