"""
Raw seed dataset of ~25 sample job postings.
These are realistic raw postings as they'd come from scraping.
"""

RAW_POSTINGS = [
    {
        "source": "rozee.pk",
        "posting_id": "rozee_001",
        "raw_html": """
        <h2>Senior Backend Engineer</h2>
        <p><strong>Company:</strong> TechFlow Solutions</p>
        <p><strong>Location:</strong> Karachi</p>
        <p><strong>Posted:</strong> 2024-08-25</p>
        <p><strong>Description:</strong>
        We're hiring a Senior Backend Engineer to lead our cloud infrastructure team.
        5+ years of experience required.
        <br/><br/>
        <strong>Responsibilities:</strong>
        Design and implement scalable backend systems using Python and FastAPI.
        Architect microservices using Docker and Kubernetes.
        Lead code reviews and mentor junior developers.
        <br/><br/>
        <strong>Requirements:</strong>
        Strong proficiency in Python, FastAPI, and REST APIs.
        Experience with PostgreSQL and Redis.
        Kubernetes and Docker orchestration.
        AWS or GCP experience.
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_002",
        "raw_html": """
        <h2>Frontend Developer (React)</h2>
        <p><strong>Company:</strong> Creative Studios</p>
        <p><strong>Location:</strong> Lahore</p>
        <p><strong>Posted:</strong> 2024-08-23</p>
        <p>Join our growing frontend team! We build modern web applications with React and Next.js.
        <br/>
        <strong>Requirements:</strong> React, JavaScript/TypeScript, HTML/CSS, Git
        <br/>
        <strong>Nice to have:</strong> Next.js, Tailwind CSS, Jest testing
        <br/>
        Salary: 80k-120k PKR
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_003",
        "raw_html": """
        <h2>AI/ML Engineer - NLP Focus</h2>
        <p><strong>Company:</strong> DataMind AI</p>
        <p><strong>Location:</strong> Karachi</p>
        <p><strong>Posted:</strong> 2024-08-24</p>
        <p>We're building cutting-edge NLP models for Urdu language processing.
        <br/><br/>
        <strong>Key Skills Needed:</strong>
        Python (NumPy, Pandas, Scikit-learn)
        Deep Learning frameworks (PyTorch, TensorFlow)
        NLP libraries (spaCy, NLTK, Hugging Face Transformers)
        Experience with transformer models and fine-tuning.
        Git and collaborative development.
        </p>
        """
    },
    {
        "source": "linkedin",
        "posting_id": "linkedin_001",
        "raw_html": """
        <h1>DevOps Engineer - Infrastructure</h1>
        <p>Company: CloudTech Pakistan</p>
        <p>Location: Islamabad</p>
        <p>Posted Date: August 22, 2024</p>
        <p>Description: Manage and optimize our cloud infrastructure on AWS. 
        Implement CI/CD pipelines using GitHub Actions and Jenkins.
        Design and maintain Kubernetes clusters.
        <br/>
        Requirements: 
        - AWS certification or 3+ years AWS experience
        - Kubernetes and Docker
        - CI/CD tools (Jenkins, GitHub Actions, GitLab CI)
        - Linux system administration
        - Python scripting for automation
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_004",
        "raw_html": """
        <h2>Data Analyst</h2>
        <p><strong>Company:</strong> Analytics Plus</p>
        <p><strong>Location:</strong> Lahore</p>
        <p><strong>Posted:</strong> 2024-08-20</p>
        <p>We need a Data Analyst to drive insights from our business data.
        <br/>
        Skills Required:
        SQL (writing complex queries)
        Python (Pandas, NumPy)
        Excel (advanced formulas, pivot tables)
        Data visualization (Tableau, Power BI)
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_005",
        "raw_html": """
        <h2>Mobile App Developer (Flutter)</h2>
        <p><strong>Company:</strong> MobileFirst Apps</p>
        <p><strong>Location:</strong> Karachi</p>
        <p><strong>Posted:</strong> 2024-08-22</p>
        <p>Build beautiful cross-platform mobile apps with Flutter.
        <strong>Required:</strong> Dart, Flutter, REST APIs, Firebase
        <strong>Preferred:</strong> BLoC pattern, GetX, Hive database
        </p>
        """
    },
    {
        "source": "linkedin",
        "posting_id": "linkedin_002",
        "raw_html": """
        <h1>Full Stack Developer</h1>
        <p>Company: WebSolutions Inc</p>
        <p>City: Karachi</p>
        <p>Posted: August 21, 2024</p>
        <p>We're looking for a Full Stack Developer comfortable with both frontend and backend.
        <br/>
        Tech Stack: React, Node.js, Express, MongoDB, PostgreSQL
        <br/>
        Must have: JavaScript/TypeScript, REST APIs, Git
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_006",
        "raw_html": """
        <h2>QA Engineer - Automation</h2>
        <p><strong>Company:</strong> QualityAssure Ltd</p>
        <p><strong>Location:</strong> Lahore</p>
        <p><strong>Posted:</strong> 2024-08-25</p>
        <p>Automate our testing workflows.
        <strong>Skills:</strong> Selenium, Python, TestNG, Jest, Manual Testing
        <strong>Nice to have:</strong> CI/CD integration, API testing
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_007",
        "raw_html": """
        <h2>Product Manager - Tech</h2>
        <p><strong>Company:</strong> InnovateTech</p>
        <p><strong>Location:</strong> Islamabad</p>
        <p><strong>Posted:</strong> 2024-08-24</p>
        <p>Lead product strategy for our SaaS platform.
        <br/>
        <strong>Requirements:</strong>
        5+ years product management or closely related role
        Understanding of technical architecture (APIs, databases, cloud)
        Experience with data-driven product decisions
        Familiarity with Agile/Scrum
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_008",
        "raw_html": """
        <h2>Junior Python Developer</h2>
        <p><strong>Company:</strong> StartupXYZ</p>
        <p><strong>Location:</strong> Karachi</p>
        <p><strong>Posted:</strong> 2024-08-23</p>
        <p>Entry-level Python role. We'll mentor you!
        <strong>Need:</strong> Python basics, Django or FastAPI, SQL, Git
        </p>
        """
    },
    {
        "source": "linkedin",
        "posting_id": "linkedin_003",
        "raw_html": """
        <h1>Machine Learning Engineer</h1>
        <p>Company: AI Innovations</p>
        <p>Location: Karachi</p>
        <p>Date Posted: August 20, 2024</p>
        <p>Build ML pipelines for production recommendation systems.
        <br/>
        Stack: Python, TensorFlow/PyTorch, Scikit-learn, XGBoost
        <br/>
        Essential: 2+ years ML experience, Statistics/Math background, Big Data tools (Spark)
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_009",
        "raw_html": """
        <h2>Cloud Solutions Architect</h2>
        <p><strong>Company:</strong> EnterpriseCloud Co</p>
        <p><strong>Location:</strong> Lahore</p>
        <p><strong>Posted:</strong> 2024-08-19</p>
        <p>Design enterprise-scale cloud solutions.
        <strong>Required:</strong> AWS Solutions Architect certification, Terraform, CloudFormation, 7+ years experience
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_010",
        "raw_html": """
        <h2>Security Engineer</h2>
        <p><strong>Company:</strong> CyberShield</p>
        <p><strong>Location:</strong> Islamabad</p>
        <p><strong>Posted:</strong> 2024-08-22</p>
        <p>Secure our infrastructure and applications.
        <br/>
        <strong>Skills:</strong> 
        Linux/Windows security
        Network protocols and firewalls
        Penetration testing
        OWASP Top 10, secure coding
        Kubernetes security (bonus)
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_011",
        "raw_html": """
        <h2>Technical Content Writer</h2>
        <p><strong>Company:</strong> TechBlog Media</p>
        <p><strong>Location:</strong> Remote</p>
        <p><strong>Posted:</strong> 2024-08-24</p>
        <p>Write technical tutorials and guides.
        <strong>Must have:</strong> Strong English writing, understanding of software development
        <strong>Preferred:</strong> Git, Markdown, experience with REST APIs
        </p>
        """
    },
    {
        "source": "linkedin",
        "posting_id": "linkedin_004",
        "raw_html": """
        <h1>Solutions Engineer</h1>
        <p>Company: TechB2B Solutions</p>
        <p>City: Karachi</p>
        <p>Posted: August 19, 2024</p>
        <p>Bridge between sales and technical teams.
        <br/>
        Tech Knowledge: Cloud platforms (AWS/GCP), APIs, Databases
        <br/>
        Soft Skills: Communication, presentation, client management
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_012",
        "raw_html": """
        <h2>Database Administrator</h2>
        <p><strong>Company:</strong> DataCorp</p>
        <p><strong>Location:</strong> Lahore</p>
        <p><strong>Posted:</strong> 2024-08-21</p>
        <p>Manage and optimize databases.
        <strong>Skills:</strong> PostgreSQL, MySQL, Oracle, performance tuning, backup/recovery, replication
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_013",
        "raw_html": """
        <h2>GraphQL Backend Developer</h2>
        <p><strong>Company:</strong> ModernAPI Inc</p>
        <p><strong>Location:</strong> Karachi</p>
        <p><strong>Posted:</strong> 2024-08-24</p>
        <p>Build GraphQL APIs for modern applications.
        <strong>Requirements:</strong> Node.js, TypeScript, GraphQL, Apollo, MongoDB
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_014",
        "raw_html": """
        <h2>Business Analyst</h2>
        <p><strong>Company:</strong> ConsultPro</p>
        <p><strong>Location:</strong> Islamabad</p>
        <p><strong>Posted:</strong> 2024-08-23</p>
        <p>Analyze business requirements and drive solutions.
        <strong>Need:</strong> SQL, Excel, understanding of software development lifecycle, 3+ years relevant experience
        </p>
        """
    },
    {
        "source": "linkedin",
        "posting_id": "linkedin_005",
        "raw_html": """
        <h1>Blockchain Developer</h1>
        <p>Company: CryptoTech Labs</p>
        <p>Location: Lahore</p>
        <p>Posted Date: August 25, 2024</p>
        <p>Develop smart contracts and blockchain applications.
        <br/>
        Requirements: Solidity, Ethereum, Web3.js, Smart Contract Security
        <br/>
        Experience with DeFi protocols preferred.
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_015",
        "raw_html": """
        <h2>IT Support Specialist</h2>
        <p><strong>Company:</strong> TechSupport Ltd</p>
        <p><strong>Location:</strong> Lahore</p>
        <p><strong>Posted:</strong> 2024-08-25</p>
        <p>Provide technical support to users.
        <strong>Skills:</strong> Windows/Linux, Networking basics, Troubleshooting, Help desk tools
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_016",
        "raw_html": """
        <h2>Web Developer (PHP)</h2>
        <p><strong>Company:</strong> WebAgency</p>
        <p><strong>Location:</strong> Karachi</p>
        <p><strong>Posted:</strong> 2024-08-20</p>
        <p>Build web applications with PHP and Laravel.
        <strong>Required:</strong> PHP, Laravel, MySQL, JavaScript, HTML/CSS
        </p>
        """
    },
    {
        "source": "linkedin",
        "posting_id": "linkedin_006",
        "raw_html": """
        <h1>Product Designer</h1>
        <p>Company: DesignFirst Studio</p>
        <p>City: Karachi</p>
        <p>Posted: August 22, 2024</p>
        <p>Design beautiful user experiences.
        <br/>
        Tools: Figma, Adobe XD, Sketch
        <br/>
        Skills: UI/UX, prototyping, user research, wireframing
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_017",
        "raw_html": """
        <h2>DevOps/SRE</h2>
        <p><strong>Company:</strong> ScaleOps</p>
        <p><strong>Location:</strong> Islamabad</p>
        <p><strong>Posted:</strong> 2024-08-24</p>
        <p>Ensure system reliability and performance.
        <strong>Skills:</strong> Terraform, Ansible, Prometheus, Grafana, ELK Stack, AWS, Kubernetes
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_018",
        "raw_html": """
        <h2>Senior Python Developer</h2>
        <p><strong>Company:</strong> PythonCorp</p>
        <p><strong>Location:</strong> Lahore</p>
        <p><strong>Posted:</strong> 2024-08-21</p>
        <p>Lead Python development team.
        <strong>Requirements:</strong> 5+ years Python, FastAPI/Django, PostgreSQL, Redis, Celery, design patterns
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_019",
        "raw_html": """
        <h2>React Native Developer</h2>
        <p><strong>Company:</strong> MobileInnovate</p>
        <p><strong>Location:</strong> Karachi</p>
        <p><strong>Posted:</strong> 2024-08-23</p>
        <p>Build mobile apps with React Native and TypeScript.
        <strong>Need:</strong> React Native, JavaScript/TypeScript, Firebase, Redux, Expo
        </p>
        """
    },
    {
        "source": "linkedin",
        "posting_id": "linkedin_007",
        "raw_html": """
        <h1>Site Reliability Engineer (SRE)</h1>
        <p>Company: CloudReliability Inc</p>
        <p>Location: Islamabad</p>
        <p>Posted: August 21, 2024</p>
        <p>Build reliable systems at scale.
        <br/>
        Stack: Go, Python, Kubernetes, Prometheus, service mesh
        <br/>
        Experience: 3+ years SRE/DevOps, incident response, capacity planning
        </p>
        """
    },
    {
        "source": "rozee.pk",
        "posting_id": "rozee_020",
        "raw_html": """
        <h2>Angular Developer</h2>
        <p><strong>Company:</strong> EnterpriseFront</p>
        <p><strong>Location:</strong> Lahore</p>
        <p><strong>Posted:</strong> 2024-08-25</p>
        <p>Build enterprise applications with Angular.
        <strong>Required:</strong> Angular 15+, TypeScript, RxJS, REST APIs, lazy loading
        </p>
        """
    },
]
