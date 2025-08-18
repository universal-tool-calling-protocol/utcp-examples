from fastapi import FastAPI
from pydantic import BaseModel
from utcp_http.http_call_template import HttpCallTemplate
from utcp.data.utcp_manual import UtcpManual
from utcp.python_specific_tooling.tool_decorator import utcp_tool
import uvicorn

class TestRequest(BaseModel):
    value: str

__version__ = "1.0.0"
BASE_PATH = "http://localhost:8080"

app = FastAPI()

@app.get("/utcp", response_model=UtcpManual)
def get_utcp():
    return UtcpManual.create_from_decorators(manual_version=__version__) 

@utcp_tool(tool_call_template=HttpCallTemplate(
    name="test_provider",
    url=f"{BASE_PATH}/test",
    http_method="POST"
))
@app.post("/test")
def test_endpoint(data: TestRequest):
    return {"received": data.value}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
