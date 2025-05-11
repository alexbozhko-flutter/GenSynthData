#!/usr/bin/env python3
"""
Main script to run the entire invoice generation pipeline.
"""

import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_script(script_path: str) -> None:
    """Run a Python script and check its exit code."""
    logger.info(f"Running {script_path}")
    exit_code = os.system(f"python {script_path}")
    if exit_code != 0:
        raise RuntimeError(f"Script {script_path} failed with exit code {exit_code}")

def main():
    """Main function to run the entire pipeline."""
    # Get the project root directory
    project_root = Path(__file__).parent
    scripts_dir = project_root / "scripts"
    
    # List of scripts to run in order
    scripts = [
        "01_data_preparation.py",
        "02_synthetic_generation.py",
        "03_pdf_generation.py",
        "04_corpus_validation.py"
    ]
    
    # Run each script in sequence
    for script in scripts:
        script_path = scripts_dir / script
        if not script_path.exists():
            logger.error(f"Script {script} not found at {script_path}")
            continue
        
        try:
            run_script(str(script_path))
            logger.info(f"Successfully completed {script}")
        except Exception as e:
            logger.error(f"Error running {script}: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        main()
        logger.info("Pipeline completed successfully")
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        exit(1) 