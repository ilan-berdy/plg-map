const FACILITY_BY_STATE = {
  "Alabama": {
    "large": [
      "Tenet Healthcare",
      "Community Health Systems Inc",
      "UAB Medicine",
      "Huntsville Hospital Health System",
      "Crestwood Medical Center"
    ],
    "small": [
      "Vascular Center of Mobile",
      "The Myers Institute"
    ]
  },
  "Alaska": {
    "large": [
      "HCA Healthcare",
      "Community Health Systems Inc"
    ],
    "small": [
      "Empower Physical Therapy"
    ]
  },
  "Arizona": {
    "large": [
      "Tenet Healthcare",
      "Community Health Systems Inc"
    ],
    "small": [
      "Blue Water Psychiatry",
      "Harvest Physical Therapy, LLC",
      "Sonoran Vein and Endovascular",
      "Healthspan MD, PLLC",
      "Spine Orthopedic and Sports Physical Therapy Inc",
      "The Physio Shop Tucson, LLC"
    ]
  },
  "Arkansas": {
    "large": [
      "Community Health Systems Inc"
    ],
    "small": [
      "Coulter Physical Therapy, Inc.",
      "Arkansas - HRS",
      "Ozarks Community Hospital"
    ]
  },
  "California": {
    "large": [
      "HCA Healthcare",
      "Tenet Healthcare",
      "Keck Hospital of USC (FKA USC University Hospital)",
      "Childrens Hospital Los Angeles",
      "Vibra Healthcare",
      "Community Hospital of the Monterey Peninsula (AKA Montage Health)",
      "UCLA Medical Center - Santa Monica",
      "Community Memorial Health System",
      "MarinHealth Medical Center (FKA Marin General Hospital)"
    ],
    "small": [
      "My Care Labs",
      "GLA Office Management",
      "Arthur J. Ting, M.D.",
      "ONclick Healthcare",
      "Ascent Urology",
      "Serrano Kidney and Vascular Access Center"
    ]
  },
  "Colorado": {
    "large": [
      "HCA Healthcare",
      "Childrens Hospital Colorado System"
    ],
    "small": [
      "Pikes Peak Orthopaedic Surgery and Sports Medicine",
      "Elevated Internal Medicine",
      "EDGE REHABILITATION & WELLNESS LLC",
      "Health Now",
      "CO Physio Pro & Panther PT - Evolution Physical Therapy",
      "All Abilities - HRS"
    ]
  },
  "Connecticut": {
    "large": [
      "Yale New Haven Health"
    ],
    "small": [
      "SYNERGY ADVANCED HEALTHCARE",
      "Evolve Brain Health",
      "Evolution Physical Therapy & Fitness",
      "Connecticut Region - Evolution Physical Therapy, LLC",
      "CT Sports PT - Evolution Physical Therapy"
    ]
  },
  "Delaware": {
    "large": [],
    "small": []
  },
  "Florida": {
    "large": [
      "HCA Healthcare",
      "Tenet Healthcare",
      "Community Health Systems Inc",
      "Lakeland Regional Health"
    ],
    "small": [
      "Osteoporosis & Rheumatology Center of Tampa Bay LLC",
      "Advanced Hand and Plastic Surgery Center, LLC",
      "FitOn Care",
      "Orthopaedic Center of Vero Beach",
      "Ponte Vedra Spine and Pain Center",
      "Vado Therapy"
    ]
  },
  "Georgia": {
    "large": [
      "HCA Healthcare",
      "Community Health Systems Inc"
    ],
    "small": [
      "Hypertension & Kidney Care of North Atlanta",
      "QuikClinic",
      "Back in the Game Physical Therapy",
      "Origin Healthcare (DBA Midtown ENT)",
      "Stout Healthcare",
      "Quest - HRS"
    ]
  },
  "Hawaii": {
    "large": [
      "The Queens Health Systems"
    ],
    "small": [
      "Lanai Community Health Center",
      "Waimea Primary Care LLC"
    ]
  },
  "Idaho": {
    "large": [
      "HCA Healthcare"
    ],
    "small": [
      "Family First Medical Center",
      "Asthma & Allergy of Idaho LLC",
      "Streamline Sports Physical Therapy, PC",
      "Pilot North Therapy Group",
      "Wright Physical Therapy",
      "Elevate Physical Therapy"
    ]
  },
  "Illinois": {
    "large": [
      "Hospital Sisters Health System Enterprise",
      "Memorial Health (Springfield IL)",
      "University of Illinois Hospital & Health Sciences System (AKA UI Health)"
    ],
    "small": [
      "Legends Home Therapy",
      "Progressive Medical Center SC",
      "Chicago Area Rehab Experts",
      "Legends Wound Care",
      "Oasis Therapy Services",
      "GI Partners of Illinois, LLC"
    ]
  },
  "Indiana": {
    "large": [
      "HCA Healthcare",
      "Community Health Systems Inc",
      "Beacon Health System",
      "Union Health"
    ],
    "small": [
      "Woodway Internal Medicine"
    ]
  },
  "Iowa": {
    "large": [
      "HCA Healthcare"
    ],
    "small": []
  },
  "Kansas": {
    "large": [
      "Saint Lukes Health System (Kansas City MO)"
    ],
    "small": [
      "Rebound Physical Therapy"
    ]
  },
  "Kentucky": {
    "large": [
      "University of Louisville Physicians"
    ],
    "small": [
      "Fuller Physical Therapy",
      "BP - Commonwealth Foot and Ankle"
    ]
  },
  "Louisiana": {
    "large": [
      "Ochsner Health System",
      "University Medical Center New Orleans (FKA Medical Center of Louisiana at New Orleans and Interim LSU Public Hospital)",
      "St Tammany Parish Hospital",
      "Touro Infirmary",
      "West Jefferson Medical Center",
      "Slidell Memorial Hospital"
    ],
    "small": [
      "Pedro Romaguera APMC",
      "Magnolia Pediatrics"
    ]
  },
  "Maine": {
    "large": [
      "Eastern Maine Health Systems"
    ],
    "small": []
  },
  "Maryland": {
    "large": [
      "Brook Lane Psychiatric Center"
    ],
    "small": [
      "Surgical Associates Chartered",
      "Innovative Physical Therapy and Fitness Centers LLC"
    ]
  },
  "Massachusetts": {
    "large": [
      "Tenet Healthcare",
      "Beth Israel Lahey Health",
      "Boston Childrens Hospital Health System",
      "Baystate Medical Center",
      "Boston Medical Center",
      "Harrington Healthcare"
    ],
    "small": [
      "Men's Health Boston",
      "NEUROLOGY PARTNERS, PC",
      "Town Center Pediatrics",
      "Pedi-Q Urgent Care"
    ]
  },
  "Michigan": {
    "large": [
      "Tenet Healthcare",
      "Metro Health Hospital"
    ],
    "small": [
      "Premier Medicine PC",
      "Michigan Women's Care, PLLC",
      "Crossley Wellness Center",
      "Beyond Podiatry",
      "BP - Great Lakes Foot and Ankle",
      "BP - Michigan Foot and Ankle"
    ]
  },
  "Minnesota": {
    "large": [
      "Olmsted Medical Center"
    ],
    "small": [
      "Life Medical P.A."
    ]
  },
  "Mississippi": {
    "large": [
      "HCA Healthcare",
      "Community Health Systems Inc",
      "Ochsner Health System"
    ],
    "small": [
      "Cooper Family Med Center Inc",
      "Creekmore Clinic",
      "MAYS MEDICAL WELLNESS, LLC",
      "Southern Physical Therapy"
    ]
  },
  "Missouri": {
    "large": [
      "HCA Healthcare",
      "Community Health Systems Inc",
      "Saint Lukes Health System (Kansas City MO)"
    ],
    "small": []
  },
  "Montana": {
    "large": [],
    "small": [
      "Health Rehab Solutions",
      "Kalispell Rehabilitation Associates, Inc. - HRS",
      "Lake - HRS",
      "Big Sky - HRS",
      "Pintler PT - HRS",
      "Yellowstone - HRS"
    ]
  },
  "Nebraska": {
    "large": [],
    "small": [
      "ENT Physicians of Kearney",
      "Rehab Guru Physical Therapy"
    ]
  },
  "Nevada": {
    "large": [
      "HCA Healthcare"
    ],
    "small": [
      "Dr. Philip Malinas MD and Associates",
      "Nevada Surgical",
      "Encompass Care",
      "Orthopaedic Institute of Henderson",
      "Sierra Foot and Ankle",
      "SAGE SURGICAL & NEUROMODULATION LLC"
    ]
  },
  "New Hampshire": {
    "large": [
      "HCA Healthcare",
      "Beth Israel Lahey Health",
      "St Joseph Hospital of NH"
    ],
    "small": []
  },
  "New Jersey": {
    "large": [
      "Jefferson Health",
      "Virtua Health",
      "Cooper University",
      "Capital Health",
      "Inspira Health Network (FKA South Jersey Healthcare)",
      "AtlantiCare Health System"
    ],
    "small": [
      "Premier Vein & Vascular",
      "Beyond Radix Physical Therapy",
      "Professional Pain Associates",
      "Springfield Physical Therapy and Wellness"
    ]
  },
  "New Mexico": {
    "large": [
      "Community Health Systems Inc",
      "University of New Mexico Hospital (AKA UNM Hospital)"
    ],
    "small": [
      "Donald E Wenner III MD PC",
      "Sleep Lab of Las Cruces, LLC"
    ]
  },
  "New York": {
    "large": [
      "Northwell",
      "NewYork-Presbyterian Healthcare System",
      "Memorial Sloan-Kettering Cancer Center",
      "Westchester Medical Center Health Network",
      "Albany Medical Center",
      "White Plains Hospital",
      "Bassett Healthcare Network",
      "Mount Sinai South Nassau (FKA South Nassau Communities Hospital)",
      "University Hospital of Brooklyn at SUNY Downstate Medical Center",
      "Ellis Medicine",
      "Richmond University Medical Center",
      "Cayuga Health System"
    ],
    "small": [
      "Lattimore of Brownstone",
      "Orthopedic Plus - Physical Therapy Center PLLC",
      "Focus Physical Therapy of Olean",
      "Donald C. Wallerson, M.D. PLLC",
      "Movement Concepts Physical Therapy",
      "Rockland Urgent Care Family Health NP, P.C."
    ]
  },
  "North Carolina": {
    "large": [
      "HCA Healthcare",
      "Community Health Systems Inc",
      "Ashe Memorial Hospital"
    ],
    "small": [
      "Precision Health",
      "NC Kidney Care",
      "Cedar Creek Family Medicine",
      "Integrative Therapies",
      "Carolina Pain and Weight Loss"
    ]
  },
  "North Dakota": {
    "large": [],
    "small": [
      "Home Therapy Solutions LLC"
    ]
  },
  "Ohio": {
    "large": [
      "HCA Healthcare",
      "Cincinnati Childrens Hospital Medical Center",
      "TriHealth",
      "Summa Health (FKA Summa Health System)"
    ],
    "small": [
      "Oxford Physical Therapy",
      "BP - Five Clinics",
      "BP - Podiatry Associates of Ohio"
    ]
  },
  "Oklahoma": {
    "large": [
      "HCA Healthcare",
      "Community Health Systems Inc"
    ],
    "small": [
      "ORTHO PLUS HOLDINGS, LLC",
      "Ortho Plus, LLC",
      "Regional Physical Therapy Inc",
      "Courcier Clinic Physical Therapy",
      "Just Kids Pediatrics"
    ]
  },
  "Oregon": {
    "large": [
      "HCA Healthcare"
    ],
    "small": [
      "Equinox Clinics",
      "Visionary Psychiatry"
    ]
  },
  "Pennsylvania": {
    "large": [
      "HCA Healthcare",
      "Community Health Systems Inc",
      "Jefferson Health",
      "Geisinger (FKA Geisinger Health System)",
      "WellSpan Health",
      "Childrens Hospital of Philadelphia (AKA CHOP)",
      "Main Line Health",
      "Crozer Health (FKA Crozer-Keystone Health System)",
      "Vibra Healthcare"
    ],
    "small": [
      "Endeavor Health",
      "Hillside Foot and Ankle",
      "Functional Freedom",
      "West Park Rehab",
      "Cloudline Physical Therapy"
    ]
  },
  "Rhode Island": {
    "large": [
      "Yale New Haven Health"
    ],
    "small": [
      "Core of Hope Psychiatry",
      "Pediatric Associates, Inc"
    ]
  },
  "South Carolina": {
    "large": [
      "Tenet Healthcare",
      "Prisma Health (FKA SC Health Company)"
    ],
    "small": [
      "Southern Urgent Care",
      "Coastal Sleep Lab, Inc",
      "HopeHealth, Inc."
    ]
  },
  "South Dakota": {
    "large": [],
    "small": []
  },
  "Tennessee": {
    "large": [
      "HCA Healthcare",
      "Tenet Healthcare",
      "Community Health Systems Inc",
      "Vanderbilt University Medical",
      "Regional Medical Center (AKA Regional One Health Hospital)"
    ],
    "small": [
      "Allergic Diseases, Asthma, and Immunology Clinic, PC",
      "William Van Bingham MD PC",
      "Restorative Family Medicine",
      "Gary J Smith MD PC",
      "Hardin Medical Center"
    ]
  },
  "Texas": {
    "large": [
      "HCA Healthcare",
      "Tenet Healthcare",
      "Community Health Systems Inc",
      "Vibra Healthcare",
      "Baylor Scott & White Medical Center - Frisco"
    ],
    "small": [
      "Keller Surgical",
      "Prime MD Geriatrics",
      "APEC Holdings, Corp.",
      "Wichita Heart & Vascular Center PLLC",
      "Top of Texas Psychiatry PLLC",
      "Arlington Physical Therapy PC"
    ]
  },
  "Utah": {
    "large": [
      "HCA Healthcare"
    ],
    "small": [
      "Optimal Health Family Practice LLC",
      "Intensive Physical Therapy Insitute",
      "Meier & Marsh Professional Therapies, LLC.",
      "Bushnell Physical Therapy",
      "BE WELL HEALTHCARE",
      "Alder Grove Pediatrics"
    ]
  },
  "Vermont": {
    "large": [],
    "small": []
  },
  "Virginia": {
    "large": [
      "HCA Healthcare"
    ],
    "small": [
      "Kemet Health",
      "PACS Urgent Care",
      "Pediatric Associates of Charlottesville",
      "Virginian Physical Therapy and Staffing",
      "Universal Health Corporation",
      "Professional Rehab Associates, Inc."
    ]
  },
  "Washington": {
    "large": [
      "Virginia Mason Seattle Medical Center",
      "Harborview Medical Center",
      "Mid-Valley Hospital"
    ],
    "small": [
      "Cascade Foot and Ankle Clinic",
      "Cascade Practice Management",
      "En Pointe Physical Therapy",
      "ProActive Sports Med",
      "North Peninsula Physical Therapy",
      "Next Level Physical Therapy and Performance Inc."
    ]
  },
  "West Virginia": {
    "large": [
      "Vandalia Health"
    ],
    "small": []
  },
  "Wisconsin": {
    "large": [
      "Hospital Sisters Health System Enterprise"
    ],
    "small": [
      "Great Midwest Foot and Ankle Centers, S.C.",
      "Beam Healthcare"
    ]
  },
  "Wyoming": {
    "large": [],
    "small": [
      "Core Physical Therapy",
      "Specialty Counseling & Consulting"
    ]
  }
};
