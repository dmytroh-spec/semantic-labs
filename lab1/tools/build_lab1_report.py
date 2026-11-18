from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "Лабораторна_робота_1_Kyiv_Tourism_RDF.docx"


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=100, bottom=80, end=100) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for edge, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    tr_pr.append(repeat)


def set_keep_with_next(paragraph, enabled=True) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    keep = p_pr.find(qn("w:keepNext"))
    if enabled and keep is None:
        keep = OxmlElement("w:keepNext")
        p_pr.append(keep)


def set_repeat_table_rows_no_split(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    tr_pr.append(cant_split)


def add_heading(doc, text: str, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.add_run(text)
    set_keep_with_next(p)
    return p


def add_body(doc, text: str, indent=True):
    p = doc.add_paragraph(style="Body Text")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent:
        p.paragraph_format.first_line_indent = Cm(1.25)
    p.add_run(text)
    return p


def add_bullet(doc, text: str):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Cm(0.8)
    p.paragraph_format.first_line_indent = Cm(-0.45)
    p.add_run(text)
    return p


def add_numbered(doc, text: str):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.left_indent = Cm(0.8)
    p.paragraph_format.first_line_indent = Cm(-0.45)
    p.add_run(text)
    return p


def add_code(doc, code: str, caption: str | None = None):
    if caption:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(caption)
        run.italic = True
        run.font.size = Pt(10)
        set_keep_with_next(p)
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    set_repeat_table_rows_no_split(table.rows[0])
    cell = table.cell(0, 0)
    set_cell_shading(cell, "F4F6F8")
    set_cell_margins(cell, 100, 120, 100, 120)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1
    for index, line in enumerate(code.strip().splitlines()):
        if index:
            p.add_run().add_break()
        run = p.add_run(line)
        run.font.name = "Consolas"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        run.font.size = Pt(8)
    return table


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False if widths else True
    header = table.rows[0]
    set_repeat_table_header(header)
    for idx, value in enumerate(headers):
        cell = header.cells[idx]
        set_cell_shading(cell, "D9E2F3")
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(str(value))
        r.bold = True
        r.font.size = Pt(10)
        if widths:
            cell.width = Cm(widths[idx])
    for row_data in rows:
        row = table.add_row()
        set_repeat_table_rows_no_split(row)
        for idx, value in enumerate(row_data):
            cell = row.cells[idx]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(str(value))
            r.font.size = Pt(9.5)
            if widths:
                cell.width = Cm(widths[idx])
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_placeholder(doc, title: str, instruction: str):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.cell(0, 0)
    cell.width = Cm(16.2)
    set_cell_shading(cell, "F2F2F2")
    set_cell_margins(cell, 220, 160, 220, 160)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(title)
    r.bold = True
    r.font.size = Pt(12)
    p2 = cell.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run(instruction)
    r2.italic = True
    r2.font.size = Pt(10)
    return table


def add_caption(doc, text: str):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(text)
    r.font.size = Pt(10)
    r.italic = True
    return p


def setup_document():
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(1.5)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(14)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(0)

    body = doc.styles["Body Text"]
    body.font.name = "Times New Roman"
    body._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    body.font.size = Pt(14)
    body.paragraph_format.line_spacing = 1.5
    body.paragraph_format.space_after = Pt(0)

    for level in (1, 2):
        style = doc.styles[f"Heading {level}"]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.font.bold = True
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.space_before = Pt(10 if level == 1 else 7)
        style.paragraph_format.space_after = Pt(6)
        style.font.size = Pt(14)
        style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER if level == 1 else WD_ALIGN_PARAGRAPH.LEFT

    return doc


def build_report():
    doc = setup_document()

    add_heading(doc, "Мета роботи")
    add_body(doc, "Ознайомитися з принципами подання знань у вигляді RDF-графів, навчитися створювати RDF-модель засобами Python та бібліотеки RDFLib, серіалізувати її у форматах Turtle і JSON-LD, виконувати SPARQL-запити та пов’язувати локальні ресурси із зовнішньою базою знань Wikidata.")

    add_heading(doc, "Завдання роботи")
    tasks = [
        "обрати предметну область і підготувати джерело даних;",
        "визначити класи, властивості та зв’язки майбутнього RDF-графа;",
        "побудувати граф програмно за допомогою RDFLib;",
        "виконати серіалізацію графа у форматах Turtle та JSON-LD;",
        "додати до графа фрагмент, описаний вручну мовою Turtle;",
        "побудувати візуалізацію графа;",
        "підготувати й виконати п’ять SPARQL-запитів, включно з фільтрацією, сортуванням, агрегаціями та проходженням кількох зв’язків;",
        "пов’язати окремі локальні ресурси з Wikidata за допомогою owl:sameAs;",
        "показати приклад помилки моделювання та спосіб її виправлення;",
        "перевірити цілісність створених артефактів і проаналізувати результати.",
    ]
    for item in tasks:
        add_bullet(doc, item)

    add_heading(doc, "Предметна область і джерело даних")
    add_body(doc, "Предметною областю є міський туризм у Києві. RDF-граф описує Україну, місто Київ, туристичні пам’ятки, типи пам’яток і туристичні маршрути. Для кожної пам’ятки зберігаються назва, тип, рейтинг, орієнтовна вартість входу та зв’язок із містом. Маршрути об’єднують пам’ятки й задають послідовність відвідування.")
    add_body(doc, "Джерелом є підготовлений для лабораторної роботи локальний JSON-файл data/kyiv_tourism_data.json. Такий підхід забезпечує відтворюваність: граф можна перебудувати без доступу до зовнішнього API. Wikidata використовується окремо для семантичного зв’язування відомих сутностей, а не як основне джерело туристичних характеристик.")
    add_table(doc, ["Показник", "Значення"], [
        ("Кількість RDF-трійок після ручного доповнення", "171"),
        ("Кількість класів предметної області", "5"),
        ("Кількість екземплярів ресурсів", "28"),
        ("Кількість туристичних пам’яток", "20"),
        ("Кількість власних типів зв’язків", "5"),
        ("Кількість SPARQL-запитів", "5"),
        ("Формати серіалізації", "Turtle, JSON-LD"),
    ], widths=[11.5, 4.5])

    add_heading(doc, "Питання до RDF-графу")
    questions = [
        "Які пам’ятки мають рейтинг не нижче 4,7 і вартість входу не більше 15 євро?",
        "Які музеї розташовані у Києві?",
        "Скільки туристичних пам’яток описано для кожного міста?",
        "Які пам’ятки входять до маршрутів і в якому місті та країні вони розташовані?",
        "Яка середня вартість входу для кожного типу туристичних пам’яток?",
    ]
    for q in questions:
        add_numbered(doc, q)

    add_heading(doc, "Структура RDF-графу")
    add_body(doc, "Базовий простір імен проєкту — https://example.org/tourism/. Для повторного використання загальноприйнятої семантики застосовано RDF, RDFS, Schema.org, Dublin Core Terms, OWL та XML Schema Datatypes.")
    add_table(doc, ["Клас", "Призначення", "Приклад URI"], [
        ("tour:Country", "Країна", "tour:country/ukraine"),
        ("tour:City", "Місто", "tour:city/kyiv"),
        ("tour:Attraction", "Туристична пам’ятка", "tour:attraction/saint-sophia"),
        ("tour:AttractionType", "Категорія пам’ятки", "tour:type/museum"),
        ("tour:TouristRoute", "Туристичний маршрут", "tour:route/kyiv-weekend"),
    ], widths=[4.0, 5.3, 6.7])
    add_table(doc, ["Властивість", "Зміст зв’язку"], [
        ("tour:locatedInCountry", "місто → країна"),
        ("tour:locatedInCity", "пам’ятка → місто"),
        ("tour:hasAttractionType", "пам’ятка → тип пам’ятки"),
        ("tour:includesAttraction", "маршрут → пам’ятка"),
        ("tour:nextStop", "пам’ятка → наступна пам’ятка маршруту"),
    ], widths=[7.0, 9.0])

    add_heading(doc, "Побудова графу засобами RDFLib")
    add_body(doc, "Модуль src/rdf_model.py читає JSON-дані, створює URI ресурсів, додає класи та екземпляри, а потім формує зв’язки. Текстові назви зберігаються як україномовні літерали, рейтинг і ціна — як типізовані xsd:decimal, а населення — як xsd:integer.")
    add_code(doc, '''EX = Namespace("https://example.org/tourism/")
SCHEMA = Namespace("https://schema.org/")

def add_resource(graph, uri, rdf_class, label):
    graph.add((uri, RDF.type, rdf_class))
    graph.add((uri, RDFS.label, Literal(label, lang="uk")))

graph.add((attraction_uri, TOUR.locatedInCity, city_uri))
graph.add((attraction_uri, TOUR.hasAttractionType, type_uri))
graph.add((attraction_uri, SCHEMA.ratingValue,
           Literal(str(item["rating"]), datatype=XSD.decimal)))
graph.add((attraction_uri, TOUR.entryPriceEUR,
           Literal(str(item["price"]), datatype=XSD.decimal)))''', "Лістинг 1 — фрагмент програмної побудови RDF-графу")
    add_body(doc, "Після програмного формування граф серіалізується у data/kyiv_graph_generated.ttl і data/kyiv_graph.jsonld. Далі до нього додається ручний Turtle-фрагмент, а завершена версія зберігається у data/kyiv_graph.ttl.")

    add_heading(doc, "Ручне доповнення мовою Turtle")
    add_body(doc, "Ручний фрагмент додає опис туристичного маршруту та Софійського собору. Він демонструє, що RDFLib може поєднувати програмно створені трійки з даними, записаними безпосередньо в Turtle.")
    add_code(doc, '''@prefix tour: <https://example.org/tourism/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix schema: <https://schema.org/> .

<https://example.org/tourism/route/kyiv-weekend>
    dcterms:description
      "Дводенний пішохідний маршрут історичним центром Києва"@uk .

<https://example.org/tourism/attraction/saint-sophia>
    schema:description
      "Пам'ятка архітектури та монументального живопису XI століття"@uk .''', "Лістинг 2 — ручне доповнення RDF-графу")

    add_heading(doc, "Візуалізація RDF-графу")
    add_body(doc, "Скрипт src/draw_graph.py перетворює RDF-трійки на орієнтований граф. Вузли відповідають ресурсам і літералам, а підписані ребра — предикатам. Для читабельності візуалізація обмежується сутностями предметної області та основними зв’язками. Отримане зображення містить 28 вузлів і 65 ребер.")
    add_placeholder(doc, "МІСЦЕ ДЛЯ РИСУНКА 1", "Вставити файл output/kyiv_tourism_graph.png або знімок вікна з відкритою візуалізацією.")
    add_caption(doc, "Рисунок 1 — Візуалізація RDF-графу міського туризму Києва")

    add_heading(doc, "SPARQL-запити та результати")
    add_heading(doc, "Запит 1. Доступні пам’ятки з високим рейтингом", level=2)
    add_code(doc, '''SELECT ?name ?rating ?price WHERE {
  ?item a tour:Attraction ; rdfs:label ?name ;
        schema:ratingValue ?rating ; tour:entryPriceEUR ?price .
  FILTER(?rating >= 4.7 && ?price <= 15)
}
ORDER BY DESC(?rating) ?price ?name''')
    add_body(doc, "Запит повернув 13 результатів. Нижче наведено частину вибірки.", indent=False)
    add_table(doc, ["Пам’ятка", "Рейтинг", "Ціна, EUR"], [
        ("Михайлівський Золотоверхий монастир", "4.8", "0"),
        ("Андріївська церква", "4.8", "5"),
        ("Києво-Печерська лавра", "4.8", "8"),
        ("Софійський собор", "4.8", "12"),
        ("Майдан Незалежності", "4.7", "0"),
        ("Золоті ворота", "4.7", "5"),
    ], widths=[10.5, 2.7, 2.8])

    add_heading(doc, "Запит 2. Музеї за містом", level=2)
    add_code(doc, '''SELECT ?museum ?city WHERE {
  ?item a tour:Attraction ; rdfs:label ?museum ;
        tour:hasAttractionType <https://example.org/tourism/type/museum> ;
        tour:locatedInCity ?cityResource .
  ?cityResource rdfs:label ?city .
}
ORDER BY ?city ?museum''')
    add_table(doc, ["Музей", "Місто"], [
        ("Музей історії України у Другій світовій війні", "Київ"),
        ("Музей однієї вулиці", "Київ"),
        ("Національний музей історії України", "Київ"),
    ], widths=[12.0, 4.0])

    add_heading(doc, "Запит 3. Кількість пам’яток у місті", level=2)
    add_code(doc, '''SELECT ?city (COUNT(?item) AS ?attractionCount) WHERE {
  ?item a tour:Attraction ; tour:locatedInCity ?cityResource .
  ?cityResource rdfs:label ?city .
}
GROUP BY ?city''')
    add_table(doc, ["Місто", "Кількість пам’яток"], [("Київ", "20")], widths=[8.0, 8.0])

    add_heading(doc, "Запит 4. Шлях маршрут → пам’ятка → місто → країна", level=2)
    add_code(doc, '''SELECT ?route ?attraction ?city ?country WHERE {
  ?routeResource a tour:TouristRoute ; rdfs:label ?route ;
                 tour:includesAttraction ?item .
  ?item rdfs:label ?attraction ; tour:locatedInCity ?cityResource .
  ?cityResource rdfs:label ?city ;
                tour:locatedInCountry ?countryResource .
  ?countryResource rdfs:label ?country .
}''')
    add_body(doc, "Запит виконує проходження трьох послідовних семантичних зв’язків і повернув 20 рядків — по одному для кожної пам’ятки, включеної до маршрутів.")

    add_heading(doc, "Запит 5. Середня ціна за типом пам’ятки", level=2)
    add_code(doc, '''SELECT ?type (AVG(?price) AS ?averagePrice)
             (COUNT(?item) AS ?count) WHERE {
  ?item a tour:Attraction ; tour:hasAttractionType ?typeResource ;
        tour:entryPriceEUR ?price .
  ?typeResource rdfs:label ?type .
}
GROUP BY ?type
ORDER BY DESC(?averagePrice)''')
    add_table(doc, ["Тип", "Середня ціна, EUR", "Кількість"], [
        ("Монумент", "7.50", "2"),
        ("Релігійна пам’ятка", "6.25", "4"),
        ("Музей", "6.00", "3"),
        ("Історична пам’ятка", "2.00", "3"),
        ("Парк", "0.00", "3"),
    ], widths=[8.5, 4.5, 3.0])

    add_heading(doc, "Зв’язування з Wikidata")
    add_body(doc, "Відомі сутності локального графа пов’язані з відповідними елементами Wikidata предикатом owl:sameAs. Такий зв’язок означає, що локальний URI та URI Wikidata ідентифікують той самий об’єкт. Це дає змогу поєднувати власний граф із зовнішніми відкритими даними.")
    add_table(doc, ["Локальний ресурс", "Wikidata"], [
        ("Україна", "Q212"),
        ("Київ", "Q1899"),
        ("Софійський собор", "Q830054"),
        ("Золоті ворота", "Q4289171"),
        ("Майдан Незалежності", "Q863759"),
        ("Києво-Печерська лавра", "Q242711"),
    ], widths=[10.0, 6.0])
    add_code(doc, '''<https://example.org/tourism/attraction/maidan>
    owl:sameAs <http://www.wikidata.org/entity/Q863759> .''', "Лістинг 3 — приклад зовнішнього семантичного зв’язку")
    add_placeholder(doc, "МІСЦЕ ДЛЯ РИСУНКА 2", "Вставити знімок консолі після запуску python src/fetch_wikidata.py.")
    add_caption(doc, "Рисунок 2 — Перевірка пов’язаних сутностей у Wikidata")

    add_heading(doc, "Помилковий і виправлений приклад")
    add_body(doc, "Потенційна помилка полягає у збереженні числових значень як звичайних рядків. У такому разі SPARQL може виконувати лексикографічне, а не числове порівняння, а агрегат AVG не матиме коректного числового типу.")
    add_code(doc, '''# Помилково: значення не має числового datatype
graph.add((uri, TOUR.entryPriceEUR, Literal(item["price"])))

# Виправлено: явний тип xsd:decimal
graph.add((uri, TOUR.entryPriceEUR,
           Literal(str(item["price"]), datatype=XSD.decimal)))''', "Лістинг 4 — правильна типізація числового літерала")
    add_body(doc, "Явна типізація xsd:decimal забезпечує коректну роботу FILTER, ORDER BY та AVG. Аналогічний принцип застосовано до рейтингу; для населення використано xsd:integer.")

    add_heading(doc, "Опис програмного продукту та алгоритмів")
    modules = [
        ("src/rdf_model.py", "модель предметної області, побудова URI, класів, літералів і зв’язків"),
        ("src/create_kyiv_graph.py", "запуск побудови, приєднання ручного Turtle-фрагмента, серіалізація"),
        ("src/explore_graph.py", "перегляд властивостей ресурсу та трійок, де він є суб’єктом або об’єктом"),
        ("src/execute_queries.py", "послідовне завантаження та виконання п’яти SPARQL-файлів"),
        ("src/draw_graph.py", "підготовка візуального орієнтованого графа"),
        ("src/fetch_wikidata.py", "перевірка зовнішніх Wikidata URI"),
        ("src/validate_project.py", "автоматизована перевірка кількості трійок, класів, запитів і вихідних файлів"),
    ]
    add_table(doc, ["Модуль", "Призначення"], modules, widths=[6.0, 10.0])
    add_body(doc, "Основний алгоритм: 1) прочитати JSON; 2) створити класи й екземпляри; 3) додати властивості та зв’язки; 4) приєднати Turtle-фрагмент; 5) серіалізувати граф; 6) виконати SPARQL-запити; 7) побудувати візуалізацію; 8) запустити перевірку артефактів.")

    add_heading(doc, "Результати роботи")
    add_body(doc, "Після запуску основних сценаріїв отримано завершений RDF-граф і всі передбачені завданням артефакти. Вбудована перевірка підтвердила наявність класів, екземплярів, власних зв’язків, JSON-LD, ручного Turtle-фрагмента, п’яти SPARQL-запитів, owl:sameAs та PNG-візуалізації.")
    add_code(doc, '''Створено програмний граф: 169 трійок
Фінальний граф після ручного Turtle: 171 трійка
01_affordable_top_attractions.rq: 13 результатів
02_museums_by_city.rq: 3 результати
03_attractions_per_city.rq: 1 результат
04_route_city_country.rq: 20 результатів
05_average_price_by_type.rq: 5 результатів
Візуалізація: 28 вузлів, 65 ребер
Перевірка проєкту: усі перевірки OK''', "Лістинг 5 — узагальнений результат виконання")
    add_placeholder(doc, "МІСЦЕ ДЛЯ РИСУНКА 3", "Вставити знімок консолі з результатом python src/validate_project.py.")
    add_caption(doc, "Рисунок 3 — Результат автоматичної перевірки проєкту")

    add_heading(doc, "Використання штучного інтелекту")
    add_body(doc, "Штучний інтелект використовувався як допоміжний інструмент для аналізу вимог, структурування програмного рішення та підготовки пояснень. RDF-модель, SPARQL-запити, зовнішні ідентифікатори й результати запуску перевірялися за кодом і вихідними файлами.")

    add_heading(doc, "Репозиторій")
    add_body(doc, "Код і дані зберігаються у Git-репозиторії semantic-labs. Перед здачею тут слід додати URL віддаленого репозиторію, якщо він потрібний викладачеві.")
    add_placeholder(doc, "МІСЦЕ ДЛЯ ПОСИЛАННЯ", "Вставити адресу GitHub/GitLab-репозиторію або видалити цей блок, якщо посилання не потрібне.")

    add_heading(doc, "Висновки")
    add_body(doc, "Побудовано RDF-граф предметної області «Міський туризм у Києві»: п’ять класів, п’ять власних типів зв’язків, 20 пам’яток і 171 трійка. Граф серіалізовано у Turtle та JSON-LD, доповнено ручним Turtle-фрагментом і пов’язано з Wikidata.")
    add_body(doc, "SPARQL-запити продемонстрували фільтрацію, сортування, COUNT, AVG і проходження ланцюжка маршрут → пам’ятка → місто → країна. Рішення відтворюється з локального JSON-джерела та перевіряється окремим сценарієм валідації.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build_report()
