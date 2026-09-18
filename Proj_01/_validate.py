import app


def main() -> None:
    demo = app.build_demo()
    assert demo is not None
    print("Blocks constructed successfully")


if __name__ == "__main__":
    main()
