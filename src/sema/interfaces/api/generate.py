from fastapi import FastAPI
from fastapi.responses import FileResponse
from sema.generator.seed_builder import SeedBuilder
import tempfile
import shutil

app = FastAPI()

@app.post("/api/generate")
async def generate_sema(request: GenerateRequest):
    """
    request contains:
    - selected_types: ["power.watts", "channel.readings"]
    - selected_enums: ["actor.class"]
    - package_name: "gbo"
    - repo_name: "gridworks-backoffice"
    """
    
    builder = SeedBuilder()
    
    # Generate to temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir)
        
        builder.generate_seed(
            selected_types=request.selected_types,
            selected_enums=request.selected_enums,
            package_name=request.package_name,
            repo_name=request.repo_name,
            output_path=output_path
        )
        
        # Zip the sema/ directory
        zip_path = shutil.make_archive(f"{tmpdir}/sema", 'zip', output_path / "sema")
        
        return FileResponse(
            zip_path,
            media_type='application/zip',
            filename=f"{request.repo_name}_sema.zip"
        )