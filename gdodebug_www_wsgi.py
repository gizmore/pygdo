import uvicorn

if __name__ == '__main__':
    """
    Debug this file with a debugger :)
    """
    uvicorn.run("index_wsgi:pygdo_application", port=5000, log_level="info", loop="asyncio", interface='wsgi')

