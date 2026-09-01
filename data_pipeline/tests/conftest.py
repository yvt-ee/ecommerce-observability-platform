import pytest

from data_pipeline.spark_utils import get_local_spark_session


@pytest.fixture(scope="session")
def spark():
    session = get_local_spark_session("pytest-data-pipeline")
    yield session
    session.stop()
