import ast
import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORSミドルウェアを追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ログの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 環境変数から設定を読み込む
BACKEND_DIR = os.getenv("BACKEND_DIR", "/app/backend")


class FileContent(BaseModel):
    filename: str
    content: str


def get_python_files(directory):
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)
                python_files.append(relative_path)
    return python_files


def extract_imports(content):
    try:
        tree = ast.parse(content)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports
    except SyntaxError:
        logger.error(f"Syntax error in Python file")
        return []
    except Exception as e:
        logger.error(f"Unexpected error while parsing Python file: {str(e)}")
        return []


@app.get("/")
async def root():
    return {"message": "Welcome to the Python Files Graph API"}


@app.get("/files")
async def get_files():
    try:
        files = get_python_files(BACKEND_DIR)
        nodes = [{"id": f, "label": f} for f in files]
        edges = []

        for file in files:
            with open(os.path.join(BACKEND_DIR, file), 'r') as f:
                content = f.read()
                imports = extract_imports(content)
                for imp in imports:
                    for target in files:
                        if target.replace('/', '.').replace('.py', '') == imp:
                            edges.append({"source": file, "target": target})

        return {"nodes": nodes, "edges": edges}
    except Exception as e:
        logger.error(f"Error getting files: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/file/{file_path:path}")
async def get_file_content(file_path: str):
    try:
        full_path = os.path.join(BACKEND_DIR, file_path)
        if not full_path.startswith(BACKEND_DIR):
            raise HTTPException(status_code=403, detail="Access denied")

        with open(full_path, 'r') as f:
            content = f.read()
        return {"content": content}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)
