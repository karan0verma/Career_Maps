from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from src.core.config import settings
from src.api.routes import auth, users, admin, companies, jobs, stats, resume
from src.db.session import engine
from src.admin_views import UserAdmin, CompanyAdmin, JobAdmin, SavedJobAdmin

app = FastAPI(title=settings.PROJECT_NAME)

admin_app = Admin(app, engine)
admin_app.add_view(UserAdmin)
admin_app.add_view(CompanyAdmin)
admin_app.add_view(JobAdmin)
admin_app.add_view(SavedJobAdmin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(resume.router, prefix="/users/me/resume", tags=["resume"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
