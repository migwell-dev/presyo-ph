import pytest

from presyo_ph.spark import get_spark_session


@pytest.fixture(scope="session")
def spark():
    session = get_spark_session()

    yield session

    session.stop()
