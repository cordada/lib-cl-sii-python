from __future__ import annotations

from datetime import datetime

from bs4 import BeautifulSoup

from .data_models import (
    LastFiledDocument,
    LegalRepresentative,
    Property,
    TaxpayerData,
    TaxpayerProperties,
    TaxpayerProvidedInfo,
)


def parse_taxpayer_provided_info(html_content: str) -> TaxpayerProvidedInfo:
    """
    Parse the CTE HTML content to extract the content of the section:
    "Información proporcionada por el contribuyente para fines tributarios (1)"

    Args:
        html_content: HTML string containing the taxpayer information table

    Returns:
        TaxpayerProvidedInfo instance with the parsed data
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the main table with id="tbl_sociedades"
    table = soup.find('table', id='tbl_sociedades')

    if not table:
        raise ValueError("Could not find taxpayer information table in HTML")

    # Initialize lists for each section
    legal_representatives = []
    company_formation = []
    participation_in_companies = []

    # Current section being parsed
    current_section = None

    # Iterate through rows to extract data
    rows = table.find_all('tr')  # type: ignore[attr-defined]
    for row in rows:
        section_header = row.find(
            'span', class_='textof', string=lambda s: s and 'Representante(s) Legal(es)' in s
        )
        if section_header:
            current_section = 'legal_representatives'
            continue

        section_header = row.find(
            'span',
            class_='textof',
            string=lambda s: s and 'Conformación de la sociedad' in s,
        )
        if section_header:
            current_section = 'company_formation'
            continue

        section_header = row.find(
            'span',
            class_='textof',
            string=lambda s: s and 'Participación en sociedades vigentes' in s,
        )
        if section_header:
            current_section = 'participation_in_companies'
            continue

        # Skip rows without useful data
        cells = row.find_all('td')
        if len(cells) < 3:
            continue

        name_cell = cells[1].find('span', class_='textof')
        rut_cell = cells[2].find('span', class_='textof')
        date_cell = cells[3].find('span', class_='textof')

        # If this is a data row with person information
        if name_cell and rut_cell and date_cell and name_cell.text.strip():
            name = name_cell.text.strip()
            rut = rut_cell.text.strip()
            incorporation_date = date_cell.text.strip()

            person = LegalRepresentative(name=name, rut=rut, incorporation_date=incorporation_date)

            if current_section == 'legal_representatives':
                legal_representatives.append(person)
            elif current_section == 'company_formation':
                company_formation.append(person)
            elif current_section == 'participation_in_companies':
                participation_in_companies.append(person)

    return TaxpayerProvidedInfo(
        legal_representatives=legal_representatives,
        company_formation=company_formation,
        participation_in_existing_companies=participation_in_companies,
    )


def parse_taxpayer_data(html_content: str) -> TaxpayerData:
    """
    Parse the CTE HTML content to extract the content of the section:
    "Datos del Contribuyente"

    Args:
        html_content: HTML string containing the taxpayer information table

    Returns:
        TaxpayerData instance with the parsed data
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', id='tbl_dbcontribuyente')
    if not table:
        raise ValueError("Could not find 'Datos del Contribuyente' table in HTML")

    fecha_inicio_elem = table.find(id='td_fecha_inicio')  # type: ignore[attr-defined]
    if fecha_inicio_elem:
        start_of_activities_date = (
            datetime.strptime(fecha_inicio_elem.get_text(strip=True), "%d-%m-%Y").date()
            if fecha_inicio_elem.get_text(strip=True)
            else None
        )
    else:
        start_of_activities_date = None

    actividades_elem = table.find(id='td_actividades')  # type: ignore[attr-defined]
    if actividades_elem:
        economic_activities = actividades_elem.get_text(separator="\n", strip=True)
    else:
        economic_activities = ""

    categoria_elem = table.find(id='td_categoria')  # type: ignore[attr-defined]
    if categoria_elem:
        tax_category = categoria_elem.get_text(strip=True)
    else:
        tax_category = ""

    domicilio_elem = table.find(id='td_domicilio')  # type: ignore[attr-defined]
    if domicilio_elem:
        address = domicilio_elem.get_text(strip=True)
    else:
        address = ""

    # Sucursales
    branches = []
    sucursales_row = table.find(  # type: ignore[attr-defined]
        'td',
        string=lambda s: s and 'Sucursales:' in s,
    )
    if sucursales_row:
        sucursales_td = sucursales_row.find_next_sibling('td')
        if sucursales_td:
            branches_text = sucursales_td.get_text(separator="\n", strip=True)
            branches = [b for b in branches_text.split("\n") if b]

    # Últimos documentos timbrados
    last_filed_documents = []
    tim_nombre_elem = table.find(id='td_tim_nombre')  # type: ignore[attr-defined]
    tim_fecha_elem = table.find(id='td_tim_fecha')  # type: ignore[attr-defined]
    if tim_nombre_elem and tim_fecha_elem:
        names = tim_nombre_elem.get_text(separator="\n", strip=True).split("\n")
        dates = tim_fecha_elem.get_text(separator="\n", strip=True).split("\n")
        for name, date_str in zip(names, dates):
            if name and date_str:
                doc_date = datetime.strptime(date_str, "%d-%m-%Y").date()
                last_filed_documents.append(LastFiledDocument(name=name, date=doc_date))

    # Observaciones tributarias
    tax_observations = None
    observaciones_elem = table.find(id='td_observaciones')  # type: ignore[attr-defined]
    if observaciones_elem:
        tax_observations = observaciones_elem.get_text(strip=True)

    return TaxpayerData(
        start_of_activities_date=start_of_activities_date,
        economic_activities=economic_activities,
        tax_category=tax_category,
        address=address,
        branches=branches,
        last_filed_documents=last_filed_documents,
        tax_observations=tax_observations,
    )


def parse_taxpayer_properties(html_content: str) -> TaxpayerProperties:
    """
    Parse the CTE HTML content to extract the content of the section:
    "Propiedades y Bienes Raíces (3)"

    Args:
        html_content: HTML string containing the taxpayer properties table

    Returns:
        TaxpayerProperties instance with the parsed data
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the main table with id="tbl_propiedades"
    table = soup.find('table', id='tbl_propiedades')
    if not table:
        raise ValueError("Could not find taxpayer information table in HTML")

    properties = []
    rows = table.find_all('tr')  # type: ignore[attr-defined]
    for row in rows[2:]:  # Skip headers rows

        # Skip rows without useful data
        cells = row.find_all('td')
        if len(cells) < 8:
            continue

        commune = cells[0].get_text(strip=True) or None
        role = cells[1].get_text(strip=True) or None
        address = cells[2].get_text(strip=True) or None
        purpose = cells[3].get_text(strip=True) or None
        fiscal_valuation = cells[4].get_text(strip=True) or None
        overdue_installments = cells[5].get_text(strip=True) or None
        current_installments = cells[6].get_text(strip=True) or None
        condition = cells[7].get_text(strip=True) or None

        properties.append(
            Property(
                commune=commune,
                role=role,
                address=address,
                purpose=purpose,
                fiscal_valuation=fiscal_valuation,
                overdue_installments=overdue_installments,
                current_installments=current_installments,
                condition=condition,
            )
        )
    return TaxpayerProperties(properties=properties)
