from sqladmin import ModelView
from src.models.user import User, SavedJob
from src.models.company import Company
from src.models.job import Job

class UserAdmin(ModelView, model=User):
    column_list = [User.user_id, User.email, User.role, User.is_active, User.created_at]
    column_searchable_list = [User.email, User.role]
    column_sortable_list = [User.created_at, User.email]
    icon = "fa-solid fa-user"
    name_plural = "Users"

class CompanyAdmin(ModelView, model=Company):
    column_list = [Company.company_id, Company.display_name, Company.website, Company.industry, Company.is_active]
    column_searchable_list = [Company.display_name, Company.official_name, Company.website, Company.industry]
    column_sortable_list = [Company.display_name, Company.created_at]
    icon = "fa-solid fa-building"
    name_plural = "Companies"

class JobAdmin(ModelView, model=Job):
    column_list = [Job.job_id, Job.title, Job.company_id, Job.work_mode, Job.employment_type, Job.is_active]
    column_searchable_list = [Job.title, Job.location, Job.work_mode]
    column_sortable_list = [Job.posted_at, Job.title]
    icon = "fa-solid fa-briefcase"
    name_plural = "Jobs"

class SavedJobAdmin(ModelView, model=SavedJob):
    column_list = [SavedJob.user_id, SavedJob.job_id, SavedJob.saved_at]
    icon = "fa-solid fa-bookmark"
    name_plural = "Saved Jobs"
