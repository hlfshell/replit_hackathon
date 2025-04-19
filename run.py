import uvicorn


def main():
    """Run the application using uvicorn server"""
    uvicorn.run(
        "app.backend.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()

