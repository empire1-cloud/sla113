"""SLA113 Pydantic Models"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class TenantPlan(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class TenantStatus(str, Enum):
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class BrandConfig(BaseModel):
    primary_color: str = "#1a1a2e"
    secondary_color: str = "#e94560"
    accent_color: str = "#0f3460"
    logo_url: str = ""
    favicon_url: str = ""
    custom_css: str = ""
    operator_name: str = ""
    tagline: str = ""


class TenantFeatureFlags(BaseModel):
    custom_domain: bool = False
    api_access: bool = False
    white_label: bool = True
    analytics: bool = False
    priority_support: bool = False
    max_projects: int = 5
    max_builds_per_month: int = 10
    max_storage_mb: int = 500


class TenantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    subdomain: str = Field(..., min_length=3, max_length=63, pattern=r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
    plan: TenantPlan = TenantPlan.FREE
    brand: BrandConfig = Field(default_factory=BrandConfig)
    admin_email: str = ""
    admin_password: str = ""


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    plan: Optional[TenantPlan] = None
    brand: Optional[BrandConfig] = None
    status: Optional[TenantStatus] = None
    features: Optional[TenantFeatureFlags] = None


class TenantBillingPeriod(BaseModel):
    stripe_customer_id: str = ""
    stripe_subscription_id: str = ""
    current_period_start: str = ""
    current_period_end: str = ""
    payment_method: str = ""
    billing_email: str = ""


# ─── Projects (tenant-scoped) ───
class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    game_type: str = Field(..., description="One of the supported game types")
    description: Optional[str] = None
    theme: Optional[str] = Field(None, description="Visual theme: cyberpunk, fantasy, ocean, space, etc.")
    target_platform: str = Field(default="web", description="web, mobile, or both")


# ─── Vision Engine ───
class VisionGenerateRequest(BaseModel):
    project_id: str
    asset_type: str = Field(default="sprites", description="sprites, backgrounds, ui, animations, effects")
    style: Optional[str] = Field(None, description="pixel_art, vector, 3d_render, hand_drawn, anime")
    count: int = Field(default=5, ge=1, le=20)
    custom_prompt: Optional[str] = None


class ImageGenRequest(BaseModel):
    prompt: str
    style: str = "pixel_art"
    asset_type: str = "concept_art"
    size: str = "1024x1024"
    quality: str = "high"


# ─── Logic Engine ───
class LogicGenerateRequest(BaseModel):
    project_id: str
    logic_type: str = Field(default="mechanics", description="mechanics, rtp, paytable, rng, scoring, levels, economy")
    difficulty: str = Field(default="medium", description="easy, medium, hard, progressive")
    custom_requirements: Optional[str] = None


# ─── Composer Engine ───
class ComposeRequest(BaseModel):
    project_id: str
    include_vision: bool = True
    include_logic: bool = True
    output_format: str = Field(default="json", description="json, html5, specification")


# ─── Terminal ───
class TerminalRequest(BaseModel):
    command: str
    session_id: Optional[str] = "default"


# ─── Jobs (Night Queue) ───
class CreateJobRequest(BaseModel):
    preset: str
    config: Optional[dict] = None
    priority: str = "normal"
    depends_on: Optional[List[str]] = None


# ─── Pipelines ───
class CreatePipelineRequest(BaseModel):
    name: str
    type: str = "Automation"
    lane: int = 1


# ─── Build Pipeline ───
class CreateBuildRequest(BaseModel):
    project_id: str
    target: str = "webgl"
    optimization: str = "balanced"
    include_assets: bool = True
    include_logic: bool = True


# ─── Compliance ───
class ComplianceCheckRequest(BaseModel):
    project_id: str
    jurisdiction: str = "GLI"
    check_type: str = "full"


# ─── Deploy ───
class DeployRequest(BaseModel):
    build_id: str
    target_cdn: str = "cloudflare"
    region: str = "us-west"
    auto_ssl: bool = True


# ─── Master Admin ───
class SystemAdminLogin(BaseModel):
    api_key: str
