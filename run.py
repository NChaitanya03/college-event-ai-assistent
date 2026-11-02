import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("Starting CAIAS AI Event Assistant...")
    print("Open your browser and visit: http://127.0.0.1:8000")
    print("=" * 70)
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

