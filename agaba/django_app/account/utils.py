import secrets
import string

from django.core.files import File as DjangoFile
from balance.models import AccountPDF
from pathlib import Path
from borb.pdf import Document
from borb.pdf import Page
from borb.pdf import SingleColumnLayout
from borb.pdf import Paragraph
from borb.pdf import PDF
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont


def generate_otp(length=6):
    """Генерирует OTP заданной длины."""
    characters = string.digits

    otp = ''.join(secrets.choice(characters) for _ in range(length))
    return otp


FONT_PATH = Path(__file__).parent / "fonts" / "DejaVuSans.ttf"


def generate_pdf(replenishment):
    """Генерация счета PDF."""
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Font file not found: {FONT_PATH}")

    pdf = Document()
    page = Page()
    pdf.add_page(page)

    cyrillic_font = TrueTypeFont.true_type_font_from_file(FONT_PATH)

    layout = SingleColumnLayout(page)

    layout.add(Paragraph(
        "Счет на пополнение баланса",
        font=cyrillic_font,
        font_size=14
    ))
    layout.add(Paragraph(
        'Поставщик: "ООО АГАБА"',
        font=cyrillic_font,
        font_size=14
    ))
    layout.add(Paragraph(
        "ИНН: 1234567890",
        font=cyrillic_font,
        font_size=14
    ))
    layout.add(Paragraph(
        "КПП: 1234567890",
        font=cyrillic_font,
        font_size=14
    ))
    layout.add(Paragraph(
        "Юридический адрес: 1234 АБВ ГХИ ЙКМ",
        font=cyrillic_font,
        font_size=14
    ))
    layout.add(Paragraph(
        "Ставка: 18%",
        font=cyrillic_font,
        font_size=14
    ))
    layout.add(Paragraph(
        "Номер телефона: +7 (123) 456-78-90",
        font=cyrillic_font,
        font_size=14
    ))
    layout.add(Paragraph(
        "Почта: test@test.ru",
        font=cyrillic_font,
        font_size=14
    ))

    layout.add(Paragraph(
        f"ИНН: {replenishment.company.inn}",
        font=cyrillic_font,
        font_size=12
    ))
    layout.add(Paragraph(
        f"КПП: {replenishment.company.kpp}",
        font=cyrillic_font,
        font_size=12
    ))
    layout.add(Paragraph(
        f"Компания: {replenishment.company.name}",
        font=cyrillic_font,
        font_size=12
    ))
    layout.add(Paragraph(
        f"Юридический адрес {replenishment.company.legal_address}",
        font=cyrillic_font,
        font_size=14
    ))
    layout.add(Paragraph(
        "",
        font=cyrillic_font,
        font_size=12
    ))
    layout.add(Paragraph(
        f"Сумма: {replenishment.amount_replenishment} ₽",
        font=cyrillic_font,
        font_size=12
    ))

    file_name = f"replenishment_{replenishment.operation_id}.pdf"
    file_path = Path("/tmp") / file_name

    try:
        with open(file_path, "wb") as pdf_file_handle:
            PDF.dumps(pdf_file_handle, pdf)
    except Exception as e:
        print(f"Error saving PDF: {e}")
        raise

    return file_path


def save_pdf_to_db(replenishment):
    """Сохраняем PDF счета в БД."""
    pdf_file_path = generate_pdf(replenishment)

    with open(pdf_file_path, 'rb') as pdf_file:
        account_pdf = AccountPDF(
            user=replenishment.user,
            company=replenishment.company
        )

        django_file = DjangoFile(pdf_file)
        account_pdf.path_invoice.save(
            f"invoice_{replenishment.operation_id}.pdf",
            django_file,
            save=True
        )
        account_pdf.download_link = account_pdf.path_invoice.url
        account_pdf.save()

    if Path(pdf_file_path).exists():
        Path(pdf_file_path).unlink()

    return account_pdf
