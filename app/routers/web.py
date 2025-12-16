from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Trang chủ"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "app_name": "ShiftGenix"}
    )

@router.get("/schedule", response_class=HTMLResponse)
def schedule_page(request: Request):
    """Trang xếp lịch trực"""
    return templates.TemplateResponse(
        "schedule.html",
        {"request": request}
    )

@router.get("/staff", response_class=HTMLResponse)
def staff_management(request: Request):
    """Trang quản lý nhân viên"""
    return templates.TemplateResponse(
        "staff.html",
        {"request": request}
    )

@router.get("/departments", response_class=HTMLResponse)
def department_management(request: Request):
    """Trang quản lý khoa/phòng ban"""
    return templates.TemplateResponse(
        "departments.html",
        {"request": request}
    )

@router.get("/results", response_class=HTMLResponse)
def view_results(request: Request):
    """Trang xem kết quả lịch trực"""
    return templates.TemplateResponse(
        "results.html",
        {"request": request}
    )

@router.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    """Trang giới thiệu"""
    return templates.TemplateResponse(
        "about.html",
        {"request": request}
    )