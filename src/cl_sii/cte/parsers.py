from __future__ import annotations

from bs4 import BeautifulSoup

from .data_models import LegalRepresentative, TaxpayerProvidedInfo


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
