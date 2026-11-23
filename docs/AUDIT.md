# Accuracy audit, 200 random postings of 2098

Reproduce with `python scripts/audit_sample.py --n 200 --seed 1`.

| Check | Wrong | Rate |
|---|---|---|
| location is in the U.S. | 0 | 0.0% |
| title still passes the CS/CE title rules | 0 | 0.0% |
| title is not for a term that has passed | 0 | 0.0% |
| internship / new grad / early matches the title | 0 | 0.0% |
| every tag is reproduced by the sentence saved as its evidence | 1 | 0.5% |

**199 of 200 rows passed every check (99.5%).**

## Wrong: every tag is reproduced by the sentence saved as its evidence

- [RTX — FPGA Engineering Intern (Summer 2027)(Onsite)](https://globalhr.wd5.myworkdayjobs.com/REC_RTX_Ext_Gateway/job/US-TX-MCKINNEY-513WD--2501-W-University-Dr--WING-D-BLDG/FPGA-Engineering-Intern--Summer-2027--Onsite-_01880037) — clearance_level=secret but its evidence now reads None

## To judge by hand

Is each of these really a CS or CE job a student could do? Mark the ones that aren't.

- [ ] [Daimler Truck — IT Developer Analyst Intern](https://dtna.wd5.myworkdayjobs.com/DTNA_affiliate/job/Mount-Holly-NC-US/IT-Developer-Analyst-Intern_DT-20681-1) — Mount Holly, NC US
- [ ] [Bass Pro Shops — Product Testing and Validation Engineering Co-op](https://basspro.wd1.myworkdayjobs.com/careers/job/Springfield-MO-Tracker-Marine-Base-Camp/Product-Validation-Engineer-Co-Op_R267057) — Springfield, MO (Tracker Marine Base Camp)
- [ ] [Labcorp — Intern - People Analytics](https://labcorp.wd1.myworkdayjobs.com/External/job/Durham-NC/Intern---People-Analytics_2640527) — Durham NC
- [ ] [Ciena — WaveLogic Software Intern (Summer 2027)](https://ciena.wd5.myworkdayjobs.com/Careers/job/Atlanta/WaveLogic-Software-Intern--Summer-2027-_R031695) — Atlanta
- [ ] [Voloridge Investment Management — Quantitative Trading Intern 2027](https://job-boards.greenhouse.io/voloridgeinvestmentmanagement/jobs/4405530009) — Jupiter, FL
- [ ] [Tevora — Cybersecurity Internship Winter 2027 - Federal](https://jobs.lever.co/tevora/6d569b10-339d-4b86-9ae1-17ee462948a1) — Fairfax, VA
- [ ] [Trimble Inc — IS Help Desk Intern](https://trimble.wd1.myworkdayjobs.com/TrimbleCareers/job/US---CO-Westminster/IS-Help-Desk-Intern_R58179) — US - CO, Westminster
- [ ] [Rockwell Automation — Co-op, Hardware Development Engineer (Jan - July 2027)](https://rockwellautomation.wd1.myworkdayjobs.com/External-Rockwell-Automation-Early-Careers/job/Mayfield-Heights-Ohio-United-States/Co-op--Hardware-Development-Engineer--Jan---July-2027-_R26-6638) — Mayfield Heights, Ohio, United States
- [ ] [HNTB — Intern - AI Business Process Developer (Summer 2027)](https://hntb.wd5.myworkdayjobs.com/HNTB_University_Careers/job/Austin-TX/Intern---AI-Business-Process-Developer--Summer-2027-_R-31865) — Austin, TX
- [ ] [Bracco Medical Technologies — Software Engineering Intern/ Co-op (R&D Sustaining)](https://bracco.wd103.myworkdayjobs.com/BraccoCareers/job/USA-Eden-Prairie-Minnesota-55344/Software-Engineering-Intern--Co-op--R-D-Sustaining-_JR100327) — USA, Eden Prairie, Minnesota, 55344
- [ ] [Verkada — Technical Support Engineering Intern - Spring 2027](https://job-boards.greenhouse.io/verkada/jobs/5056164007) — San Mateo, CA United States
- [ ] [AMCA — Software Engineering Internship (Summer 2027)](https://job-boards.greenhouse.io/amca/jobs/4425120009) — El Segundo, CA
- [ ] [Samsung Semiconductor — Intern, SSD Firmware Development](https://job-boards.greenhouse.io/samsungsemiconductor/jobs/8203058003) — San Jose, California, United States
- [ ] [Stoke Space — Summer 2027 Internship - Software](https://job-boards.greenhouse.io/stokespacetechnologies/jobs/6176786004) — Kent, Washington
- [ ] [Acron Aviation — Software Engineer Intern - St. Pete Site](https://jobs.lever.co/acronaviation/19dbac7d-b4fb-4d21-9247-dc610bf55fed) — St Petersburg, FL
- [ ] [Tenet Healthcare Corporation — BI Developer Intern - Hybrid in Dallas, TX](https://eodr.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX/job/2603021909) — Dallas, TX, United States
- [ ] [LPL Financial Holdings — New Grad 2027 - Platform Engineer](https://lplfinancial.wd1.myworkdayjobs.com/University/job/Fort-MillCharlotte/New-Grad---2027---Platform-Engineering_R-052500-1) — Fort Mill/Charlotte
- [ ] [Insulet Corporation — Co-op, Embedded Software Test Engineering: January - June 2027 (Onsite)](https://insulet.wd5.myworkdayjobs.com/insuletcareers/job/Acton-Massachusetts/Co-op--Embedded-Software-Test-Engineering--January---June-2027--Onsite-_REQ-2026-18012) — Acton, Massachusetts
- [ ] [CACI International — Software Engineer Intern - Summer 2027](https://caci.wd1.myworkdayjobs.com/External/job/Omaha-NE-US/Software-Engineer-Intern---Summer-2027_332776) — Omaha, NE, US
- [ ] [NVIDIA — NVIDIA 2027 Internships: Hardware ASIC Design](https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/NVIDIA-2027-Internships--Hardware-ASIC-Design_JR2023486) — US, CA, Santa Clara
- [ ] [Amgen — Grad Intern – R&D TSRS Data Sciences Operations & Analytic (Summer 2027)](https://amgen.wd1.myworkdayjobs.com/Careers/job/United-States---Remote/Grad-Intern---R-D-TSRS-Data-Sciences-Operations---Analytic--Summer-2027-_R-260585) — United States - Remote
- [ ] [Amazon — Data Center Infrastructure Engineer Intern, Summer 2027 - East](https://www.amazon.jobs/en/jobs/10605141/data-center-infrastructure-engineer-intern-summer-2027-east) — Herndon, Virginia, USA
- [ ] [Amazon — Software Development Engineer Intern, Amazon Leo - Summer 2027 (USA)](https://www.amazon.jobs/en/jobs/10587999/software-development-engineer-intern-amazon-leo-summer-2027-usa) — Redmond, Washington, USA
- [ ] [AeroVironment — Summer 2027 GNC / Autonomy Intern](https://avav.wd1.myworkdayjobs.com/AVAV/job/Simi-Valley-CA/Summer-2027-GNC---Autonomy-Intern_8610) — Simi Valley, CA
- [ ] [Rockwell Automation — Intern, Information Technology](https://rockwellautomation.wd1.myworkdayjobs.com/External-Rockwell-Automation-Early-Careers/job/Milwaukee-Wisconsin-United-States/Intern--Information-Technology_R26-5374-1) — Milwaukee, Wisconsin, United States
