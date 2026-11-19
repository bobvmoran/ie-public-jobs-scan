"""Pages the weekly scan reads.

Each entry:
  slug  - file name for the saved page (data/pages/<slug>.md)
  name  - human label
  url   - public page to open (search/listing pages only)
  pages - optional: how many result pages to follow by clicking a "Next" link (default 1)

Add a URL here when you find a useful public listing page. Keep it to search
or listing pages that anyone can open without signing in.
"""

PJ_BOARD = (
    "https://publicjobs.tal.net/vx/lang-en-GB/mobile-0/appcentre-ext/brand-4/"
    "xf-423dd989250d/candidate/jobboard/vacancy/3/adv/"
)

SOURCES = [
    # --- publicjobs.ie ---
    *[
        {"slug": f"publicjobs-board-{s}", "name": f"publicjobs job board (from {s})",
         "url": f"{PJ_BOARD}?start={s}"}
        for s in (0, 50, 100, 150, 200, 250)
    ],
    {"slug": "publicjobs-news", "name": "publicjobs Latest news and events",
     "url": "https://www.publicjobs.ie/en/information-hub/latest-news-and-events"},

    # --- HSE / Tusla ---
    {"slug": "hse-limerick", "name": "HSE jobs - Limerick",
     "url": "https://about.hse.ie/jobs/job-search/?county=Limerick", "pages": 3},
    {"slug": "hse-cork", "name": "HSE jobs - Cork",
     "url": "https://about.hse.ie/jobs/job-search/?county=Cork", "pages": 3},
    {"slug": "hse-clare", "name": "HSE jobs - Clare",
     "url": "https://about.hse.ie/jobs/job-search/?county=Clare", "pages": 2},
    {"slug": "hse-tipperary", "name": "HSE jobs - Tipperary",
     "url": "https://about.hse.ie/jobs/job-search/?county=Tipperary", "pages": 2},
    {"slug": "hse-kerry", "name": "HSE jobs - Kerry",
     "url": "https://about.hse.ie/jobs/job-search/?county=Kerry", "pages": 2},
    {"slug": "hse-mgmt-admin-ict", "name": "HSE jobs - Management/Admin/ICT",
     "url": "https://about.hse.ie/jobs/job-search/?category=management%2Fadmin%2Fict", "pages": 5},
    {"slug": "hse-tech-transformation", "name": "HSE jobs - Technology & Transformation team",
     "url": "https://about.hse.ie/jobs/job-search/?team=Technology%20and%20transformation&health_region="},
    {"slug": "tusla-live", "name": "Tusla live jobs",
     "url": "https://tusla-candidate.thehirelab.com/livejobs"},

    # --- Aggregators ---
    *[
        {"slug": f"irishjobs-{p.strip('/').replace('/', '-')}", "name": f"irishjobs.ie {p}",
         "url": f"https://www.irishjobs.ie/jobs/{p}"}
        for p in ("assistant-principal", "principal-officer", "head-of-data", "head-of-ict",
                  "head-of-digital", "data/in-limerick", "data-manager/in-cork",
                  "public-sector", "civil-service")
    ],
    *[
        {"slug": f"jobsie-{p}", "name": f"jobs.ie {p}", "url": f"https://www.jobs.ie/jobs/{p}"}
        for p in ("data-analytics", "assistant-principal", "public-sector")
    ],
    {"slug": "analytics-institute", "name": "Analytics Institute job board",
     "url": "https://analyticsinstitute.org/resources/job-listing.html"},
    {"slug": "jobs-ac-uk-ireland", "name": "jobs.ac.uk - Ireland",
     "url": "https://www.jobs.ac.uk/categories/ireland-jobs/1"},

    # --- Local government ---
    {"slug": "localgovernmentjobs", "name": "localgovernmentjobs.ie vacancies",
     "url": "https://www.localgovernmentjobs.ie/Search/Vacancies", "pages": 5},
    {"slug": "lgma", "name": "LGMA work with us",
     "url": "https://www.lgma.ie/en/about-us/work-with-us/"},

    # --- Garda / Staffline ---
    {"slug": "garda-data-tech", "name": "Garda Data & Technology coming soon",
     "url": "https://www.garda.ie/en/careers/career-opportunities-for-garda-staff/coming-soon-competitions-for-roles-in-the-area-of-data-technology-in-an-garda-siochana.html"},
    {"slug": "staffline-getgot", "name": "Staffline GetGot listings",
     "url": "https://staffline.getgotjobs.ie/listings"},

    # --- State bodies ---
    {"slug": "revenue", "name": "Revenue career opportunities",
     "url": "https://www.revenue.ie/en/corporate/information-about-revenue/careers/career-opportunities.aspx"},
    {"slug": "cso", "name": "CSO vacancies",
     "url": "https://www.cso.ie/en/aboutus/careers/ourvacancies/"},
    {"slug": "central-bank", "name": "Central Bank current vacancies",
     "url": "https://www.centralbank.ie/careers/current-vacancies"},
    {"slug": "cib", "name": "Citizens Information Board vacancies",
     "url": "https://www.citizensinformationboard.ie/en/news/vacancies.html"},
    {"slug": "crr", "name": "Commission for Railway Regulation careers",
     "url": "https://www.crr.ie/about/careers/"},
    {"slug": "conscia", "name": "Conscia Talent job results",
     "url": "https://www.consciatalent.com/job-results"},
    {"slug": "comreg", "name": "ComReg careers", "url": "https://www.comreg.ie/about/careers/"},
    {"slug": "cnam", "name": "Coimisiun na Mean vacancies",
     "url": "https://www.cnam.ie/about/careers/current-vacancies/"},
    {"slug": "hiqa", "name": "HIQA careers", "url": "https://www.hiqa.ie/about-us/careers"},
    {"slug": "dpc", "name": "Data Protection Commission careers",
     "url": "https://www.dataprotection.ie/en/who-we-are/careers"},
    {"slug": "esb-data", "name": "ESB careers - data",
     "url": "https://careers.esb.ie/search/?q=data"},
    {"slug": "esb-ict", "name": "ESB careers - ICT",
     "url": "https://careers.esb.ie/search/?q=ICT"},

    # --- Universities ---
    {"slug": "tus", "name": "TUS HR vacancies", "url": "https://tus.ie/hr/vacancies/"},
    {"slug": "atu-academic", "name": "ATU academic jobs",
     "url": "https://www.atu.ie/connect/jobs/academic-jobs"},
    {"slug": "ucc-compsci", "name": "UCC Computer Science vacancies",
     "url": "https://www.ucc.ie/en/compsci/vacancies/overview/"},
    # Add UL, MTU and SETU vacancy pages here once you have their public URLs.
]
