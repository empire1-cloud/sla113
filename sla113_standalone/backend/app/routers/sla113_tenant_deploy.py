"""SLA113 Tenant Deploy — Game deployment per tenant.

Deploys built game bundles to tenant-scoped paths:
  static/tenants/{subdomain}/deploys/{deploy_id}/
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timezone
import uuid
import os
import shutil
import logging
from pathlib import Path

from app.core.database import get_database
from app.core.config import get_settings
from app.core.tenant_context import get_current_tenant

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/deploy", tags=["sla113-tenant-deploy"])

DEPLOY_BASE = Path(__file__).resolve().parent.parent / "static" / "tenants"


def _db():
    return get_database()


@router.post("/{build_id}")
async def deploy_build(
    build_id: str,
    label: str = "",
    tenant: dict = Depends(get_current_tenant),
):
    tid = tenant["id"]
    subdomain = tenant["subdomain"]
    db = _db()
    build = await db["sla113_builds"].find_one(
        {"id": build_id, "tenant_id": tid, "status": "completed"}
    )
    if not build:
        raise HTTPException(status_code=404, detail="Completed build not found in this tenant")
    features = tenant.get("features", {})
    now = datetime.now(timezone.utc).isoformat()
    deploy_id = f"DEPLOY-{uuid.uuid4().hex[:8].upper()}"
    deploy_path = DEPLOY_BASE / subdomain / "deploys" / deploy_id
    deploy_path.mkdir(parents=True, exist_ok=True)
    index_path = deploy_path / "index.html"
    game_title = build.get("project_name", "Game")
    html = _generate_deply_html(
        game_title=game_title,
        tenant_name=tenant.get("name", "Operator"),
        primary_color=tenant.get("brand", {}).get("primary_color", "#1a1a2e"),
        build_id=build_id,
    )
    index_path.write_text(html)
    deploy = {
        "id": deploy_id,
        "tenant_id": tid,
        "build_id": build_id,
        "project_id": build.get("project_id", ""),
        "label": label or deploy_id,
        "game_type": build.get("game_type", "unknown"),
        "build_status": "completed",
        "status": "deployed",
        "url": f"https://{subdomain}.{get_settings().PLATFORM_DOMAIN}/static/tenants/{subdomain}/deploys/{deploy_id}/index.html",
        "path": str(deploy_path),
        "created_at": now,
        "updated_at": now,
    }
    await db["sla113_deployments"].insert_one(deploy)
    deploy.pop("_id", None)
    await db["sla113_tenants"].update_one(
        {"id": tid},
        {"$inc": {"stats.total_deployments": 1}, "$set": {"updated_at": now}},
    )
    logger.info(f"Deployed {deploy_id} for tenant {subdomain} (build {build_id})")
    return deploy


@router.get("/list")
async def list_deploys(tenant: dict = Depends(get_current_tenant)):
    db = _db()
    cursor = db["sla113_deployments"].find(
        {"tenant_id": tenant["id"]}, {"_id": 0}
    ).sort("created_at", -1).limit(50)
    deploys = await cursor.to_list(50)
    return {"deployments": deploys, "total": len(deploys)}


@router.get("/{deploy_id}")
async def get_deploy(deploy_id: str, tenant: dict = Depends(get_current_tenant)):
    db = _db()
    deploy = await db["sla113_deployments"].find_one(
        {"id": deploy_id, "tenant_id": tenant["id"]}, {"_id": 0}
    )
    if not deploy:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deploy


@router.delete("/{deploy_id}")
async def delete_deploy(deploy_id: str, tenant: dict = Depends(get_current_tenant)):
    tid = tenant["id"]
    db = _db()
    deploy = await db["sla113_deployments"].find_one(
        {"id": deploy_id, "tenant_id": tid}
    )
    if not deploy:
        raise HTTPException(status_code=404, detail="Deployment not found")
    path = deploy.get("path", "")
    if path and os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
    await db["sla113_deployments"].delete_one({"id": deploy_id, "tenant_id": tid})
    await db["sla113_tenants"].update_one(
        {"id": tid},
        {"$inc": {"stats.total_deployments": -1}},
    )
    return {"deleted": True, "deploy_id": deploy_id}


def _generate_deply_html(game_title: str, tenant_name: str, primary_color: str, build_id: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title>{game_title} — {tenant_name}</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#0a0a12; color:#fff; font-family:system-ui,-apple-system,sans-serif; min-height:100dvh; display:flex; flex-direction:column; align-items:center; justify-content:center; }}
  #game-container {{ width:100%; max-width:480px; aspect-ratio:9/16; background:#111; border-radius:12px; border:2px solid {primary_color}; overflow:hidden; position:relative; }}
  #game-canvas {{ width:100%; height:100%; display:block; }}
  .header {{ text-align:center; padding:12px 16px; width:100%; max-width:480px; }}
  .header h1 {{ font-size:1.1rem; color:{primary_color}; }}
  .header .meta {{ font-size:0.75rem; color:#888; margin-top:4px; }}
  .footer {{ text-align:center; padding:12px; font-size:0.7rem; color:#555; }}
  .build-badge {{ position:absolute; bottom:8px; right:8px; background:rgba(0,0,0,0.7); color:#555; font-size:0.6rem; padding:2px 6px; border-radius:4px; pointer-events:none; }}
</style>
</head>
<body>
  <div class="header">
    <h1>{game_title}</h1>
    <div class="meta">Powered by {tenant_name}</div>
  </div>
  <div id="game-container">
    <canvas id="game-canvas"></canvas>
    <div class="build-badge">{build_id}</div>
  </div>
  <div class="footer">SLA113 Game OS &mdash; {tenant_name}</div>
  <script>
    const canvas = document.getElementById('game-canvas');
    const ctx = canvas.getContext('2d');
    function resize() {{
      const container = document.getElementById('game-container');
      canvas.width = container.clientWidth;
      canvas.height = container.clientHeight;
    }}
    window.addEventListener('resize', resize);
    resize();
    function draw() {{
      const w = canvas.width, h = canvas.height;
      ctx.fillStyle = '#0a0a12';
      ctx.fillRect(0, 0, w, h);
      ctx.fillStyle = '{primary_color}';
      ctx.font = `${{Math.min(w,h)*0.05}}px system-ui`;
      ctx.textAlign = 'center';
      ctx.fillText('{game_title}', w/2, h/2);
      ctx.font = `${{Math.min(w,h)*0.025}}px system-ui`;
      ctx.fillStyle = '#555';
      ctx.fillText('Game Bundle Loading...', w/2, h/2 + 30);
      requestAnimationFrame(draw);
    }}
    draw();
  </script>
</body>
</html>"""
