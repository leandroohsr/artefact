import uvicorn


def main() -> None:
    uvicorn.run("artefact.api:app", reload=True)


if __name__ == "__main__":
    main()
