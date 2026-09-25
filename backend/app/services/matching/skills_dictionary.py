from typing import TypedDict

from app.schemas.requirement import RequirementCategory


class SkillEntry(TypedDict):
    canonical: str
    category: RequirementCategory
    aliases: list[str]


TECHNICAL_SKILL = RequirementCategory.TECHNICAL_SKILL
TOOL = RequirementCategory.TOOL
LANGUAGE = RequirementCategory.LANGUAGE
SOFT_SKILL = RequirementCategory.SOFT_SKILL

# ~50 kayıtlık iki dilli (TR/EN) beceri sözlüğü. KeywordMatcher, ilan metninde
# geçen kayıtları gereksinim, CV metninde geçen alias'ları da karşılık kabul eder.
SKILLS: list[SkillEntry] = [
    {"canonical": "Python", "category": TECHNICAL_SKILL, "aliases": ["python"]},
    {"canonical": "SQL", "category": TECHNICAL_SKILL, "aliases": ["sql"]},
    {
        "canonical": "Machine Learning",
        "category": TECHNICAL_SKILL,
        "aliases": ["machine learning", "ml", "makine öğrenmesi", "makine öğrenimi"],
    },
    {"canonical": "JavaScript", "category": TECHNICAL_SKILL, "aliases": ["javascript", "js"]},
    {"canonical": "TypeScript", "category": TECHNICAL_SKILL, "aliases": ["typescript", "ts"]},
    {"canonical": "Java", "category": TECHNICAL_SKILL, "aliases": ["java"]},
    {"canonical": "C++", "category": TECHNICAL_SKILL, "aliases": ["c++", "cpp"]},
    {"canonical": "C#", "category": TECHNICAL_SKILL, "aliases": ["c#", "csharp"]},
    {"canonical": "HTML", "category": TECHNICAL_SKILL, "aliases": ["html"]},
    {"canonical": "CSS", "category": TECHNICAL_SKILL, "aliases": ["css"]},
    {
        "canonical": "React",
        "category": TECHNICAL_SKILL,
        "aliases": ["react", "react.js", "reactjs"],
    },
    {
        "canonical": "Node.js",
        "category": TECHNICAL_SKILL,
        "aliases": ["node.js", "nodejs", "node"],
    },
    {
        "canonical": "REST API",
        "category": TECHNICAL_SKILL,
        "aliases": ["rest api", "restful", "rest"],
    },
    {"canonical": "GraphQL", "category": TECHNICAL_SKILL, "aliases": ["graphql"]},
    {
        "canonical": "Microservices",
        "category": TECHNICAL_SKILL,
        "aliases": ["microservices", "mikroservis", "mikroservisler"],
    },
    {"canonical": "Pandas", "category": TECHNICAL_SKILL, "aliases": ["pandas"]},
    {"canonical": "NumPy", "category": TECHNICAL_SKILL, "aliases": ["numpy"]},
    {"canonical": "TensorFlow", "category": TECHNICAL_SKILL, "aliases": ["tensorflow"]},
    {"canonical": "PyTorch", "category": TECHNICAL_SKILL, "aliases": ["pytorch"]},
    {
        "canonical": "Unit Testing",
        "category": TECHNICAL_SKILL,
        "aliases": ["unit test", "unit testing", "birim test", "birim testi"],
    },
    {"canonical": "Scrum", "category": TECHNICAL_SKILL, "aliases": ["scrum"]},
    {"canonical": "FastAPI", "category": TOOL, "aliases": ["fastapi"]},
    {"canonical": "Django", "category": TOOL, "aliases": ["django"]},
    {"canonical": "Flask", "category": TOOL, "aliases": ["flask"]},
    {"canonical": "Docker", "category": TOOL, "aliases": ["docker"]},
    {"canonical": "Kubernetes", "category": TOOL, "aliases": ["kubernetes", "k8s"]},
    {"canonical": "Git", "category": TOOL, "aliases": ["git"]},
    {"canonical": "Linux", "category": TOOL, "aliases": ["linux"]},
    {"canonical": "AWS", "category": TOOL, "aliases": ["aws", "amazon web services"]},
    {"canonical": "Azure", "category": TOOL, "aliases": ["azure"]},
    {"canonical": "Google Cloud", "category": TOOL, "aliases": ["gcp", "google cloud"]},
    {"canonical": "PostgreSQL", "category": TOOL, "aliases": ["postgresql", "postgres"]},
    {"canonical": "MySQL", "category": TOOL, "aliases": ["mysql"]},
    {"canonical": "MongoDB", "category": TOOL, "aliases": ["mongodb", "mongo"]},
    {"canonical": "Redis", "category": TOOL, "aliases": ["redis"]},
    {"canonical": "CI/CD", "category": TOOL, "aliases": ["ci/cd", "cicd"]},
    {"canonical": "Jira", "category": TOOL, "aliases": ["jira"]},
    {"canonical": "Figma", "category": TOOL, "aliases": ["figma"]},
    {"canonical": "Excel", "category": TOOL, "aliases": ["excel"]},
    {
        "canonical": "Bash/Shell",
        "category": TOOL,
        "aliases": ["bash", "shell script", "shell scripting"],
    },
    {
        "canonical": "English",
        "category": LANGUAGE,
        "aliases": ["english", "i̇ngilizce", "ingilizce"],
    },
    {"canonical": "German", "category": LANGUAGE, "aliases": ["german", "almanca"]},
    {"canonical": "French", "category": LANGUAGE, "aliases": ["french", "fransızca"]},
    {
        "canonical": "Spanish",
        "category": LANGUAGE,
        "aliases": ["spanish", "i̇spanyolca", "ispanyolca"],
    },
    {
        "canonical": "Communication",
        "category": SOFT_SKILL,
        "aliases": ["communication", "iletişim"],
    },
    {
        "canonical": "Teamwork",
        "category": SOFT_SKILL,
        "aliases": ["teamwork", "takım çalışması", "takim calismasi"],
    },
    {
        "canonical": "Problem Solving",
        "category": SOFT_SKILL,
        "aliases": ["problem solving", "problem çözme"],
    },
    {
        "canonical": "Time Management",
        "category": SOFT_SKILL,
        "aliases": ["time management", "zaman yönetimi"],
    },
    {"canonical": "Leadership", "category": SOFT_SKILL, "aliases": ["leadership", "liderlik"]},
    {"canonical": "Agile", "category": SOFT_SKILL, "aliases": ["agile", "çevik"]},
]
