from share import Factory, UnknownKeyError


def test_factory_register_and_create():
    f: Factory[str] = Factory()

    @f.register("hello")
    def builder() -> str:  # type: ignore[return-type]
        return "world"

    obj = f.create("hello")
    assert callable(obj)
    assert obj() == "world"


def test_factory_unknown_without_default_raises():
    f: Factory[object] = Factory()
    try:
        _ = f.create("missing")
        raise AssertionError("Expected UnknownKeyError but none was raised")
    except UnknownKeyError:
        pass


def test_factory_default_used_when_unknown():
    f: Factory[str] = Factory()

    @f.register("default")
    def default_builder() -> str:  # type: ignore[return-type]
        return "ok"

    f.set_default("default")

    obj = f.create("unknown")
    assert obj() == "ok"
