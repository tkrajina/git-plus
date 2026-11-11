from gitplus import semver


def test_parse_tag_keeps_prerelease_suffix():
    version = semver.parse_tag_as_semver("v1.2.3-beta")

    assert version is not None
    assert version.suffix == "beta"


def test_parse_tag_suffix_survives_str_roundtrip():
    version = semver.parse_tag_as_semver("v2.0.0-rc1")

    assert version is not None
    assert str(version) == "2.0.0-rc1"
