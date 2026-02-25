"""Tool for synthesizing and validating generated code."""

import subprocess
from pathlib import Path


class SynthesizerTool:
    """Tool for running CDK synth and validating generated infrastructure."""

    def __init__(self, output_dir: str = "packages/generated/infrastructure"):
        self.output_dir = Path(output_dir)

    async def synth(self) -> dict:
        """
        Run CDK synth to validate the generated infrastructure.

        Returns:
            dict with success status and any error messages
        """
        try:
            result = subprocess.run(
                ["npx", "cdk", "synth"],
                cwd=self.output_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout,
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "CDK synth timed out after 60 seconds",
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "CDK CLI not found. Please install with: npm install -g aws-cdk",
            }
        except OSError as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def validate_typescript(self, code: str) -> dict:
        """
        Validate TypeScript code syntax.

        Returns:
            dict with valid status and any errors
        """
        import tempfile

        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".ts", delete=False) as f:
                f.write(code)
                temp_path = f.name

            result = subprocess.run(
                ["npx", "tsc", "--noEmit", temp_path],
                capture_output=True,
                text=True,
                timeout=10,
            )

            Path(temp_path).unlink()

            if result.returncode == 0:
                return {"valid": True, "errors": []}
            else:
                return {"valid": False, "errors": result.stderr.split("\n")}

        except (subprocess.TimeoutExpired, OSError, FileNotFoundError) as e:
            return {"valid": False, "errors": [str(e)]}
