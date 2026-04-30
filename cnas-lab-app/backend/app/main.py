from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import os

from app.database import engine, Base, SessionLocal
from app.models import models  # noqa: F401
from app.services.auth import init_admin_user
from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.import_csv import router as import_router
from app.api.crud import create_crud_router
from app.api.schemas import (
    Personnel, PersonnelCreate, PersonnelUpdate, PersonnelResponse,
    Authorization, AuthorizationCreate, AuthorizationUpdate, AuthorizationResponse,
    Training, TrainingCreate, TrainingUpdate, TrainingResponse,
    Supervision, SupervisionCreate, SupervisionUpdate, SupervisionResponse,
    Equipment, EquipmentCreate, EquipmentUpdate, EquipmentResponse,
    Calibration, CalibrationCreate, CalibrationUpdate, CalibrationResponse,
    Check, CheckCreate, CheckUpdate, CheckResponse,
    Maintenance, MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse,
    QualityControl, QCCreate, QCUpdate, QCResponse,
    InternalAudit, AuditCreate, AuditUpdate, AuditResponse,
    ManagementReview, MRCreate, MRUpdate, MRResponse,
    DetectionProject, ProjectCreate, ProjectUpdate, ProjectResponse,
    Document, DocumentCreate, DocumentUpdate, DocumentResponse,
    NCR, NCRCreate, NCRUpdate, NCRResponse,
)
from app.models.models import (
    Personnel as PersonnelModel,
    Authorization as AuthorizationModel,
    Training as TrainingModel,
    Supervision as SupervisionModel,
    Equipment as EquipmentModel,
    Calibration as CalibrationModel,
    Check as CheckModel,
    Maintenance as MaintenanceModel,
    QualityControl as QCModel,
    InternalAudit as AuditModel,
    ManagementReview as MRModel,
    DetectionProject as ProjectModel,
    Document as DocumentModel,
    NCR as NCRModel,
)

Base.metadata.create_all(bind=engine)

db = SessionLocal()
init_admin_user(db)
db.close()

app = FastAPI(title="CNAS实验室管理体系", version="1.0.0")


class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.url.path == "/" or request.url.path.endswith(".html"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response


app.add_middleware(NoCacheMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(import_router, prefix="/api")

app.include_router(create_crud_router(
    PersonnelModel, PersonnelCreate, PersonnelUpdate, PersonnelResponse,
    "/personnel", ["人员管理"], ["name", "employee_id", "department"],
), prefix="/api")
app.include_router(create_crud_router(
    AuthorizationModel, AuthorizationCreate, AuthorizationUpdate, AuthorizationResponse,
    "/authorizations", ["资质授权"], ["auth_name"],
), prefix="/api")
app.include_router(create_crud_router(
    TrainingModel, TrainingCreate, TrainingUpdate, TrainingResponse,
    "/trainings", ["培训记录"], ["topic"],
), prefix="/api")
app.include_router(create_crud_router(
    SupervisionModel, SupervisionCreate, SupervisionUpdate, SupervisionResponse,
    "/supervisions", ["监督记录"], [],
), prefix="/api")
app.include_router(create_crud_router(
    EquipmentModel, EquipmentCreate, EquipmentUpdate, EquipmentResponse,
    "/equipment", ["设备管理"], ["name", "equipment_id"],
), prefix="/api")
app.include_router(create_crud_router(
    CalibrationModel, CalibrationCreate, CalibrationUpdate, CalibrationResponse,
    "/calibrations", ["校准记录"], [],
), prefix="/api")
app.include_router(create_crud_router(
    CheckModel, CheckCreate, CheckUpdate, CheckResponse,
    "/checks", ["期间核查"], [],
), prefix="/api")
app.include_router(create_crud_router(
    MaintenanceModel, MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse,
    "/maintenance", ["维护记录"], [],
), prefix="/api")
app.include_router(create_crud_router(
    QCModel, QCCreate, QCUpdate, QCResponse,
    "/quality-controls", ["质量控制"], ["qc_number"],
), prefix="/api")
app.include_router(create_crud_router(
    AuditModel, AuditCreate, AuditUpdate, AuditResponse,
    "/internal-audits", ["内部审核"], ["audit_number"],
), prefix="/api")
app.include_router(create_crud_router(
    MRModel, MRCreate, MRUpdate, MRResponse,
    "/management-reviews", ["管理评审"], ["mr_number"],
), prefix="/api")
app.include_router(create_crud_router(
    ProjectModel, ProjectCreate, ProjectUpdate, ProjectResponse,
    "/detection-projects", ["检测业务"], ["project_number", "project_name", "customer_name"],
), prefix="/api")
app.include_router(create_crud_router(
    DocumentModel, DocumentCreate, DocumentUpdate, DocumentResponse,
    "/documents", ["文件管理"], ["doc_number", "doc_name"],
), prefix="/api")
app.include_router(create_crud_router(
    NCRModel, NCRCreate, NCRUpdate, NCRResponse,
    "/ncrs", ["不符合/纠正措施"], ["ncr_number", "description"],
), prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
