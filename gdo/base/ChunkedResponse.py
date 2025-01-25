class ChunkedResponse:
    """
    (c) Chappy / ChatGPT
    """
    TCP_FRAME_SIZE = 1024

    def __init__(self, response_bytes: bytes, chunk_size: int = TCP_FRAME_SIZE):
        self.response_bytes = response_bytes
        self.chunk_size = chunk_size

    def wsgi_generator(self):
        for i in range(0, len(self.response_bytes), self.chunk_size):
            yield self.response_bytes[i : i + self.chunk_size]

    async def asgi_generator(self):
        total_size = len(self.response_bytes)
        for i in range(0, total_size, self.chunk_size):
            chunk = self.response_bytes[i : i + self.chunk_size]
            more_body = (i + self.chunk_size) < total_size
            yield chunk, more_body

