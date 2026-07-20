"""
Modular prompt templates for the Skill Matching Agent.
"""

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

SKILL_SYSTEM_PROMPT = (
    "You are a Senior Engineering Manager & Technical Skill Architect. "
    "Your role is to analyze engineering tasks and determine the ideal developer role, required technical skills, "
    "experience level (Junior, Mid, Senior, Lead), recommended tools/frameworks, and clear technical reasoning for each assignment."
)

COORDINATOR_SKILL_SYSTEM_PROMPT = (
    "You are an expert Engineering Resource Manager. Your role is to assign engineering tasks "
    "to the actual available team members of the project. You analyze the skills and roles "
    "of each available team member and distribute the tasks appropriately among them."
)

SKILL_ROLE_MATCHING_PROMPT = (
    "Review the following Task Breakdown output:\n\n"
    "--- START TASK BREAKDOWN ---\n{task_breakdown_json}\n--- END TASK BREAKDOWN ---\n\n"
    "For each task, identify the ideal developer role (e.g., Frontend Developer, Backend Developer, DevOps Engineer, QA Engineer, Database Engineer), "
    "required experience level (Junior, Mid, Senior, Lead), required technical skills, recommended tools, and a clear reason for your selection. "
    "Output MUST be a valid JSON object formatted EXACTLY as follows:\n\n"
    "{{\n"
    '  "assignments": [\n'
    '    {{\n'
    '      "task_title": "Build File Parser Utility for PDF/DOCX/TXT",\n'
    '      "developer_role": "Backend Developer",\n'
    '      "experience_level": "Mid",\n'
    '      "skills": ["Python", "FastAPI"],\n'
    '      "recommended_tools": ["PyTest", "Docker"],\n'
    '      "reason": "Requires backend development and writing tests."\n'
    '    }}\n'
    '  ]\n'
    "}}\n\n"
    "Ensure your output contains strictly valid JSON."
)

SKILL_MEMBER_MATCHING_PROMPT = (
    "Review the following Task Breakdown output:\n\n"
    "--- START TASK BREAKDOWN ---\n{task_breakdown_json}\n--- END TASK BREAKDOWN ---\n\n"
    "Here is the list of available team members for this project:\n\n"
    "--- START TEAM MEMBERS ---\n{team_members_json}\n--- END TEAM MEMBERS ---\n\n"
    "Perform a skill and capacity matching analysis. Assign each task to the most appropriate team member from the list. "
    "You MUST match task requirements (like frontend/backend/devops) to the developer's role and skills. "
    "Output MUST be a valid JSON object formatted EXACTLY as follows:\n\n"
    "{{\n"
    '  "assignments": [\n'
    '    {{\n'
    '      "task_id": "TASK-1",\n'
    '      "task_title": "Build File Parser Utility for PDF/DOCX/TXT",\n'
    '      "assigned_member_id": "UUID-OF-MEMBER",\n'
    '      "assigned_member_name": "Name of Member",\n'
    '      "reasoning": "Requires Backend Python skills which matches their profile."\n'
    '    }}\n'
    '  ]\n'
    "}}\n\n"
    "Rules for assignments:\n"
    "1. You MUST assign each task to an actual team member listed in the team members context above. Do NOT invent new developers.\n"
    "2. 'assigned_member_id' MUST match their exact 'id' from the team members list.\n"
    "3. 'assigned_member_name' MUST match their exact 'name' from the team members list.\n"
    "4. Distribute the workload reasonably across all team members based on their roles and skills. Do not assign all tasks to one person.\n"
    "Ensure your output contains strictly valid JSON."
)

# For backward compatibility
SKILL_MATCHING_PROMPT = SKILL_MEMBER_MATCHING_PROMPT

def get_skill_prompt_template() -> ChatPromptTemplate:
    """Returns a compiled LangChain ChatPromptTemplate for Skill Matching."""
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SKILL_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(SKILL_ROLE_MATCHING_PROMPT),
    ])
