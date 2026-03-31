"""Cloud Run entrypoint — starts the ADK API server programmatically.

This avoids CLI issues and gives us control over host/port binding,
which is critical for Cloud Run (must bind 0.0.0.0:$PORT).
"""

import os
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app

PORT = int(os.environ.get("PORT", "8080"))

app = get_fast_api_app(
    agents_dir=os.path.dirname(os.path.abspath(__file__)),
    web=True,
    host="0.0.0.0",
    port=PORT,
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
