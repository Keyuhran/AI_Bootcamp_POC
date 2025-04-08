# Project Scope/Background

At Public Utilities Board (PUB), Singapore’s National Water Agency's Water Quality Department (WQD), we conduct water quality tests to ensure the safety of Singapore's water supply system. Beside testing works, we also take the lead to front internal and external water quality issues. We spend a considerable amount of time replying to queries involving water quality issues. Although we receive an average of 1-2 queries per day, we do not have a dedicated team to respond to these queries.

We conducted a review and determined that most of these queries fall under a few themes (1) water quality parameters in the regulations and our water supply, (2) water quality testing, (3) potential collaborators (4) enquiry on the treatment technologies in PUB. How can we more effectively (accurately) and efficiently (reduce lead-time and resources required) in responding to public queries on water quality issues?

# Objectives

We plan to implement a Large Language Model (LLM) to draft responses to water quality issues. The main idea reduces manhours to free up our staff to handle more complex / critical inquiries. For context, a typical customer response requires approximately 4 manhours to be drafted and cleared. With the implementation of a Generative AI (GenAI) chatbot, the turnaround time will be reduced to 2 hours on average. We envisage this solution to be used on a daily basis.

The data source for this LLM models include: (1) water quality data from various regulations and (2) SFA regulatory requirements, and a database of email archives, to generate the email responses. This LLM aims to provide a draft email for proof-reading, by tapping on its ability to reason with complex information and string together a logical and grammatically correct response, while tapping on the GenAI features of this LLM model to understand the context of the queries.

# Data Source

The data source used in this model includes:

1.  Water quality data in a csv file, where information is obtained from the following guideline/regulatory standards:

    a.  Environmental Public Health (EPH) (Water Suitable for Drinking) (No. 2) Regulations 2019

    b.  PUB Drinking Water Quality Report (July 2023 – June 2024)

    c.  Singapore Food Agency (SFA)’s Code of Practice on Drinking Water Sampling and Safety Plans (2019), [Issued under the provisions of the EPH (Water Suitable for Drinking) (No. 2) Regulations 2019]

    d.  World Health Organization (WHO)’s Guidelines for drinking-water Quality (4th edition, incorporating first and second addenda)

2.  Email archives

    a.  Enquiry on water quality testing (services, accreditation)

    b.  Enquiry on water quality matters

        -  Specific parameters on water supply (chloride, dissolved oxygen, fluoride, heavy metals, PFAS, plate count, resistivity

        -  Water quality standards/reports, testing

            1.  Standard Methods for the Examination of Water and Wastewater

            2.  WHO’s Guidelines for drinking water Quality

            3.  USEPA National Primary Drinking Water Regulations

        -  Other analysis methods

        -  Sighted issue (i.e. discoloured water, scaling after boiling, pollution)

        -  Monitoring of water quality in network, supplies

    c.  Enquiry on treatment technologies, types and methods pertaining to:

        -  Desalination

        -  Reservoirs

        -  Disinfection

    d.  Alerts to false reporting of water quality information by other companies to promote their products

    e.  Miscellaneous enquiries

        -  Rerouted emails from various agencies, such as NEA, SFA

        -  Outreach

        -  Innovation challenge

        -  Tech providers promoting their products for use in PUB’s operations

        -  Potential collaborators (aquaculture technology, filters for sewers, treatment of PFAS etc.)

We noted that there are unlimited data sources that we can tap on as there are many possibilities from the email enquiries. For this Proof-of-Concept (PoC), we have curated a database to summarise these enquiries and cover most of the breadth of the enquiries, so as to demonstrate the effectiveness of the chatbot.

# Features

**Security Features:** Password protection through a ‘check password’ function. If authentication fails, the chatbot will prevent any further code execution. Embedded code to prevent prompt injection and hacking.

**Contextual Search and Retrieval**: Users are presented with two flexible input methods: they can either directly paste email text into a spacious text area or upload .msg email files, making it convenient for different use cases. The chatbot could leverage natural language processing (through a user’s query) and information retrieval techniques (for email uploads) to understand the context and intent. This would allow the chatbot to search its knowledge base and provide relevant responses, rather than just matching keywords. The interface maintains a clean, centered layout with clear navigation options, including the ability to return to the input page and start over. Throughout the process, all email content and generated responses are stored in the session state, ensuring no data is lost during user interactions.

**Response Generation**: The workflow is streamlined: once content is submitted (either through text input or file upload), it's processed through the ‘full_workflow’ function, which generates appropriate responses for water quality-related queries. The result is then displayed alongside the original content, allowing users to review both pieces of information simultaneously. This thoughtful design creates an efficient tool for handling water quality-related email communications while maintaining professionalism and user-friendliness.

# About Us

Project Leader Matthew Loh is an Assistant Director (QA and Regulations) in the QA Inspectorate Division of the Water Quality Department (WQD) at PUB.

Arvind Dev is a Senior Engineer (Operations) from the Water Supply (Plants) (WSP) Department at PUB. He is based in Johor River Waterworks (JRWW).

Loh Wei Hao is a Senior Specialist in the Tech Development Section in the Research and Technology Office of the Technology and Engineering Department (TED) at PUB.
