from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader


def save_pdf(comic_id, title, layout, settings):

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = output_dir / f"{comic_id}.pdf"

    panels_dir = Path("static/panels")

    panel_files = [
        panels_dir / "panel_1.png",
        panels_dir / "panel_2.png",
        panels_dir / "panel_3.png",
        panels_dir / "panel_4.png",
        panels_dir / "panel_5.png",
    ]

    pdf = canvas.Canvas(
        str(pdf_path),
        pagesize=A4
    )

    page_width, page_height = A4

    for index, panel_path in enumerate(panel_files, start=1):

        if not panel_path.exists():
            continue

        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(
            40,
            page_height - 40,
            f"{title} - Panel {index}"
        )

        image = ImageReader(str(panel_path))

        pdf.drawImage(
            image,
            40,
            100,
            width=515,
            height=515,
            preserveAspectRatio=True,
            anchor="c"
        )

        pdf.setFont("Helvetica", 11)
        pdf.drawString(
            40,
            60,
            f"Art Style: {settings.get('art_style', 'Comic Book')}"
        )

        pdf.drawRightString(
            page_width - 40,
            60,
            f"Tone: {settings.get('tone', 'Adventure')}"
        )

        pdf.showPage()

    pdf.save()

    print(f"PDF successfully created: {pdf_path}")

    return str(pdf_path)