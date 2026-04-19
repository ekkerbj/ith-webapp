import pytest
from sqlalchemy.orm import Session

from ith_webapp.models.market import Market

def test_classification_can_be_persisted_and_retrieved(session: Session):
    from ith_webapp.models.classification import Classification
    obj = Classification(name="Test Classification")
    session.add(obj)
    session.commit()
    result = session.get(Classification, obj.classification_id)
    assert result is not None
    assert result.name == "Test Classification"
