"""
Static schema file server for schemas.electricity.works

Serves YAML schemas from type_definitions/ with clean URLs:
- /types/g.node.gt/004 -> type_definitions/schemas/g.node.gt.004.yaml
- /enums/base.g.node.class/000 -> type_definitions/enums/base.g.node.class.000.yaml
- /formats/uuid4.str -> type_definitions/formats/uuid4.str.yaml
"""

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import yaml

app = FastAPI(title="Sema Server")

# Enable CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "HEAD", "OPTIONS"],
    allow_headers=["*"],
)

# Path to your type_definitions directory
TYPE_DEFS_ROOT = Path(__file__).resolve().parents[3] / "definitions"

def get_schema_file(category: str, name: str, version: Optional[str] = None) -> Path:
    """
    Resolve schema file path from URL components.
    
    Args:
        category: 'schemas', 'enums', or 'formats'
        name: e.g., 'g.node.gt', 'base.g.node.class', 'uuid4.str'
        version: e.g., '004', '000', or None for formats
    
    Returns:
        Path to the schema file
    """
    if version:
        filename = f"{name}.{version}.yaml"
    else:
        filename = f"{name}.yaml"
    
    file_path = TYPE_DEFS_ROOT / category / filename
    
    print(f"file_path is {file_path}")
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Schema not found: {category}/{name}" + (f"/{version}" if version else "")
        )
    
    return file_path


def load_schema(file_path: Path) -> dict:
    """Load and parse YAML schema file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading schema: {e}")


def get_latest_version(category: str, name: str) -> Optional[str]:
    """Find the latest version of a schema by scanning the directory."""
    schema_dir = TYPE_DEFS_ROOT / category
    pattern = f"{name}.*.yaml"
    
    versions = []
    for file_path in schema_dir.glob(pattern):
        # Extract version from filename like "g.node.gt.004.yaml"
        stem = file_path.stem  # "g.node.gt.004"
        parts = stem.split(".")
        if len(parts) > len(name.split(".")):
            version = parts[-1]
            if version.isdigit():
                versions.append(version)
    
    if not versions:
        return None
    
    # Return highest version (as string)
    return max(versions, key=lambda v: int(v))


@app.get("/types/{name}/{version}")
async def get_type_schema(name: str, version: str, response: Response):
    """Serve a versioned type schema."""
    file_path = get_schema_file("types", name, version)
    schema = load_schema(file_path)
    
    # Set appropriate headers
    response.headers["Content-Type"] = "application/schema+json"
    response.headers["Cache-Control"] = "public, max-age=31536000"  # 1 year
    
    return schema


@app.get("/types/{name}/latest")
async def get_type_latest(name: str):
    """Redirect to the latest version of a type."""
    latest_version = get_latest_version("schemas", name)
    
    if not latest_version:
        raise HTTPException(
            status_code=404,
            detail=f"No versions found for type: {name}"
        )
    
    return RedirectResponse(
        url=f"/types/{name}/{latest_version}",
        status_code=307  # Temporary redirect
    )


@app.get("/types/{name}")
async def list_type_versions(name: str):
    """List all available versions of a type."""
    schema_dir = TYPE_DEFS_ROOT / "schemas"
    pattern = f"{name}.*.yaml"
    
    versions = []
    for file_path in schema_dir.glob(pattern):
        stem = file_path.stem
        parts = stem.split(".")
        if len(parts) > len(name.split(".")):
            version = parts[-1]
            if version.isdigit():
                versions.append({
                    "version": version,
                    "url": f"/types/{name}/{version}"
                })
    
    if not versions:
        raise HTTPException(
            status_code=404,
            detail=f"Type not found: {name}"
        )
    
    # Sort by version number
    versions.sort(key=lambda v: int(v["version"]), reverse=True)
    
    return {
        "type_name": name,
        "versions": versions,
        "latest": versions[0] if versions else None
    }


@app.get("/enums/{name}/{version}")
async def get_enum_schema(name: str, version: str, response: Response):
    """Serve a versioned enum schema."""
    file_path = get_schema_file("enums", name, version)
    schema = load_schema(file_path)
    
    response.headers["Content-Type"] = "application/schema+json"
    response.headers["Cache-Control"] = "public, max-age=31536000"
    
    return schema


@app.get("/enums/{name}/latest")
async def get_enum_latest(name: str):
    """Redirect to the latest version of an enum."""
    latest_version = get_latest_version("enums", name)
    
    if not latest_version:
        raise HTTPException(
            status_code=404,
            detail=f"No versions found for enum: {name}"
        )
    
    return RedirectResponse(
        url=f"/enums/{name}/{latest_version}",
        status_code=307
    )


@app.get("/enums/{name}")
async def list_enum_versions(name: str):
    """List all available versions of an enum."""
    schema_dir = TYPE_DEFS_ROOT / "enums"
    pattern = f"{name}.*.yaml"
    
    versions = []
    for file_path in schema_dir.glob(pattern):
        stem = file_path.stem
        parts = stem.split(".")
        if len(parts) > len(name.split(".")):
            version = parts[-1]
            if version.isdigit():
                versions.append({
                    "version": version,
                    "url": f"/enums/{name}/{version}"
                })
    
    if not versions:
        raise HTTPException(
            status_code=404,
            detail=f"Enum not found: {name}"
        )
    
    versions.sort(key=lambda v: int(v["version"]), reverse=True)
    
    return {
        "enum_name": name,
        "versions": versions,
        "latest": versions[0] if versions else None
    }


@app.get("/formats/{name}")
async def get_format_schema(name: str, response: Response):
    """Serve a format schema (formats are not versioned)."""
    file_path = get_schema_file("formats", name, version=None)
    schema = load_schema(file_path)
    
    response.headers["Content-Type"] = "application/schema+json"
    response.headers["Cache-Control"] = "public, max-age=86400"  # 1 day
    
    return schema


@app.get("/formats")
async def list_formats():
    """List all available format schemas."""
    formats_dir = TYPE_DEFS_ROOT / "formats"
    
    formats = []
    for file_path in formats_dir.glob("*.yaml"):
        name = file_path.stem
        formats.append({
            "name": name,
            "url": f"/formats/{name}"
        })
    
    formats.sort(key=lambda f: f["name"])
    
    return {
        "formats": formats
    }


@app.get("/")
async def root():
    """API root with documentation."""
    return {
        "name": "SemaServer",
        "description": "JSON Schema definitions for GridWorks Application Shared Language",
        "documentation": "https://sema.readthedocs.io/",
        "endpoints": {
            "types": {
                "get_schema": "/types/{name}/{version}",
                "get_latest": "/types/{name}/latest",
                "list_versions": "/types/{name}",
                "example": "/types/g.node.gt/004"
            },
            "enums": {
                "get_schema": "/enums/{name}/{version}",
                "get_latest": "/enums/{name}/latest",
                "list_versions": "/enums/{name}",
                "example": "/enums/base.g.node.class/000"
            },
            "formats": {
                "get_schema": "/formats/{name}",
                "list_all": "/formats",
                "example": "/formats/uuid4.str"
            }
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)