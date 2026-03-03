import tempfile
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from main import generate_report

app = FastAPI(
    title="HR Report API",
    description="API для генерации HR-отчетов в формате PDF",
    version="1.0.0"
)

# Настройка CORS для работы с n8n и другими сервисами
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint для Docker и мониторинга"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/")
async def root():
    """Информация об API"""
    return {
        "service": "HR Report API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "generate_from_server": "/generate-report-from-server",
            "generate_from_file": "/generate-report",
            "generate_with_url": "/generate-report-from-url",
            "docs": "/docs"
        }
    }


@app.get("/generate-report-from-server", response_class=FileResponse)
async def generate_report_from_server():
    """
    Генерация PDF-отчёта из данных на сервере (по умолчанию из URL в переменной окружения).

    Возвращает готовый PDF-файл.
    """
    try:
        # Вызываем функцию генерации отчёта без параметров - она загрузит данные из URL
        pdf_path = generate_report()
        
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise HTTPException(
                status_code=500,
                detail="PDF-отчёт не был создан",
            )

        return FileResponse(
            path=str(pdf_file),
            filename="HR-отчет.pdf",
            media_type="application/pdf",
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {exc}")


@app.get("/generate-report-from-url")
async def generate_report_from_url(url: str = None):
    """
    Генерация PDF-отчёта из данных по указанному URL.
    
    Параметры:
    - url: URL Excel-файла с данными (опционально, если не указан, используется значение по умолчанию)
    
    Возвращает JSON с информацией об отчете или файл PDF (в зависимости от параметра format).
    """
    try:
        pdf_path = generate_report(data_file_url=url)
        
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise HTTPException(
                status_code=500,
                detail="PDF-отчёт не был создан",
            )
        
        file_size = pdf_file.stat().st_size
        
        # Возвращаем информацию об отчете в JSON формате (удобно для n8n)
        return JSONResponse({
            "status": "success",
            "message": "PDF-отчёт успешно создан",
            "file_path": str(pdf_path),
            "file_size_bytes": file_size,
            "file_size_kb": round(file_size / 1024, 2),
            "filename": "HR-отчет.pdf",
            "download_url": f"/generate-report-from-server",
            "timestamp": datetime.now().isoformat()
        })

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {exc}")


@app.post("/generate-report", response_class=FileResponse)
async def generate_report_endpoint(file: UploadFile = File(...)):
    """
    Загрузка Excel-файла и генерация PDF-отчёта.

    Возвращает готовый PDF-файл.
    """
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Ожидается Excel-файл (.xlsx или .xls)")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_path = tmpdir_path / "data.xlsx"
            output_path = tmpdir_path / "HR-отчет.pdf"

            # Сохраняем загруженный файл
            content = await file.read()
            input_path.write_bytes(content)

            # Вызываем функцию генерации отчёта напрямую
            pdf_path = generate_report(str(input_path))
            
            # Копируем PDF в временную директорию для возврата
            pdf_file = Path(pdf_path)
            if pdf_file.exists():
                output_path.write_bytes(pdf_file.read_bytes())
            else:
                raise HTTPException(
                    status_code=500,
                    detail="PDF-отчёт не был создан",
                )

            return FileResponse(
                path=str(output_path),
                filename="HR-отчет.pdf",
                media_type="application/pdf",
            )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {exc}")


