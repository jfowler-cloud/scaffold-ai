"""CDK deployment service for deploying generated infrastructure."""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional


class CDKDeploymentService:
    """Service for deploying CDK stacks."""

    def __init__(self):
        self.cdk_version = self._get_cdk_version()

    def _get_cdk_version(self) -> Optional[str]:
        """Get installed CDK version."""
        try:
            result = subprocess.run(
                ["cdk", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None

    def deploy(
        self,
        stack_name: str,
        cdk_code: str,
        app_code: str,
        region: str = "us-east-1",
        profile: Optional[str] = None,
        require_approval: bool = True,
    ) -> Dict[str, any]:
        """
        Deploy a CDK stack.

        Args:
            stack_name: Name of the stack to deploy
            cdk_code: CDK stack code (lib/stack.ts)
            app_code: CDK app code (bin/app.ts)
            region: AWS region
            profile: AWS profile name
            require_approval: Whether to require manual approval (default: True)

        Returns:
            Dict with deployment status and outputs
        """
        if not self.cdk_version:
            return {
                "success": False,
                "error": "CDK CLI not installed. Install with: npm install -g aws-cdk",
            }

        temp_dir = None
        try:
            # Create temporary CDK project
            temp_dir = tempfile.mkdtemp(prefix="scaffold-ai-deploy-")
            project_path = Path(temp_dir)

            # Initialize CDK project structure
            self._create_cdk_project(project_path, stack_name, cdk_code, app_code)

            # Install dependencies
            install_result = self._run_command(
                ["npm", "install"], cwd=project_path, timeout=120
            )
            if install_result["returncode"] != 0:
                return {
                    "success": False,
                    "error": f"npm install failed: {install_result['stderr']}",
                }

            # Bootstrap CDK (if needed)
            bootstrap_result = self._bootstrap_cdk(project_path, region, profile)
            if not bootstrap_result["success"]:
                return bootstrap_result

            # Deploy stack
            deploy_result = self._deploy_stack(
                project_path, region, profile, require_approval
            )

            return deploy_result

        except (OSError, RuntimeError) as e:
            return {"success": False, "error": f"Deployment failed: {str(e)}"}
        finally:
            # Cleanup temp directory
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _create_cdk_project(
        self, project_path: Path, stack_name: str, cdk_code: str, app_code: str
    ):
        """Create CDK project structure."""
        # Create directories
        (project_path / "lib").mkdir(parents=True)
        (project_path / "bin").mkdir(parents=True)

        # Write package.json
        package_json = {
            "name": stack_name.lower().replace(" ", "-"),
            "version": "0.1.0",
            "bin": {"app": "bin/app.js"},
            "scripts": {"build": "tsc", "cdk": "cdk"},
            "devDependencies": {
                "@types/node": "^22.0.0",
                "aws-cdk": "^2.0.0",
                "typescript": "^5.0.0",
            },
            "dependencies": {"aws-cdk-lib": "^2.0.0", "constructs": "^10.0.0"},
        }

        with open(project_path / "package.json", "w") as f:
            import json

            json.dump(package_json, f, indent=2)

        # Write tsconfig.json
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "lib": ["es2020"],
                "declaration": True,
                "strict": True,
                "noImplicitAny": True,
                "strictNullChecks": True,
                "noImplicitThis": True,
                "alwaysStrict": True,
                "noUnusedLocals": False,
                "noUnusedParameters": False,
                "noImplicitReturns": True,
                "noFallthroughCasesInSwitch": False,
                "inlineSourceMap": True,
                "inlineSources": True,
                "experimentalDecorators": True,
                "strictPropertyInitialization": False,
                "typeRoots": ["./node_modules/@types"],
            },
            "exclude": ["node_modules", "cdk.out"],
        }

        with open(project_path / "tsconfig.json", "w") as f:
            import json

            json.dump(tsconfig, f, indent=2)

        # Write cdk.json
        approval_level = "never" if not require_approval else "broadening"
        cdk_json = {
            "app": "npx ts-node --prefer-ts-exts bin/app.ts",
            "requireApproval": approval_level,
            "context": {
                "@aws-cdk/core:enableStackNameDuplicates": True,
                "aws-cdk:enableDiffNoFail": True,
            },
        }

        with open(project_path / "cdk.json", "w") as f:
            import json

            json.dump(cdk_json, f, indent=2)

        # Write stack code
        with open(project_path / "lib" / f"{stack_name.lower()}-stack.ts", "w") as f:
            f.write(cdk_code)

        # Write app code
        with open(project_path / "bin" / "app.ts", "w") as f:
            f.write(app_code)

    def _bootstrap_cdk(
        self, project_path: Path, region: str, profile: Optional[str]
    ) -> Dict[str, any]:
        """Bootstrap CDK in the target account/region."""
        cmd = ["npx", "cdk", "bootstrap"]

        env = os.environ.copy()
        env["AWS_REGION"] = region
        if profile:
            env["AWS_PROFILE"] = profile

        result = self._run_command(cmd, cwd=project_path, env=env, timeout=300)

        # Bootstrap might already be done, which is fine
        if (
            result["returncode"] == 0
            or "already bootstrapped" in result["stdout"].lower()
        ):
            return {"success": True}

        return {"success": False, "error": f"Bootstrap failed: {result['stderr']}"}

    def _deploy_stack(
        self,
        project_path: Path,
        region: str,
        profile: Optional[str],
        require_approval: bool,
    ) -> Dict[str, any]:
        """Deploy the CDK stack."""
        approval_flag = "never" if not require_approval else "broadening"
        cmd = [
            "npx",
            "cdk",
            "deploy",
            "--require-approval",
            approval_flag,
            "--outputs-file",
            "outputs.json",
        ]

        env = os.environ.copy()
        env["AWS_REGION"] = region
        if profile:
            env["AWS_PROFILE"] = profile

        result = self._run_command(cmd, cwd=project_path, env=env, timeout=600)

        if result["returncode"] != 0:
            return {
                "success": False,
                "error": f"Deployment failed: {result['stderr']}",
                "stdout": result["stdout"],
            }

        # Read outputs
        outputs = {}
        outputs_file = project_path / "outputs.json"
        if outputs_file.exists():
            import json

            with open(outputs_file) as f:
                outputs = json.load(f)

        return {
            "success": True,
            "message": "Stack deployed successfully",
            "outputs": outputs,
            "stdout": result["stdout"],
        }

    def _run_command(
        self, cmd: List[str], cwd: Path, env: Optional[Dict] = None, timeout: int = 60
    ) -> Dict[str, any]:
        """Run a shell command and return result."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=env or os.environ.copy(),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
            }
        except (OSError, ValueError) as e:
            return {"returncode": -1, "stdout": "", "stderr": str(e)}

    def destroy(
        self, stack_name: str, region: str = "us-east-1", profile: Optional[str] = None
    ) -> Dict[str, any]:
        """Destroy a deployed stack."""
        # This would require storing the CDK project or using CloudFormation directly
        # For now, return a message
        return {
            "success": False,
            "error": "Stack destruction not yet implemented. Use AWS Console or CDK CLI directly.",
        }
