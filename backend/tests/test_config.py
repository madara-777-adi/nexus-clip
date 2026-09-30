from app.core.config import Settings


def test_cors_origins_parse_comma_separated_values():
    config = Settings.model_construct(
        cors_origins_raw="https://example.com, https://www.example.com,,"
    )

    assert config.cors_origins == [
        "https://example.com",
        "https://www.example.com",
    ]
